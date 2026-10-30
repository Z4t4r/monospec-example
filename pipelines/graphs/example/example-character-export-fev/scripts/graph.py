"""host-transform: experimental paths and contract access for this Graph's Sub-FEV launchers only."""

from __future__ import annotations

import json
import sys
from pathlib import Path

GRAPH = Path(__file__).resolve().parents[1]
REPO = GRAPH.parents[3]
GRAPH_ID = "example-character-export-fev"
ROOT_FEV = "example-char"
sys.path.insert(0, str(REPO / "pipelines" / "_shared"))
sys.path.insert(0, str(GRAPH / "scripts"))


def load_yaml(path: Path) -> dict:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8"))


def config() -> dict:
    cfg = load_yaml(GRAPH / "config.yaml")
    if cfg["graph"]["status"] != "active":
        raise ValueError("Graph is not active")
    return cfg


def contract(sub_fev: str) -> dict:
    return load_yaml(GRAPH / "contract.yaml")["sub_fev"][sub_fev]


def check(checks: list, check_id: str, ok: bool, reason: str, evidence: str | None = None) -> bool:
    row = {"id": check_id, "status": "pass" if ok else "fail", "reason": reason}
    if evidence:
        row["evidence"] = evidence
    checks.append(row)
    return ok


def latest_passing_run(sub_dir: Path) -> Path | None:
    runs = sorted((sub_dir / "runs").glob("*/summary.json"), reverse=True)
    for summary in runs:
        if json.loads(summary.read_text(encoding="utf-8")).get("result") == "pass":
            return summary.parent
    return None
