"""Root Aggregate Verdict helpers (host-evidence dialect)."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence

from .provenance import RunManifest, VERDICTS, verify_manifest_integrity


@dataclass
class AggregateResult:
    root_fev: str
    aggregate_verdict: str
    reasons: list[str] = field(default_factory=list)
    local_verdicts: dict[str, str] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: str | Path) -> Path:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(self.to_dict(), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return p


def aggregate_local_verdicts(
    root_fev: str,
    manifests: Sequence[RunManifest],
    *,
    run_dirs: Sequence[str | Path] | None = None,
    require_all_feasible: bool = False,
) -> AggregateResult:
    """Aggregate Local Verdicts without default Local→Root propagation.

    Rules:
    - Integrity / provenance failures => do not emit FEASIBLE.
    - Any BLOCKED among locals => Aggregate BLOCKED (unless stronger FAIL path).
    - Contradictory FEASIBLE vs NOT_FEASIBLE on same claim set => INCONCLUSIVE.
    - Incomplete set / missing evidence => INCONCLUSIVE (not FEASIBLE).
    - require_all_feasible: Aggregate FEASIBLE only if every local is FEASIBLE
      and no problems; otherwise PARTIALLY_FEASIBLE / INCONCLUSIVE / NOT_FEASIBLE.
    """
    if not manifests:
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="INCONCLUSIVE",
            reasons=["no local manifests"],
            problems=["empty_manifest_set"],
        )

    problems: list[str] = []
    locals_map: dict[str, str] = {}
    for idx, manifest in enumerate(manifests):
        if manifest.root_fev != root_fev:
            problems.append(
                f"{manifest.sub_fev}: root_fev mismatch {manifest.root_fev} != {root_fev}"
            )
        if manifest.local_verdict not in VERDICTS:
            problems.append(f"{manifest.sub_fev}: invalid verdict")
        if not manifest.evidence:
            problems.append(f"{manifest.sub_fev}: missing evidence entries")
        if not manifest.dirty_tree_snapshot:
            problems.append(f"{manifest.sub_fev}: missing dirty_tree_snapshot")
        if run_dirs is not None and idx < len(run_dirs):
            problems.extend(
                f"{manifest.sub_fev}: {p}"
                for p in verify_manifest_integrity(manifest, run_dirs[idx])
            )
        locals_map[manifest.sub_fev] = manifest.local_verdict

    # Environment compatibility: engine keys must not conflict when present.
    engines = {
        m.sub_fev: m.environment.get("engine")
        for m in manifests
        if m.environment.get("engine")
    }
    unique_engines = {v for v in engines.values() if v}
    if len(unique_engines) > 1:
        problems.append(f"incompatible engines: {sorted(unique_engines)}")

    verdicts = set(locals_map.values())
    reasons: list[str] = []

    if problems:
        reasons.append("integrity or provenance problems present")
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="INCONCLUSIVE",
            reasons=reasons + problems,
            local_verdicts=locals_map,
            problems=problems,
        )

    if "FEASIBLE" in verdicts and "NOT_FEASIBLE" in verdicts:
        reasons.append("contradictory local FEASIBLE and NOT_FEASIBLE")
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="INCONCLUSIVE",
            reasons=reasons,
            local_verdicts=locals_map,
            problems=["contradictory_locals"],
        )

    if "BLOCKED" in verdicts:
        reasons.append("at least one Sub-FEV BLOCKED")
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="BLOCKED",
            reasons=reasons,
            local_verdicts=locals_map,
        )

    if require_all_feasible:
        if verdicts == {"FEASIBLE"}:
            return AggregateResult(
                root_fev=root_fev,
                aggregate_verdict="FEASIBLE",
                reasons=["all local verdicts FEASIBLE"],
                local_verdicts=locals_map,
            )
        if "NOT_FEASIBLE" in verdicts and "FEASIBLE" not in verdicts:
            return AggregateResult(
                root_fev=root_fev,
                aggregate_verdict="NOT_FEASIBLE",
                reasons=["local NOT_FEASIBLE under require_all_feasible"],
                local_verdicts=locals_map,
            )
        if "FEASIBLE" in verdicts:
            return AggregateResult(
                root_fev=root_fev,
                aggregate_verdict="PARTIALLY_FEASIBLE",
                reasons=["mixed local progress under require_all_feasible"],
                local_verdicts=locals_map,
            )
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="INCONCLUSIVE",
            reasons=["no conclusive local FEASIBLE set"],
            local_verdicts=locals_map,
        )

    # Conservative default: never invent Root FEASIBLE from partial locals.
    if verdicts == {"FEASIBLE"}:
        reasons.append(
            "all locals FEASIBLE; Root still requires explicit require_all_feasible "
            "or human Aggregate confirmation for FEASIBLE"
        )
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="PARTIALLY_FEASIBLE",
            reasons=reasons,
            local_verdicts=locals_map,
        )

    if verdicts == {"NOT_FEASIBLE"}:
        reasons.append(
            "all locals NOT_FEASIBLE; does not auto-imply Root NOT_FEASIBLE "
            "unless Parent Question logically depends on them"
        )
        return AggregateResult(
            root_fev=root_fev,
            aggregate_verdict="INCONCLUSIVE",
            reasons=reasons,
            local_verdicts=locals_map,
        )

    return AggregateResult(
        root_fev=root_fev,
        aggregate_verdict="INCONCLUSIVE",
        reasons=["incomplete or non-decisive local set"],
        local_verdicts=locals_map,
    )
