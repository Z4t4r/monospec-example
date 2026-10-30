"""Cross-process resource lease coordinator (host-evidence dialect).

Uses SQLite with BEGIN IMMEDIATE for atomic acquire across processes.
Fencing tokens prevent stale owners from executing after expiry or reclaim.
"""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

LEASE_TOOL = "tool"
LEASE_TRANSACTION = "transaction"
LEASE_EXCLUSIVE = "exclusive"

STATE_AVAILABLE = "AVAILABLE"
STATE_LEASED = "LEASED"
STATE_DIRTY = "DIRTY"
STATE_RECOVERING = "RECOVERING"

_VALID_LEASE_KINDS = frozenset({LEASE_TOOL, LEASE_TRANSACTION, LEASE_EXCLUSIVE})
_SCHEMA = """
CREATE TABLE IF NOT EXISTS resources (
  resource_id TEXT PRIMARY KEY,
  capacity INTEGER NOT NULL DEFAULT 1,
  state TEXT NOT NULL DEFAULT 'AVAILABLE',
  fencing_token INTEGER NOT NULL DEFAULT 0,
  dirty_reason TEXT
);

CREATE TABLE IF NOT EXISTS leases (
  lease_id TEXT PRIMARY KEY,
  resource_id TEXT NOT NULL,
  owner_agent TEXT NOT NULL,
  root_fev TEXT NOT NULL,
  sub_fev TEXT NOT NULL,
  run_id TEXT NOT NULL,
  lease_kind TEXT NOT NULL,
  fencing_token INTEGER NOT NULL,
  acquired_at REAL NOT NULL,
  expires_at REAL NOT NULL,
  heartbeat_at REAL NOT NULL,
  state TEXT NOT NULL,
  FOREIGN KEY(resource_id) REFERENCES resources(resource_id)
);

CREATE TABLE IF NOT EXISTS wait_queue (
  queue_id INTEGER PRIMARY KEY AUTOINCREMENT,
  resource_id TEXT NOT NULL,
  requester TEXT NOT NULL,
  enqueued_at REAL NOT NULL,
  lease_kind TEXT NOT NULL,
  owner_agent TEXT NOT NULL,
  root_fev TEXT NOT NULL,
  sub_fev TEXT NOT NULL,
  run_id TEXT NOT NULL,
  ttl_seconds REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS editor_ops (
  op_id TEXT PRIMARY KEY,
  resource_id TEXT NOT NULL,
  lease_id TEXT NOT NULL,
  fencing_token INTEGER NOT NULL,
  started_at REAL NOT NULL,
  finished_at REAL,
  status TEXT NOT NULL,
  payload TEXT
);
"""


class LeaseError(RuntimeError):
    """Lease acquire / validate / release failure."""


@dataclass(frozen=True)
class Lease:
    lease_id: str
    resource_id: str
    owner_agent: str
    root_fev: str
    sub_fev: str
    run_id: str
    lease_kind: str
    fencing_token: int
    acquired_at: float
    expires_at: float
    heartbeat_at: float
    state: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ResourceState:
    resource_id: str
    capacity: int
    state: str
    fencing_token: int
    dirty_reason: str | None
    active_leases: tuple[Lease, ...]


class Coordinator:
    """Single-host durable lease authority."""

    def __init__(self, state_path: str | Path, *, default_ttl_seconds: float = 120.0) -> None:
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.default_ttl_seconds = float(default_ttl_seconds)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.state_path), timeout=30.0, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA busy_timeout=30000")
        self._conn.executescript(_SCHEMA)
        self._conn.commit()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> Coordinator:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def register_resource(self, resource_id: str, *, capacity: int = 1) -> None:
        if capacity < 1:
            raise ValueError("capacity must be >= 1")
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO resources(resource_id, capacity, state, fencing_token)
                VALUES (?, ?, ?, 0)
                ON CONFLICT(resource_id) DO UPDATE SET capacity=excluded.capacity
                """,
                (resource_id, capacity, STATE_AVAILABLE),
            )
            self._conn.commit()

    def ensure_resources(self, resource_ids: Iterable[str], *, capacity: int = 1) -> None:
        for rid in resource_ids:
            self.register_resource(rid, capacity=capacity)

    def acquire(
        self,
        resource_id: str,
        *,
        owner_agent: str,
        root_fev: str,
        sub_fev: str,
        run_id: str,
        lease_kind: str = LEASE_TRANSACTION,
        ttl_seconds: float | None = None,
        wait_seconds: float = 0.0,
        poll_interval: float = 0.05,
    ) -> Lease:
        if lease_kind not in _VALID_LEASE_KINDS:
            raise ValueError(f"unsupported lease_kind: {lease_kind}")
        ttl = self.default_ttl_seconds if ttl_seconds is None else float(ttl_seconds)
        deadline = time.monotonic() + max(0.0, wait_seconds)
        queued = False
        while True:
            try:
                return self._try_acquire(
                    resource_id,
                    owner_agent=owner_agent,
                    root_fev=root_fev,
                    sub_fev=sub_fev,
                    run_id=run_id,
                    lease_kind=lease_kind,
                    ttl_seconds=ttl,
                )
            except LeaseError as exc:
                if "DIRTY" in str(exc) or "RECOVERING" in str(exc):
                    raise
                if time.monotonic() >= deadline:
                    if queued:
                        self._dequeue(resource_id, owner_agent, run_id)
                    raise LeaseError(
                        f"timed out waiting for lease on {resource_id}: {exc}"
                    ) from exc
                if not queued:
                    self._enqueue(
                        resource_id,
                        owner_agent=owner_agent,
                        root_fev=root_fev,
                        sub_fev=sub_fev,
                        run_id=run_id,
                        lease_kind=lease_kind,
                        ttl_seconds=ttl,
                    )
                    queued = True
                time.sleep(poll_interval)

    def heartbeat(self, lease: Lease, *, extend_seconds: float | None = None) -> Lease:
        with self._lock:
            self._expire_stale(now=time.time())
            row = self._conn.execute(
                "SELECT * FROM leases WHERE lease_id = ?", (lease.lease_id,)
            ).fetchone()
            if row is None:
                raise LeaseError(f"unknown lease {lease.lease_id}")
            if row["fencing_token"] != lease.fencing_token:
                raise LeaseError("fencing token mismatch; lease is stale")
            if row["state"] != STATE_LEASED:
                raise LeaseError(f"lease not active: {row['state']}")
            now = time.time()
            ttl = self.default_ttl_seconds if extend_seconds is None else float(extend_seconds)
            expires = now + ttl
            self._conn.execute(
                "UPDATE leases SET heartbeat_at = ?, expires_at = ? WHERE lease_id = ?",
                (now, expires, lease.lease_id),
            )
            self._conn.commit()
            return Lease(
                lease_id=row["lease_id"],
                resource_id=row["resource_id"],
                owner_agent=row["owner_agent"],
                root_fev=row["root_fev"],
                sub_fev=row["sub_fev"],
                run_id=row["run_id"],
                lease_kind=row["lease_kind"],
                fencing_token=row["fencing_token"],
                acquired_at=row["acquired_at"],
                expires_at=expires,
                heartbeat_at=now,
                state=STATE_LEASED,
            )

    def validate_fencing(self, lease: Lease) -> None:
        with self._lock:
            self._expire_stale(now=time.time())
            row = self._conn.execute(
                "SELECT * FROM leases WHERE lease_id = ?", (lease.lease_id,)
            ).fetchone()
            if row is None:
                raise LeaseError(f"unknown lease {lease.lease_id}")
            if row["state"] != STATE_LEASED:
                raise LeaseError(f"lease not active: {row['state']}")
            if row["fencing_token"] != lease.fencing_token:
                raise LeaseError("fencing token mismatch; refusing stale owner")
            res = self._conn.execute(
                "SELECT fencing_token, state FROM resources WHERE resource_id = ?",
                (lease.resource_id,),
            ).fetchone()
            if res is None:
                raise LeaseError(f"unknown resource {lease.resource_id}")
            if res["fencing_token"] != lease.fencing_token:
                raise LeaseError("resource fencing advanced; refusing stale owner")
            if res["state"] in {STATE_DIRTY, STATE_RECOVERING}:
                raise LeaseError(f"resource {lease.resource_id} is {res['state']}")

    def release(self, lease: Lease, *, mark_healthy: bool = True) -> None:
        with self._lock:
            self.validate_fencing(lease)
            self._conn.execute("DELETE FROM leases WHERE lease_id = ?", (lease.lease_id,))
            active = self._active_count(lease.resource_id)
            new_state = STATE_AVAILABLE if mark_healthy and active == 0 else (
                STATE_LEASED if active else STATE_AVAILABLE
            )
            if mark_healthy:
                self._conn.execute(
                    "UPDATE resources SET state = ?, dirty_reason = NULL WHERE resource_id = ?",
                    (new_state, lease.resource_id),
                )
            self._conn.commit()

    def mark_dirty(self, resource_id: str, reason: str) -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE resources SET state = ?, dirty_reason = ? WHERE resource_id = ?",
                (STATE_DIRTY, reason, resource_id),
            )
            self._conn.execute(
                "UPDATE leases SET state = ? WHERE resource_id = ? AND state = ?",
                ("EXPIRED", resource_id, STATE_LEASED),
            )
            self._conn.commit()

    def begin_recovery(self, resource_id: str) -> None:
        with self._lock:
            row = self._conn.execute(
                "SELECT state FROM resources WHERE resource_id = ?", (resource_id,)
            ).fetchone()
            if row is None:
                raise LeaseError(f"unknown resource {resource_id}")
            if row["state"] not in {STATE_DIRTY, STATE_RECOVERING}:
                raise LeaseError(f"resource {resource_id} is not dirty")
            self._conn.execute(
                "UPDATE resources SET state = ? WHERE resource_id = ?",
                (STATE_RECOVERING, resource_id),
            )
            self._conn.commit()

    def complete_recovery(self, resource_id: str) -> int:
        """Clear dirty state and advance fencing token. Returns new token."""
        with self._lock:
            row = self._conn.execute(
                "SELECT fencing_token, state FROM resources WHERE resource_id = ?",
                (resource_id,),
            ).fetchone()
            if row is None:
                raise LeaseError(f"unknown resource {resource_id}")
            if row["state"] not in {STATE_DIRTY, STATE_RECOVERING}:
                raise LeaseError(f"resource {resource_id} is not recovering")
            self._conn.execute("DELETE FROM leases WHERE resource_id = ?", (resource_id,))
            new_token = int(row["fencing_token"]) + 1
            self._conn.execute(
                """
                UPDATE resources
                SET state = ?, dirty_reason = NULL, fencing_token = ?
                WHERE resource_id = ?
                """,
                (STATE_AVAILABLE, new_token, resource_id),
            )
            self._conn.commit()
            return new_token

    def expire_stale(self) -> list[str]:
        with self._lock:
            return self._expire_stale(now=time.time())

    def get_resource(self, resource_id: str) -> ResourceState:
        with self._lock:
            self._expire_stale(now=time.time())
            row = self._conn.execute(
                "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
            ).fetchone()
            if row is None:
                raise LeaseError(f"unknown resource {resource_id}")
            leases = tuple(
                self._row_to_lease(r)
                for r in self._conn.execute(
                    "SELECT * FROM leases WHERE resource_id = ? AND state = ?",
                    (resource_id, STATE_LEASED),
                ).fetchall()
            )
            return ResourceState(
                resource_id=row["resource_id"],
                capacity=row["capacity"],
                state=row["state"],
                fencing_token=row["fencing_token"],
                dirty_reason=row["dirty_reason"],
                active_leases=leases,
            )

    def begin_op(self, lease: Lease, payload: Mapping[str, Any] | None = None) -> str:
        self.validate_fencing(lease)
        op_id = str(uuid.uuid4())
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO editor_ops(op_id, resource_id, lease_id, fencing_token,
                                       started_at, finished_at, status, payload)
                VALUES (?, ?, ?, ?, ?, NULL, 'RUNNING', ?)
                """,
                (
                    op_id,
                    lease.resource_id,
                    lease.lease_id,
                    lease.fencing_token,
                    time.time(),
                    json.dumps(dict(payload or {}), ensure_ascii=False),
                ),
            )
            self._conn.commit()
        return op_id

    def finish_op(self, op_id: str, *, status: str = "DONE") -> None:
        with self._lock:
            self._conn.execute(
                "UPDATE editor_ops SET finished_at = ?, status = ? WHERE op_id = ?",
                (time.time(), status, op_id),
            )
            self._conn.commit()

    def active_ops(self, resource_id: str) -> list[dict[str, Any]]:
        with self._lock:
            rows = self._conn.execute(
                """
                SELECT * FROM editor_ops
                WHERE resource_id = ? AND status = 'RUNNING'
                ORDER BY started_at
                """,
                (resource_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def acquire_many(
        self,
        resource_ids: Sequence[str],
        *,
        owner_agent: str,
        root_fev: str,
        sub_fev: str,
        run_id: str,
        lease_kind: str = LEASE_TRANSACTION,
        ttl_seconds: float | None = None,
        wait_seconds: float = 0.0,
    ) -> list[Lease]:
        """Acquire multiple resources in sorted order to avoid deadlock."""
        ordered = sorted(resource_ids)
        held: list[Lease] = []
        try:
            for rid in ordered:
                held.append(
                    self.acquire(
                        rid,
                        owner_agent=owner_agent,
                        root_fev=root_fev,
                        sub_fev=sub_fev,
                        run_id=run_id,
                        lease_kind=lease_kind,
                        ttl_seconds=ttl_seconds,
                        wait_seconds=wait_seconds,
                    )
                )
            return held
        except Exception:
            for lease in reversed(held):
                try:
                    self.release(lease)
                except LeaseError:
                    pass
            raise

    def _try_acquire(
        self,
        resource_id: str,
        *,
        owner_agent: str,
        root_fev: str,
        sub_fev: str,
        run_id: str,
        lease_kind: str,
        ttl_seconds: float,
    ) -> Lease:
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                self._expire_stale(now=time.time(), commit=False)
                row = self._conn.execute(
                    "SELECT * FROM resources WHERE resource_id = ?", (resource_id,)
                ).fetchone()
                if row is None:
                    raise LeaseError(f"unknown resource {resource_id}")
                if row["state"] in {STATE_DIRTY, STATE_RECOVERING}:
                    raise LeaseError(f"resource {resource_id} is {row['state']}")
                head = self._conn.execute(
                    """
                    SELECT * FROM wait_queue
                    WHERE resource_id = ?
                    ORDER BY queue_id ASC
                    LIMIT 1
                    """,
                    (resource_id,),
                ).fetchone()
                if head is not None and (
                    head["owner_agent"] != owner_agent or head["run_id"] != run_id
                ):
                    raise LeaseError(f"resource {resource_id} has earlier waiter")
                active = self._active_count(resource_id)
                if active >= int(row["capacity"]):
                    raise LeaseError(f"resource {resource_id} at capacity")
                now = time.time()
                fencing = int(row["fencing_token"]) + 1
                lease_id = str(uuid.uuid4())
                self._conn.execute(
                    "UPDATE resources SET state = ?, fencing_token = ? WHERE resource_id = ?",
                    (STATE_LEASED, fencing, resource_id),
                )
                self._conn.execute(
                    """
                    INSERT INTO leases(
                      lease_id, resource_id, owner_agent, root_fev, sub_fev, run_id,
                      lease_kind, fencing_token, acquired_at, expires_at, heartbeat_at, state
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lease_id,
                        resource_id,
                        owner_agent,
                        root_fev,
                        sub_fev,
                        run_id,
                        lease_kind,
                        fencing,
                        now,
                        now + ttl_seconds,
                        now,
                        STATE_LEASED,
                    ),
                )
                self._conn.execute(
                    """
                    DELETE FROM wait_queue
                    WHERE resource_id = ? AND owner_agent = ? AND run_id = ?
                    """,
                    (resource_id, owner_agent, run_id),
                )
                self._conn.commit()
                return Lease(
                    lease_id=lease_id,
                    resource_id=resource_id,
                    owner_agent=owner_agent,
                    root_fev=root_fev,
                    sub_fev=sub_fev,
                    run_id=run_id,
                    lease_kind=lease_kind,
                    fencing_token=fencing,
                    acquired_at=now,
                    expires_at=now + ttl_seconds,
                    heartbeat_at=now,
                    state=STATE_LEASED,
                )
            except Exception:
                self._conn.rollback()
                raise

    def _enqueue(
        self,
        resource_id: str,
        *,
        owner_agent: str,
        root_fev: str,
        sub_fev: str,
        run_id: str,
        lease_kind: str,
        ttl_seconds: float,
    ) -> None:
        with self._lock:
            existing = self._conn.execute(
                """
                SELECT queue_id FROM wait_queue
                WHERE resource_id = ? AND owner_agent = ? AND run_id = ?
                """,
                (resource_id, owner_agent, run_id),
            ).fetchone()
            if existing is not None:
                return
            self._conn.execute(
                """
                INSERT INTO wait_queue(
                  resource_id, requester, enqueued_at, lease_kind,
                  owner_agent, root_fev, sub_fev, run_id, ttl_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    resource_id,
                    owner_agent,
                    time.time(),
                    lease_kind,
                    owner_agent,
                    root_fev,
                    sub_fev,
                    run_id,
                    ttl_seconds,
                ),
            )
            self._conn.commit()

    def _dequeue(self, resource_id: str, owner_agent: str, run_id: str) -> None:
        with self._lock:
            self._conn.execute(
                """
                DELETE FROM wait_queue
                WHERE resource_id = ? AND owner_agent = ? AND run_id = ?
                """,
                (resource_id, owner_agent, run_id),
            )
            self._conn.commit()

    def _active_count(self, resource_id: str) -> int:
        row = self._conn.execute(
            "SELECT COUNT(*) AS c FROM leases WHERE resource_id = ? AND state = ?",
            (resource_id, STATE_LEASED),
        ).fetchone()
        return int(row["c"])

    def _expire_stale(self, *, now: float, commit: bool = True) -> list[str]:
        rows = self._conn.execute(
            "SELECT * FROM leases WHERE state = ? AND expires_at < ?",
            (STATE_LEASED, now),
        ).fetchall()
        touched: list[str] = []
        for row in rows:
            self._conn.execute(
                "UPDATE leases SET state = ? WHERE lease_id = ?",
                ("EXPIRED", row["lease_id"]),
            )
            self._conn.execute(
                """
                UPDATE resources
                SET state = ?, dirty_reason = ?
                WHERE resource_id = ?
                """,
                (
                    STATE_DIRTY,
                    f"lease {row['lease_id']} expired without release",
                    row["resource_id"],
                ),
            )
            touched.append(row["resource_id"])
        if commit:
            self._conn.commit()
        return touched

    @staticmethod
    def _row_to_lease(row: sqlite3.Row) -> Lease:
        return Lease(
            lease_id=row["lease_id"],
            resource_id=row["resource_id"],
            owner_agent=row["owner_agent"],
            root_fev=row["root_fev"],
            sub_fev=row["sub_fev"],
            run_id=row["run_id"],
            lease_kind=row["lease_kind"],
            fencing_token=row["fencing_token"],
            acquired_at=row["acquired_at"],
            expires_at=row["expires_at"],
            heartbeat_at=row["heartbeat_at"],
            state=row["state"],
        )
