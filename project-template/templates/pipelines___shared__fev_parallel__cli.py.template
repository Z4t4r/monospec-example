"""CLI for FEV parallel coordinator (host-evidence dialect)."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
import unittest
from pathlib import Path

from .coordinator import Coordinator, LeaseError
from .editor_worker import EditorWorker, live_test_procedure
from .ownership import OwnershipGuard


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fev_parallel", description="FEV 1.2.0 parallel coordinator")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_test = sub.add_parser("self-test", help="Run automated acceptance gates P0–P8")
    p_test.add_argument("--verbose", action="store_true")

    p_live = sub.add_parser(
        "live-contention",
        help="Attempt live Editor contention (P9); exits non-zero if MCP unavailable",
    )
    p_live.add_argument("--state-dir", required=True)
    p_live.add_argument("--blender-resource", default="blender_editor:default")
    p_live.add_argument("--ue-resource", default="ue58_editor:default")
    p_live.add_argument("--report", required=True)

    p_proc = sub.add_parser("live-procedure", help="Print reproducible P9 live-test procedure")

    p_own = sub.add_parser("check-ownership", help="Check changed paths against write scopes")
    p_own.add_argument("--scopes", required=True, help="JSON file of write scopes")
    p_own.add_argument("--agent", required=True)
    p_own.add_argument("--changed", required=True, help="Newline-separated changed paths file")

    args = parser.parse_args(argv)

    if args.cmd == "self-test":
        return _run_self_test(verbose=args.verbose)
    if args.cmd == "live-procedure":
        print(live_test_procedure())
        return 0
    if args.cmd == "live-contention":
        return _run_live_contention(args)
    if args.cmd == "check-ownership":
        return _check_ownership(args)
    parser.error(f"unknown command {args.cmd}")
    return 2


def _run_self_test(*, verbose: bool) -> int:
    # Import here so `python -m` path works without installing packages.
    from .tests import test_gates

    loader = unittest.defaultTestLoader
    suite = loader.loadTestsFromModule(test_gates)
    runner = unittest.TextTestRunner(verbosity=2 if verbose else 1)
    result = runner.run(suite)
    return 0 if result.wasSuccessful() else 1


def _check_ownership(args: argparse.Namespace) -> int:
    scopes_data = json.loads(Path(args.scopes).read_text(encoding="utf-8"))
    guard = OwnershipGuard.from_mapping(scopes_data)
    changed = [
        line.strip()
        for line in Path(args.changed).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    try:
        guard.refuse_integration(args.agent, changed)
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print("ownership ok")
    return 0


def _run_live_contention(args: argparse.Namespace) -> int:
    """P9 attempt: without live MCP adapters, report BLOCKED with procedure."""
    state_dir = Path(args.state_dir)
    state_dir.mkdir(parents=True, exist_ok=True)
    report_path = Path(args.report)
    report: dict[str, object] = {
        "gate": "P9",
        "status": "BLOCKED",
        "reason": "live MCP adapters not bound in this host process",
        "blender_resource": args.blender_resource,
        "ue_resource": args.ue_resource,
        "procedure": live_test_procedure(),
        "mock_independence_check": None,
    }
    # Still demonstrate independent resource progress with mock executor.
    try:
        db = state_dir / "coordinator.sqlite"
        with Coordinator(db) as coord:
            coord.ensure_resources([args.blender_resource, args.ue_resource])
            worker = EditorWorker(coord)
            b = coord.acquire(
                args.blender_resource,
                owner_agent="cursor",
                root_fev="FEV-LIVE",
                sub_fev="blender",
                run_id="live-b",
                ttl_seconds=30,
            )
            u = coord.acquire(
                args.ue_resource,
                owner_agent="codex",
                root_fev="FEV-LIVE",
                sub_fev="ue",
                run_id="live-u",
                ttl_seconds=30,
            )
            rb = worker.run_tool(b, "ping", {"source": "blender"})
            ru = worker.run_tool(u, "ping", {"source": "ue"})
            coord.release(b)
            coord.release(u)
            report["mock_independence_check"] = {
                "blender_ok": rb.ok,
                "ue_ok": ru.ok,
                "note": "mock only; not live Editor proof",
            }
    except LeaseError as exc:
        report["status"] = "BLOCKED"
        report["reason"] = f"coordinator failure before live bind: {exc}"
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["reason"] = f"unexpected: {exc}"
        report["traceback"] = traceback.format_exc()

    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    # Non-zero: live gate not PASS.
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
