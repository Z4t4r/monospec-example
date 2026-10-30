"""host-evidence: Run directory, provenance manifest and FEV / ICD summary writers."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, Sequence

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPOSITORY_ROOT / "pipelines" / "_shared"))
from cook_runtime import make_run_dir, write_basic_report_md, write_summary_json  # noqa: E402


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def save_json(path: Path, value: Any) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def repository_state() -> dict:
    """Git revision when available; a template copy without .git records that fact instead."""
    try:
        def git(*args: str) -> str:
            return subprocess.check_output(["git", *args], cwd=REPOSITORY_ROOT, text=True, encoding="utf-8",
                                           stderr=subprocess.DEVNULL)

        return {"git_revision": git("rev-parse", "HEAD").strip(),
                "dirty_tree_snapshot": git("status", "--short").splitlines()}
    except (OSError, subprocess.CalledProcessError):
        return {"git_revision": None, "note": "not a git repository; graph_hashes identify the scripts"}


def new_run(owner_dir: Path) -> Path:
    run = make_run_dir(owner_dir)
    print(f"RUN={run}", flush=True)
    return run


def evidence_hashes(run: Path) -> list:
    return [{"path": p.relative_to(run).as_posix(), "sha256": file_sha256(p)}
            for p in sorted((run / "evidence").rglob("*")) if p.is_file()]


def finalize_run(run: Path, *, graph_id: str, owner_id: str, graph_dir: Path, started: datetime, runtime: str,
                 checks: Sequence[Mapping[str, Any]], manifest: dict, fev: Mapping[str, Any] | None = None,
                 icd: Mapping[str, Any] | None = None, notes: Sequence[str] = (),
                 extra_sections: Sequence[str] = ()) -> str:
    """Write manifest.json, summary.json and report.md; return the summary result."""
    ended = datetime.now()
    scripts = sorted(p for p in graph_dir.rglob("*.py") if "runs" not in p.parts and "__pycache__" not in p.parts)
    tracked = [graph_dir / "config.yaml", graph_dir / "contract.yaml", *scripts]
    manifest.update({
        "graph_id": graph_id, "owner": owner_id, "run_id": run.name, **repository_state(),
        "host": {"python": platform.python_version(), "platform": platform.platform()},
        "graph_hashes": {p.relative_to(graph_dir).as_posix(): file_sha256(p) for p in tracked if p.is_file()},
        "evidence": evidence_hashes(run), "canonical_result": "summary.json",
    })
    if fev is not None:
        manifest["local_verdict"] = fev["verdict"]
    if icd is not None:
        manifest["acceptance"] = icd
    save_json(run / "manifest.json", manifest)
    failed = [c for c in checks if c.get("status") != "pass"]
    if fev is not None and fev["verdict"] == "BLOCKED":
        result = "blocked"
    else:
        result = "fail" if failed else "pass"
    summary = {
        "experimental": fev is not None, "runtime": runtime, "pipelineId": f"{graph_id}/{owner_id}",
        "runDir": run.relative_to(REPOSITORY_ROOT).as_posix(), "startedAt": started.isoformat(timespec="seconds"),
        "endedAt": ended.isoformat(timespec="seconds"), "durationMs": int((ended - started).total_seconds() * 1000),
        "result": result, "checks": list(checks), "notes": list(notes),
    }
    if fev is not None:
        summary["fev"] = dict(fev)
    if icd is not None:
        summary["icd"] = dict(icd)
    write_summary_json(run, summary)
    write_basic_report_md(run, summary, extra_sections=list(extra_sections))
    return result
