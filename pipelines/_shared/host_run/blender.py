"""host-evidence: launch Blender with an explicit --background flag; never falls back to UI.

The Blender entry script receives the request JSON path after ``--`` and writes its own result files.
Blender headless runs as the current user: it is a private process without shared Editor resources.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Mapping


def blender_command(executable: Path, entry: Path, request: Path) -> list:
    return [str(executable), "--background", "--factory-startup", "--disable-autoexec", "--python-exit-code", "1",
            "--python", str(entry), "--", str(request)]


def run_blender(executable: Path, entry: Path, request: Path, *, log_path: Path, timeout: int = 600) -> Mapping:
    command = blender_command(executable, entry, request)
    if "--background" not in command:
        raise RuntimeError("Blender launcher requires --background")
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8", errors="replace") as log:
        completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, timeout=timeout,
                                   creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    return {"command": command, "exit_code": completed.returncode,
            "seconds": round(time.monotonic() - started, 2), "log": log_path.name}
