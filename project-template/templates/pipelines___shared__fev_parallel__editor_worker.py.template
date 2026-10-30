"""Exclusive Editor worker boundary (host-evidence dialect).

All protected Editor / MCP operations for a resource MUST go through this
worker while holding a valid lease + fencing token. Direct raw MCP bypass is
out of policy for FEV 1.2.0 parallel runs.

Live adapters are optional; when MCP endpoints are unavailable, callers must
mark P9 BLOCKED rather than claiming PASS.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping

from .coordinator import Coordinator, Lease, LeaseError


@dataclass
class WorkerResult:
    ok: bool
    resource_id: str
    lease_id: str
    fencing_token: int
    op_id: str
    output: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class EditorWorker:
    """Single owner process facade for one protected editor resource family."""

    def __init__(
        self,
        coordinator: Coordinator,
        *,
        executor: Callable[[str, Mapping[str, Any]], Mapping[str, Any]] | None = None,
    ) -> None:
        self.coordinator = coordinator
        self._executor = executor or _mock_executor
        self._busy: dict[str, str] = {}

    def run_tool(
        self,
        lease: Lease,
        command: str,
        payload: Mapping[str, Any] | None = None,
    ) -> WorkerResult:
        return self._run(lease, command, payload or {}, transactional=False)

    def run_transaction(
        self,
        lease: Lease,
        steps: list[tuple[str, Mapping[str, Any]]],
        *,
        restore: Callable[[], None] | None = None,
    ) -> WorkerResult:
        self.coordinator.validate_fencing(lease)
        if lease.resource_id in self._busy:
            raise LeaseError(
                f"resource {lease.resource_id} already in transaction "
                f"{self._busy[lease.resource_id]}"
            )
        op_id = self.coordinator.begin_op(
            lease, {"mode": "transaction", "steps": [s[0] for s in steps]}
        )
        self._busy[lease.resource_id] = op_id
        outputs: list[dict[str, Any]] = []
        try:
            for command, payload in steps:
                self.coordinator.validate_fencing(lease)
                active = self.coordinator.active_ops(lease.resource_id)
                foreign = [a for a in active if a["op_id"] != op_id]
                if foreign:
                    raise LeaseError(
                        f"foreign mutation during transaction: {foreign[0]['op_id']}"
                    )
                outputs.append(dict(self._executor(command, payload)))
            self.coordinator.finish_op(op_id, status="DONE")
            return WorkerResult(
                ok=True,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id=op_id,
                output={"steps": outputs},
            )
        except Exception as exc:
            self.coordinator.finish_op(op_id, status="FAILED")
            self.coordinator.mark_dirty(lease.resource_id, f"transaction failed: {exc}")
            return WorkerResult(
                ok=False,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id=op_id,
                error=str(exc),
            )
        finally:
            self._busy.pop(lease.resource_id, None)
            if restore is not None:
                restore()

    def _run(
        self,
        lease: Lease,
        command: str,
        payload: Mapping[str, Any],
        *,
        transactional: bool,
    ) -> WorkerResult:
        del transactional  # reserved for future tool-vs-tx distinction
        try:
            self.coordinator.validate_fencing(lease)
        except LeaseError as exc:
            return WorkerResult(
                ok=False,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id="",
                error=str(exc),
            )
        if lease.resource_id in self._busy:
            return WorkerResult(
                ok=False,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id=self._busy[lease.resource_id],
                error="resource busy in another transaction",
            )
        op_id = self.coordinator.begin_op(lease, {"command": command, **dict(payload)})
        try:
            output = dict(self._executor(command, payload))
            self.coordinator.finish_op(op_id, status="DONE")
            return WorkerResult(
                ok=True,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id=op_id,
                output=output,
            )
        except Exception as exc:
            self.coordinator.finish_op(op_id, status="FAILED")
            return WorkerResult(
                ok=False,
                resource_id=lease.resource_id,
                lease_id=lease.lease_id,
                fencing_token=lease.fencing_token,
                op_id=op_id,
                error=str(exc),
            )


def _mock_executor(command: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
    # Deterministic mock for contention tests; not live Editor proof.
    delay = float(payload.get("delay_seconds", 0.0))
    if delay:
        time.sleep(delay)
    if payload.get("force_fail"):
        raise RuntimeError("forced executor failure")
    return {"command": command, "echo": dict(payload), "ts": time.time()}


def live_test_procedure() -> str:
    """Reproducible P9 procedure when UE5.8 / Blender MCP are available."""
    return """
# FEV 1.2.0 P9 Live Editor validation

Prerequisites:
- Blender MCP connected (user-blender get_addon_status succeeds)
- UE5.8 MCP Worker connected under AIAGENT session isolation
- No Human Desktop Editor interference

Commands (from repo root; PYTHONPATH includes pipelines/_shared):

  set PYTHONPATH=pipelines\\_shared
  python -m fev_parallel live-contention ^
    --state-dir %TEMP%\\fev_parallel_live ^
    --blender-resource blender_editor:default ^
    --ue-resource ue58_editor:default ^
    --report %TEMP%\\fev_parallel_live\\p9_report.json

Expected PASS evidence:
- Concurrent acquire on blender_editor and ue58_editor both succeed
- Two workers contending for the same editor serialize (one waits)
- Kill / timeout mid-transaction => resource DIRTY, fencing advances, reuse only after recovery
- Evidence manifests include lease_ids and hashes

If either MCP endpoint is down, record gate P9 = BLOCKED and keep this procedure.
""".strip()
