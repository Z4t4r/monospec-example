"""Run manifest / dirty-tree provenance helpers (host-evidence dialect)."""

from __future__ import annotations

import hashlib
import json
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

FEV_VERSION = "1.2.0"
VERDICTS = frozenset(
    {
        "FEASIBLE",
        "NOT_FEASIBLE",
        "PARTIALLY_FEASIBLE",
        "BLOCKED",
        "INCONCLUSIVE",
    }
)


@dataclass
class RunManifest:
    root_fev: str
    sub_fev: str
    run_id: str
    agent: str
    fev_version: str = FEV_VERSION
    git_revision: str = "UNKNOWN"
    dirty_tree_snapshot: str = ""
    environment: dict[str, Any] = field(default_factory=dict)
    input_fingerprint: str = ""
    resource_leases: list[str] = field(default_factory=list)
    evidence: list[dict[str, str]] = field(default_factory=list)
    negative_findings: list[Any] = field(default_factory=list)
    local_verdict: str = "INCONCLUSIVE"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: str | Path) -> Path:
        if self.local_verdict not in VERDICTS:
            raise ValueError(f"invalid local_verdict: {self.local_verdict}")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return p

    @classmethod
    def load(cls, path: str | Path) -> RunManifest:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls(
            root_fev=str(data["root_fev"]),
            sub_fev=str(data["sub_fev"]),
            run_id=str(data["run_id"]),
            agent=str(data["agent"]),
            fev_version=str(data.get("fev_version", FEV_VERSION)),
            git_revision=str(data.get("git_revision", "UNKNOWN")),
            dirty_tree_snapshot=str(data.get("dirty_tree_snapshot", "")),
            environment=dict(data.get("environment") or {}),
            input_fingerprint=str(data.get("input_fingerprint", "")),
            resource_leases=list(data.get("resource_leases") or []),
            evidence=list(data.get("evidence") or []),
            negative_findings=list(data.get("negative_findings") or []),
            local_verdict=str(data.get("local_verdict", "INCONCLUSIVE")),
        )


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def fingerprint_paths(paths: Iterable[str | Path]) -> str:
    items: list[str] = []
    for path in paths:
        p = Path(path)
        if p.is_file():
            items.append(f"{p.as_posix()}:{sha256_file(p)}")
        elif p.exists():
            items.append(f"{p.as_posix()}:DIR")
        else:
            items.append(f"{p.as_posix()}:MISSING")
    return sha256_text("\n".join(sorted(items)))


def git_revision(repo_root: str | Path | None = None) -> str:
    cwd = str(repo_root) if repo_root else None
    try:
        out = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        return out.strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def dirty_tree_snapshot(
    repo_root: str | Path,
    *,
    relevant_paths: Sequence[str] | None = None,
) -> str:
    """Hash of relevant uncommitted inputs (path + content or status)."""
    root = Path(repo_root)
    payload: MutableMapping[str, str] = {}
    try:
        status = subprocess.check_output(
            ["git", "status", "--porcelain"],
            cwd=str(root),
            stderr=subprocess.DEVNULL,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        status = ""
    for line in status.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if relevant_paths is not None:
            if not any(
                path == rel or path.startswith(rel.rstrip("/") + "/")
                for rel in relevant_paths
            ):
                continue
        full = root / path
        if full.is_file():
            payload[path] = sha256_file(full)
        else:
            payload[path] = line[:2]
    if relevant_paths:
        for rel in relevant_paths:
            full = root / rel
            if full.is_file() and rel not in payload:
                # Track clean tracked inputs too when explicitly relevant.
                payload[f"clean:{rel}"] = sha256_file(full)
    return sha256_text(json.dumps(payload, sort_keys=True, ensure_ascii=False))


def evidence_entries(
    run_dir: str | Path,
    relative_paths: Sequence[str],
) -> list[dict[str, str]]:
    base = Path(run_dir)
    out: list[dict[str, str]] = []
    for rel in relative_paths:
        path = base / rel
        if not path.is_file():
            raise FileNotFoundError(f"evidence missing: {path}")
        out.append({"path": rel.replace("\\", "/"), "sha256": sha256_file(path)})
    return out


def build_run_manifest(
    *,
    root_fev: str,
    sub_fev: str,
    run_id: str,
    agent: str,
    repo_root: str | Path,
    run_dir: str | Path,
    evidence_relpaths: Sequence[str],
    local_verdict: str,
    resource_leases: Sequence[str] | None = None,
    input_paths: Sequence[str | Path] | None = None,
    relevant_dirty_paths: Sequence[str] | None = None,
    environment: Mapping[str, Any] | None = None,
    negative_findings: Sequence[Any] | None = None,
) -> RunManifest:
    env = {
        "os": platform.system(),
        "platform": platform.platform(),
        "python": platform.python_version(),
    }
    if environment:
        env.update(dict(environment))
    return RunManifest(
        root_fev=root_fev,
        sub_fev=sub_fev,
        run_id=run_id,
        agent=agent,
        fev_version=FEV_VERSION,
        git_revision=git_revision(repo_root),
        dirty_tree_snapshot=dirty_tree_snapshot(
            repo_root, relevant_paths=relevant_dirty_paths
        ),
        environment=env,
        input_fingerprint=fingerprint_paths(input_paths or []),
        resource_leases=list(resource_leases or []),
        evidence=evidence_entries(run_dir, evidence_relpaths),
        negative_findings=list(negative_findings or []),
        local_verdict=local_verdict,
    )


def verify_manifest_integrity(manifest: RunManifest, run_dir: str | Path) -> list[str]:
    """Return list of integrity problems (empty => ok)."""
    problems: list[str] = []
    base = Path(run_dir)
    if manifest.local_verdict not in VERDICTS:
        problems.append(f"invalid verdict {manifest.local_verdict}")
    if not manifest.run_id:
        problems.append("missing run_id")
    if not manifest.dirty_tree_snapshot:
        problems.append("missing dirty_tree_snapshot")
    for item in manifest.evidence:
        path = base / item["path"]
        if not path.is_file():
            problems.append(f"missing evidence file {item['path']}")
            continue
        digest = sha256_file(path)
        if digest != item.get("sha256"):
            problems.append(f"hash mismatch for {item['path']}")
    return problems
