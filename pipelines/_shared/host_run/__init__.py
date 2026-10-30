"""host-evidence: shared host helpers for Blender headless and isolated AIAGENT UE5 Worker Runs.

No bpy / unreal import. Graph scripts add ``pipelines/_shared`` to ``sys.path`` and ``import host_run``.
"""

from .local_env import LocalEnvironment, load_local_environment
from .provenance import evidence_hashes, file_sha256, finalize_run, new_run, repository_state, save_json

__all__ = [
    "LocalEnvironment",
    "evidence_hashes",
    "file_sha256",
    "finalize_run",
    "load_local_environment",
    "new_run",
    "repository_state",
    "save_json",
]
