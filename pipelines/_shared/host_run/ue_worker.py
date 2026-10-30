"""host-evidence: isolated AIAGENT UE5.8 Worker launcher (empty Worker project, -NullRHI, Editor Python entry).

Follows traits/aiagent-windows-session-isolation-trait.md: the Worker project is created per Run and owned by
AIAGENT (worker.json marker), a fev_parallel lease guards it, and windows_worker.run_owned verifies the process
owner and rejects visible windows on the Human desktop. The Human project and other Workers are never opened.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Mapping

from .local_env import LocalEnvironment
from .provenance import REPOSITORY_ROOT, save_json

sys.path.insert(0, str(REPOSITORY_ROOT / "pipelines" / "_shared"))
from fev_parallel import Coordinator  # noqa: E402

REQUEST_VARIABLE = "MONOSPEC_WORKER_REQUEST"
ENGINE_PLUGINS = ("PythonScriptPlugin", "EditorScriptingUtilities")


def engine_version(engine: Path) -> dict:
    return json.loads((engine / "Engine/Build/Build.version").read_text(encoding="utf-8"))


def prepare_worker(root: Path, *, purpose: str, graph_id: str) -> Path:
    if root.exists():
        raise RuntimeError("Worker root already exists; every Run uses a new Worker project: " + str(root))
    root.mkdir(parents=True)
    project = root / "ExampleWorker.uproject"
    save_json(project, {"FileVersion": 3, "EngineAssociation": "5.8",
                        "Plugins": [{"Name": name, "Enabled": True} for name in ENGINE_PLUGINS]})
    (root / "Content").mkdir()
    save_json(root / "worker.json", {"owner": "AIAGENT", "purpose": purpose, "graph": graph_id})
    return project


def launch(*, env: LocalEnvironment, run: Path, graph_id: str, owner_id: str, entry: Path, request: Mapping,
           checks: list, manifest: dict, inputs: Mapping[str, Path] | None = None,
           timeout: int = 900) -> str | None:
    """Run one Editor Python entry in a fresh AIAGENT Worker. Return a blocked reason or None.

    ``inputs`` maps request keys to host files; each file is copied into ``<worker>/Input`` (readable by AIAGENT)
    and the request value becomes the copied path. The entry writes into ``request['output']``; that folder is
    copied to ``run/evidence/worker``.
    """
    inputs = inputs or {}
    import yaml

    evidence = run / "evidence"
    worker_base = env.path("worker_root")
    root = (worker_base / graph_id / f"{owner_id.replace('/', '-')}-{run.name.replace('-', '')}").resolve()
    output = root / "Saved" / "MonoSpecEvidence"
    manifest.setdefault("configuration", {}).update({"worker_root": str(root), "timeout": timeout,
                                                     "local_environment": env.describe()})
    try:
        engine = env.path("ue_engine_root")
        credentials = env.path("aiagent_credentials")
        profile = env.path("aiagent_profile")
        if engine is None or credentials is None or profile is None or worker_base is None:
            raise FileNotFoundError("ue_engine_root / aiagent_credentials / aiagent_profile / worker_root not configured")
        build = engine_version(engine)
        manifest.setdefault("environment", {})["engine"] = build
        version_ok = (build["MajorVersion"], build["MinorVersion"]) == (5, 8)
        checks.append({"id": "P0-ue-version", "status": "pass" if version_ok else "fail",
                       "reason": f"{build['MajorVersion']}.{build['MinorVersion']}.{build['PatchVersion']} CL{build['Changelist']}"})
        if not version_ok:
            raise ValueError("environment_mismatch: UE5.8 required")
        credential = yaml.safe_load(credentials.read_text(encoding="utf-8"))["windows_user"]
        if credential["username"].casefold() != "aiagent":
            raise ValueError("AIAGENT credential required")
        if not profile.is_dir():
            raise FileNotFoundError("AIAGENT Windows profile unavailable")
        from .windows_worker import run_owned  # noqa: PLC0415 - Windows-only ctypes module

        project = prepare_worker(root, purpose=owner_id, graph_id=graph_id)
        output.mkdir(parents=True)
        shutil.copy2(entry, root / "entry.py")
        copied = {}
        for key, source in inputs.items():
            target = root / "Input" / Path(source).name
            target.parent.mkdir(exist_ok=True)
            shutil.copy2(source, target)
            copied[key] = str(target)
        save_json(root / "request.json", {**request, **copied, "output": str(output)})
        temp = root / "Temp"
        temp.mkdir()
        subprocess.run(["icacls.exe", str(root), "/grant", "AIAGENT:(OI)(CI)M", "/Q"], capture_output=True,
                       check=True, creationflags=subprocess.CREATE_NO_WINDOW)
        environment = {k: os.environ[k] for k in ("SystemRoot", "WINDIR", "COMSPEC")}
        environment.update(PATH=os.environ["SystemRoot"] + "\\System32", USERNAME="AIAGENT",
                           USERPROFILE=str(profile), APPDATA=str(profile / "AppData/Roaming"),
                           LOCALAPPDATA=str(profile / "AppData/Local"), TEMP=str(temp), TMP=str(temp),
                           **{REQUEST_VARIABLE: str(root / "request.json")})
        state = root.parent / ".leases"
        state.mkdir(exist_ok=True)
        with Coordinator(state / "coordinator.sqlite3") as coordinator:
            resource = "ue58_editor:" + str(root).casefold()
            coordinator.register_resource(resource)
            lease = coordinator.acquire(resource, owner_agent="monospec-example-agent", root_fev=graph_id,
                                        sub_fev=owner_id, run_id=run.name, ttl_seconds=90, wait_seconds=0)
            checks.append({"id": "P0-worker-lease", "status": "pass", "reason": f"lease={lease.lease_id}"})

            def guard() -> None:
                nonlocal lease
                coordinator.validate_fencing(lease)
                if time.time() - lease.heartbeat_at > 15:
                    lease = coordinator.heartbeat(lease)

            healthy = False
            try:
                command = [str(engine / "Engine/Binaries/Win64/UnrealEditor.exe"), str(project), "-unattended",
                           "-NullRHI", "-NoSplash", "-NoSound", "-NoSourceControl", "-NoEpicPortal",
                           f"-ExecutePythonScript={root / 'entry.py'}", f"-abslog={output / 'UnrealEditor.log'}"]
                manifest["configuration"]["command"] = command
                record = run_owned(command, root=root, credential=credential, environment=environment,
                                   record_path=evidence / "worker_process.json", guard=guard, timeout=timeout)
                healthy = record["exit_code"] == 0
                checks.append({"id": "P0-worker-exit", "status": "pass" if healthy else "fail",
                               "reason": f"exit_code={record['exit_code']} owner={record['identity']['owner']} "
                                         f"visible_window_guard={record.get('visible_window_guard_pass')}"})
            finally:
                manifest.setdefault("resource_leases", []).append(lease.to_dict())
                coordinator.release(lease, mark_healthy=healthy)
    except (OSError, ValueError, RuntimeError, KeyError, TimeoutError, subprocess.SubprocessError) as exc:
        save_json(evidence / "launch-error.json", {"error_type": type(exc).__name__, "error": str(exc)})
        checks.append({"id": "P0-worker-launch", "status": "fail", "reason": f"{type(exc).__name__}: {exc}"})
        return f"{type(exc).__name__}: {exc}"
    finally:
        if output.is_dir():
            shutil.copytree(output, evidence / "worker", dirs_exist_ok=True)
    return None
