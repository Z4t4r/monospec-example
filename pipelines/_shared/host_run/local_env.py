"""host-evidence: resolve machine-local executables and Worker settings without tracking them.

Resolution order per key: explicit CLI value -> environment variable -> ``.local/environment.yaml`` -> DEFAULTS.
Values may use ``~`` and environment variables (``%USERPROFILE%`` / ``$HOME``); relative paths resolve against the
repository root. Tracked example: ``pipelines/_shared/host_run/environment.example.yaml``.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
LOCAL_FILE = REPOSITORY_ROOT / ".local" / "environment.yaml"

KEYS = {
    "blender_executable": "MONOSPEC_BLENDER",
    "ue_engine_root": "MONOSPEC_UE_ROOT",
    "aiagent_credentials": "MONOSPEC_AIAGENT_CREDENTIALS",
    "aiagent_profile": "MONOSPEC_AIAGENT_PROFILE",
    "worker_root": "MONOSPEC_WORKER_ROOT",
}

# Repository-relative defaults; the credential file stays in the gitignored traits/local/ of this repository.
DEFAULTS = {
    "aiagent_credentials": "traits/local/aiagent.yaml",
    "aiagent_profile": "C:/Users/AIAGENT",
    "worker_root": "_tmp/aiagent-workers",
}


@dataclass(frozen=True)
class LocalEnvironment:
    values: Mapping[str, str | None]
    sources: Mapping[str, str]

    def path(self, key: str) -> Path | None:
        value = self.values.get(key)
        if not value:
            return None
        path = Path(os.path.expanduser(os.path.expandvars(value)))
        return path if path.is_absolute() else REPOSITORY_ROOT / path

    def describe(self) -> dict:
        """Record which source supplied each key; never the credential content."""
        return {key: {"source": self.sources[key], "set": bool(self.values.get(key))} for key in KEYS}


def load_local_environment(overrides: Mapping[str, str | None] | None = None) -> LocalEnvironment:
    overrides = overrides or {}
    file_values: dict = {}
    if LOCAL_FILE.is_file():
        import yaml

        file_values = yaml.safe_load(LOCAL_FILE.read_text(encoding="utf-8")) or {}
    values: dict = {}
    sources: dict = {}
    for key, variable in KEYS.items():
        if overrides.get(key):
            values[key], sources[key] = str(overrides[key]), "cli"
        elif os.environ.get(variable):
            values[key], sources[key] = os.environ[variable], "env:" + variable
        elif file_values.get(key):
            values[key], sources[key] = str(file_values[key]), ".local/environment.yaml"
        elif DEFAULTS.get(key):
            values[key], sources[key] = DEFAULTS[key], "default"
        else:
            values[key], sources[key] = None, "missing"
    return LocalEnvironment(values=values, sources=sources)
