"""FEV 1.2.0 parallel investigation coordinator (host-evidence dialect).

Single-host enforceable leases, write-scope ownership, run provenance, and
Root Aggregate Verdict helpers. No bpy / Node / third-party runtime.
"""

from __future__ import annotations

from .aggregation import AggregateResult, aggregate_local_verdicts
from .coordinator import Coordinator, Lease, LeaseError, ResourceState
from .ownership import OwnershipError, OwnershipGuard, WriteScope
from .provenance import RunManifest, build_run_manifest, fingerprint_paths, sha256_file

__all__ = [
    "AggregateResult",
    "Coordinator",
    "Lease",
    "LeaseError",
    "OwnershipError",
    "OwnershipGuard",
    "ResourceState",
    "RunManifest",
    "WriteScope",
    "aggregate_local_verdicts",
    "build_run_manifest",
    "fingerprint_paths",
    "sha256_file",
]

__version__ = "1.2.0"
