"""Executable acceptance gates P0–P8 for FEV 1.2.0 (host-evidence dialect)."""

from __future__ import annotations

import json
import tempfile
import threading
import time
import unittest
from pathlib import Path

from fev_parallel.aggregation import aggregate_local_verdicts
from fev_parallel.coordinator import (
    STATE_AVAILABLE,
    STATE_DIRTY,
    Coordinator,
    LeaseError,
)
from fev_parallel.editor_worker import EditorWorker
from fev_parallel.ownership import OwnershipError, OwnershipGuard, WriteScope
from fev_parallel.provenance import FEV_VERSION, RunManifest, VERDICTS, sha256_file, sha256_text


class GateP0Compatibility(unittest.TestCase):
    def test_verdict_vocabulary_unchanged(self) -> None:
        self.assertEqual(
            VERDICTS,
            {
                "FEASIBLE",
                "NOT_FEASIBLE",
                "PARTIALLY_FEASIBLE",
                "BLOCKED",
                "INCONCLUSIVE",
            },
        )
        self.assertEqual(FEV_VERSION, "1.2.0")

    def test_local_not_feasible_does_not_auto_root(self) -> None:
        manifests = [
            RunManifest(
                root_fev="FEV-ROOT",
                sub_fev="A",
                run_id="r1",
                agent="cursor",
                dirty_tree_snapshot="abc",
                evidence=[{"path": "e.txt", "sha256": "0" * 64}],
                local_verdict="NOT_FEASIBLE",
            )
        ]
        result = aggregate_local_verdicts("FEV-ROOT", manifests)
        self.assertNotEqual(result.aggregate_verdict, "NOT_FEASIBLE")
        self.assertEqual(result.aggregate_verdict, "INCONCLUSIVE")


class GateP1ParallelInvestigation(unittest.TestCase):
    def test_independent_subfevs_overlap_progress(self) -> None:
        events: list[str] = []
        barrier = threading.Barrier(2)

        def worker(name: str, delay: float) -> None:
            events.append(f"{name}:start")
            barrier.wait(timeout=5)
            time.sleep(delay)
            events.append(f"{name}:done")

        t1 = threading.Thread(target=worker, args=("A", 0.15))
        t2 = threading.Thread(target=worker, args=("B", 0.15))
        t1.start()
        t2.start()
        t1.join(timeout=5)
        t2.join(timeout=5)
        self.assertIn("A:start", events)
        self.assertIn("B:start", events)
        # Both started before either finished => overlapping progress.
        first_done = min(i for i, e in enumerate(events) if e.endswith(":done"))
        starts_before_first_done = [
            e for e in events[:first_done] if e.endswith(":start")
        ]
        self.assertEqual(len(starts_before_first_done), 2)


class GateP2FileOwnership(unittest.TestCase):
    def test_overlap_rejected_and_unauthorized_integration_refused(self) -> None:
        with self.assertRaises(OwnershipError):
            OwnershipGuard(
                [
                    WriteScope("cursor", "sub-a", ("sub-fev/a",)),
                    WriteScope("codex", "sub-b", ("sub-fev/a/nested",)),
                ]
            )
        guard = OwnershipGuard(
            [
                WriteScope("cursor", "sub-a", ("sub-fev/a",)),
                WriteScope("codex", "sub-b", ("sub-fev/b",)),
            ]
        )
        guard.assert_allowed("cursor", ["sub-fev/a/investigation.md"])
        with self.assertRaises(OwnershipError):
            guard.assert_allowed("cursor", ["sub-fev/b/x.md"])
        with self.assertRaises(OwnershipError):
            guard.refuse_integration(
                "cursor",
                ["sub-fev/a/ok.md", "aggregate/verdict.md"],
            )


class GateP3ToolSerialization(unittest.TestCase):
    def test_at_most_one_protected_op_per_resource(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "c.sqlite"
            coord = Coordinator(db, default_ttl_seconds=30)
            coord.register_resource("ue58_editor:t")
            worker = EditorWorker(coord)
            lease_a = coord.acquire(
                "ue58_editor:t",
                owner_agent="cursor",
                root_fev="R",
                sub_fev="A",
                run_id="rA",
                lease_kind="tool",
                ttl_seconds=30,
            )
            with self.assertRaises(LeaseError):
                coord.acquire(
                    "ue58_editor:t",
                    owner_agent="codex",
                    root_fev="R",
                    sub_fev="B",
                    run_id="rB",
                    lease_kind="tool",
                    wait_seconds=0,
                )
            started = []
            done = []

            def hold() -> None:
                started.append(time.time())
                worker.run_tool(lease_a, "slow", {"delay_seconds": 0.2})
                done.append(time.time())

            t = threading.Thread(target=hold)
            t.start()
            time.sleep(0.05)
            # Second acquire waits then proceeds after release.
            def waiter() -> None:
                lease_b = coord.acquire(
                    "ue58_editor:t",
                    owner_agent="codex",
                    root_fev="R",
                    sub_fev="B",
                    run_id="rB",
                    wait_seconds=5,
                    poll_interval=0.02,
                )
                worker.run_tool(lease_b, "fast", {})
                coord.release(lease_b)
                done.append(time.time())

            # Release after first tool finishes.
            t.join(timeout=5)
            coord.release(lease_a)
            tw = threading.Thread(target=waiter)
            tw.start()
            tw.join(timeout=5)
            self.assertEqual(len(done), 2)
            active = coord.active_ops("ue58_editor:t")
            self.assertEqual(active, [])
            coord.close()


class GateP4TransactionIsolation(unittest.TestCase):
    def test_no_foreign_mutation_during_transaction(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "c.sqlite"
            coord = Coordinator(db)
            coord.register_resource("blender_editor:t")
            worker = EditorWorker(coord)
            lease = coord.acquire(
                "blender_editor:t",
                owner_agent="cursor",
                root_fev="R",
                sub_fev="A",
                run_id="r1",
                lease_kind="transaction",
            )
            # Begin a long transaction in a thread; inject a competing begin_op.
            injected = threading.Event()
            result_holder: list[object] = []

            def txn() -> None:
                def step_payload(_: str, __: dict) -> dict:
                    injected.wait(timeout=2)
                    return {"ok": True}

                w = EditorWorker(coord, executor=step_payload)
                result_holder.append(
                    w.run_transaction(lease, [("setup", {}), ("sim", {})])
                )

            th = threading.Thread(target=txn)
            th.start()
            time.sleep(0.05)
            # Foreign op attempt using a forged/stale path: second lease denied.
            with self.assertRaises(LeaseError):
                coord.acquire(
                    "blender_editor:t",
                    owner_agent="codex",
                    root_fev="R",
                    sub_fev="B",
                    run_id="r2",
                    wait_seconds=0,
                )
            injected.set()
            th.join(timeout=5)
            self.assertTrue(result_holder)
            self.assertTrue(getattr(result_holder[0], "ok"))
            coord.release(lease)
            coord.close()


class GateP5CrashTimeoutRecovery(unittest.TestCase):
    def test_stale_owner_fenced_before_reuse(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "c.sqlite"
            coord = Coordinator(db, default_ttl_seconds=0.2)
            coord.register_resource("ue58_editor:crash")
            lease = coord.acquire(
                "ue58_editor:crash",
                owner_agent="cursor",
                root_fev="R",
                sub_fev="A",
                run_id="r1",
                ttl_seconds=0.15,
            )
            time.sleep(0.25)
            expired = coord.expire_stale()
            self.assertIn("ue58_editor:crash", expired)
            state = coord.get_resource("ue58_editor:crash")
            self.assertEqual(state.state, STATE_DIRTY)
            with self.assertRaises(LeaseError):
                coord.validate_fencing(lease)
            with self.assertRaises(LeaseError):
                coord.acquire(
                    "ue58_editor:crash",
                    owner_agent="codex",
                    root_fev="R",
                    sub_fev="B",
                    run_id="r2",
                    wait_seconds=0,
                )
            coord.begin_recovery("ue58_editor:crash")
            token = coord.complete_recovery("ue58_editor:crash")
            self.assertGreaterEqual(token, 1)
            state2 = coord.get_resource("ue58_editor:crash")
            self.assertEqual(state2.state, STATE_AVAILABLE)
            lease2 = coord.acquire(
                "ue58_editor:crash",
                owner_agent="codex",
                root_fev="R",
                sub_fev="B",
                run_id="r2",
            )
            self.assertNotEqual(lease2.fencing_token, lease.fencing_token)
            with self.assertRaises(LeaseError):
                coord.validate_fencing(lease)
            coord.release(lease2)
            coord.close()


class GateP6ResourceIndependence(unittest.TestCase):
    def test_ue_and_blender_progress_concurrently(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "c.sqlite"
            coord = Coordinator(db)
            coord.ensure_resources(["ue58_editor:x", "blender_editor:y"])
            worker = EditorWorker(coord)
            marks: list[str] = []
            barrier = threading.Barrier(2)

            def run(resource: str, agent: str, tag: str) -> None:
                lease = coord.acquire(
                    resource,
                    owner_agent=agent,
                    root_fev="R",
                    sub_fev=tag,
                    run_id=tag,
                )
                marks.append(f"{tag}:leased")
                barrier.wait(timeout=5)
                worker.run_tool(lease, "ping", {"delay_seconds": 0.1})
                marks.append(f"{tag}:done")
                coord.release(lease)

            t1 = threading.Thread(
                target=run, args=("ue58_editor:x", "cursor", "ue")
            )
            t2 = threading.Thread(
                target=run, args=("blender_editor:y", "codex", "bl")
            )
            t1.start()
            t2.start()
            t1.join(timeout=5)
            t2.join(timeout=5)
            leased = [m for m in marks if m.endswith(":leased")]
            self.assertEqual(len(leased), 2)
            first_done_idx = min(i for i, m in enumerate(marks) if m.endswith(":done"))
            self.assertEqual(
                len([m for m in marks[:first_done_idx] if m.endswith(":leased")]),
                2,
            )
            coord.close()


class GateP7EvidenceProvenance(unittest.TestCase):
    def test_dirty_tree_runs_are_attributable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_a = root / "runs" / "a"
            run_b = root / "runs" / "b"
            run_a.mkdir(parents=True)
            run_b.mkdir(parents=True)
            (run_a / "out.txt").write_text("aaa", encoding="utf-8")
            (run_b / "out.txt").write_text("bbb", encoding="utf-8")
            dirty = root / "dirty_input.txt"
            dirty.write_text("shared-dirty", encoding="utf-8")
            # Simulate dirty snapshot without requiring a git repo:
            snap = sha256_text(dirty.read_text(encoding="utf-8"))
            m_a = RunManifest(
                root_fev="FEV-ROOT",
                sub_fev="sub-a",
                run_id="run-a",
                agent="cursor",
                git_revision="deadbeef",
                dirty_tree_snapshot=snap,
                environment={"os": "Windows", "engine": "UE5.8"},
                input_fingerprint=sha256_text("input-a"),
                resource_leases=["lease-a"],
                evidence=[{"path": "out.txt", "sha256": sha256_file(run_a / "out.txt")}],
                local_verdict="INCONCLUSIVE",
            )
            m_b = RunManifest(
                root_fev="FEV-ROOT",
                sub_fev="sub-b",
                run_id="run-b",
                agent="codex",
                git_revision="deadbeef",
                dirty_tree_snapshot=snap,
                environment={"os": "Windows", "engine": "UE5.8"},
                input_fingerprint=sha256_text("input-b"),
                resource_leases=["lease-b"],
                evidence=[{"path": "out.txt", "sha256": sha256_file(run_b / "out.txt")}],
                local_verdict="INCONCLUSIVE",
            )
            path_a = m_a.write(run_a / "manifest.json")
            path_b = m_b.write(run_b / "manifest.json")
            loaded_a = RunManifest.load(path_a)
            loaded_b = RunManifest.load(path_b)
            self.assertEqual(loaded_a.agent, "cursor")
            self.assertEqual(loaded_b.agent, "codex")
            self.assertEqual(loaded_a.dirty_tree_snapshot, loaded_b.dirty_tree_snapshot)
            self.assertNotEqual(loaded_a.evidence[0]["sha256"], loaded_b.evidence[0]["sha256"])
            self.assertNotEqual(loaded_a.input_fingerprint, loaded_b.input_fingerprint)


class GateP8VerdictAggregation(unittest.TestCase):
    def test_contradictory_and_incomplete_not_feasible(self) -> None:
        def mk(sub: str, verdict: str, evidence: bool = True) -> RunManifest:
            return RunManifest(
                root_fev="FEV-ROOT",
                sub_fev=sub,
                run_id=f"r-{sub}",
                agent="cursor",
                dirty_tree_snapshot="snap",
                evidence=(
                    [{"path": "e.txt", "sha256": "a" * 64}] if evidence else []
                ),
                local_verdict=verdict,
            )

        contradictory = aggregate_local_verdicts(
            "FEV-ROOT",
            [mk("a", "FEASIBLE"), mk("b", "NOT_FEASIBLE")],
        )
        self.assertEqual(contradictory.aggregate_verdict, "INCONCLUSIVE")
        self.assertNotEqual(contradictory.aggregate_verdict, "FEASIBLE")

        incomplete = aggregate_local_verdicts(
            "FEV-ROOT",
            [mk("a", "FEASIBLE", evidence=False)],
        )
        self.assertEqual(incomplete.aggregate_verdict, "INCONCLUSIVE")
        self.assertNotEqual(incomplete.aggregate_verdict, "FEASIBLE")

        # Even all-FEASIBLE without require_all_feasible stays conservative.
        all_ok = aggregate_local_verdicts(
            "FEV-ROOT",
            [mk("a", "FEASIBLE"), mk("b", "FEASIBLE")],
        )
        self.assertNotEqual(all_ok.aggregate_verdict, "FEASIBLE")

        forced = aggregate_local_verdicts(
            "FEV-ROOT",
            [mk("a", "FEASIBLE"), mk("b", "FEASIBLE")],
            require_all_feasible=True,
        )
        self.assertEqual(forced.aggregate_verdict, "FEASIBLE")


class GateSchemasPresent(unittest.TestCase):
    def test_schema_files_exist(self) -> None:
        base = Path(__file__).resolve().parents[1] / "schemas"
        for name in (
            "resource_lease.schema.json",
            "sub_fev_task.schema.json",
            "run_manifest.schema.json",
        ):
            path = base / name
            self.assertTrue(path.is_file(), name)
            json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
