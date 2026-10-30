"""host-evidence: immutable run-bundle helpers for pipelines/graphs."""

from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

L3_FOOTER = "P3 user acceptance is explicitly required by this Graph; Agent MUST NOT mark it pass."

FEV_VERDICTS = {"FEASIBLE", "NOT_FEASIBLE", "PARTIALLY_FEASIBLE", "BLOCKED", "INCONCLUSIVE"}


def _validate_fev(fev: Mapping[str, Any]) -> None:
    required = ("question", "outcome", "observations", "interpretation", "verdict",
                "limitations", "guidance", "evidence", "reproduction")
    missing = [key for key in required if key not in fev]
    if missing:
        raise ValueError("Missing FEV report fields: " + ", ".join(missing))
    if fev["verdict"] not in FEV_VERDICTS:
        raise ValueError("Invalid FEV verdict")
    for key in ("question", "outcome", "interpretation", "reproduction"):
        if not isinstance(fev[key], str) or not fev[key].strip():
            raise ValueError(f"FEV {key} must be nonempty text")
    for key in ("observations", "limitations", "guidance", "evidence"):
        if not isinstance(fev[key], (list, tuple)) or any(
            not isinstance(item, str) or not item.strip() for item in fev[key]
        ):
            raise ValueError(f"FEV {key} must be a sequence of nonempty text")
    if fev["verdict"] in {"FEASIBLE", "NOT_FEASIBLE", "PARTIALLY_FEASIBLE"} and not fev["evidence"]:
        raise ValueError("A conclusive FEV verdict requires evidence references")


def make_run_dir(graph_dir: str | Path, when: datetime | None = None) -> Path:
    """Create pipelines/.../<slug>/runs/<yyyy-MM-ddTHHmmss>/ and return it."""
    stamp = (when or datetime.now()).strftime("%Y-%m-%dT%H%M%S")
    run_dir = Path(graph_dir) / "runs" / stamp
    run_dir.mkdir(parents=True, exist_ok=False)
    (run_dir / "evidence").mkdir(exist_ok=True)
    return run_dir


def write_summary_json(
    run_dir: str | Path,
    summary: Mapping[str, Any],
) -> Path:
    path = Path(run_dir) / "summary.json"
    path.write_text(json.dumps(dict(summary), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def write_basic_report_md(
    run_dir: str | Path,
    summary: Mapping[str, Any],
    extra_sections: Sequence[str] | None = None,
    *,
    human_acceptance: bool = False,
) -> Path:
    fev = summary.get("fev")
    if fev is not None:
        _validate_fev(fev)
        if human_acceptance:
            raise ValueError("FEV reports do not require per-run human acceptance")
    pipeline_id = summary.get("pipelineId", summary.get("graph", "unknown"))
    checks = summary.get("checks") or []
    counts = Counter(str(check.get("status", "unknown")) for check in checks)
    lines: list[str] = [
        f"# Pipeline report — {pipeline_id}",
        "",
        "## Run summary",
        "",
        f"- run: {summary.get('runDir', summary.get('run', Path(run_dir).name))}",
        f"- result: {summary.get('result', 'not reported')}",
        "- checks: " + (", ".join(f"{key}={value}" for key, value in sorted(counts.items())) or "none recorded; no pass inferred"),
        "",
    ]
    if fev is not None:
        lines.extend([f"Question: {fev['question']}", "", f"Verdict: **{fev['verdict']}**", "", fev["outcome"], ""])
        for title, key in (("Observations", "observations"), ("Interpretation", "interpretation"),
                           ("Limitations / Unknowns", "limitations"), ("Implementation guidance", "guidance"),
                           ("Evidence references", "evidence"), ("Reproduction", "reproduction")):
            value = fev[key]
            lines.extend([f"## {title}", ""])
            lines.extend([value] if isinstance(value, str) else [f"- {item}" for item in value] or ["None declared."])
            lines.append("")
    lines.extend([
        "## Execution",
        "",
        f"- runtime: {summary.get('runtime', 'python')}"
        + (" (experimental)" if summary.get("experimental") else ""),
        f"- startedAt: {summary.get('startedAt', '')}",
        f"- endedAt: {summary.get('endedAt', '')}",
        f"- durationMs: {summary.get('durationMs', '')}",
        "",
    ])
    if checks:
        lines.extend(["## Checks", "", "| id | status |", "|----|--------|"])
        for check in checks:
            cell = str(check.get("status", ""))
            if check.get("reason"):
                cell += f" ({check['reason']})"
            if check.get("evidence"):
                cell += f" (evidence: {check['evidence']})"
            lines.append(f"| {check.get('id', '')} | {cell} |")
        lines.append("")
    notes = summary.get("notes") or []
    if notes:
        lines.extend(["## Notes", ""])
        for note in notes:
            lines.append(f"- {note}")
        lines.append("")
    if extra_sections:
        lines.extend(extra_sections)
    if human_acceptance:
        lines.extend(["## Acceptance", "", L3_FOOTER, ""])
    path = Path(run_dir) / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_acceptance_pending(
    run_dir: str | Path,
    template_path: str | Path | None = None,
    slug: str = "{{slug}}",
) -> Path:
    """Copy acceptance template into the run dir with Status pending."""
    run_dir = Path(run_dir)
    dest = run_dir / "acceptance.md"
    if template_path is None:
        # pipelines/_template/acceptance.md relative to this package
        template_path = Path(__file__).resolve().parents[2] / "_template" / "acceptance.md"
    text = Path(template_path).read_text(encoding="utf-8")
    text = text.replace("{{slug}}", slug)
    if "Status:" not in text:
        text = f"# Acceptance — {slug}\n\nStatus: **pending**\n\n" + text
    dest.write_text(text, encoding="utf-8")
    return dest


def ensure_missing_sink(
    run_dir: str | Path,
    relative_sink: str,
    *,
    source: str = "missing",
    count: int = 0,
    extra: MutableMapping[str, Any] | None = None,
) -> Path:
    """Write a required collector file when data is absent (never silent-skip)."""
    path = Path(run_dir) / relative_sink
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {"source": source, "count": count}
    if extra:
        payload.update(extra)
    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    else:
        path.write_text(
            f"source: {source}\ncount: {count}\n",
            encoding="utf-8",
        )
    return path


def write_run_bundle(
    graph_dir: str | Path,
    *,
    pipeline_id: str,
    checks: Sequence[Mapping[str, Any]] | None = None,
    notes: Sequence[str] | None = None,
    experimental: bool = False,
    started_at: str | None = None,
    ended_at: str | None = None,
    duration_ms: int | None = None,
    acceptance_template: str | Path | None = None,
    human_acceptance: bool = False,
    fev: Mapping[str, Any] | None = None,
) -> Path:
    """Write summary/report; acceptance is opt-in via flag or explicit template.

    FEV callers provide question, outcome, observations, interpretation, verdict,
    limitations, guidance, evidence and reproduction. Verdict is supplied, never inferred from checks.
    """
    human_acceptance = human_acceptance or acceptance_template is not None
    if fev is not None:
        _validate_fev(fev)
        if human_acceptance:
            raise ValueError("FEV bundles do not require per-run human acceptance")
    started = started_at or datetime.now().isoformat(timespec="seconds")
    ended = ended_at or datetime.now().isoformat(timespec="seconds")
    run_dir = make_run_dir(graph_dir)
    summary: dict[str, Any] = {
        "experimental": experimental,
        "runtime": "python",
        "pipelineId": pipeline_id,
        "runDir": str(run_dir).replace("\\", "/"),
        "startedAt": started,
        "endedAt": ended,
        "durationMs": duration_ms if duration_ms is not None else 0,
        "checks": list(checks or []),
        "notes": list(notes or []),
    }
    if fev is not None:
        summary["fev"] = dict(fev)
    write_summary_json(run_dir, summary)
    write_basic_report_md(run_dir, summary, human_acceptance=human_acceptance)
    if human_acceptance:
        write_acceptance_pending(run_dir, acceptance_template, slug=pipeline_id)
    return run_dir
