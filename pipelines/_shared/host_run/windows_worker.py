"""host-evidence: isolated AIAGENT process launcher with owner / visible-window guard."""

from __future__ import annotations

import ctypes as c
import json
import subprocess
import time
from ctypes import wintypes as w
from datetime import datetime, timezone
from pathlib import Path


def query(script):
    result = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", script],
                            capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, check=True)
    return json.loads(result.stdout) if result.stdout.strip() else None


class StartupInfo(c.Structure):
    _fields_ = [("cb", w.DWORD), ("reserved", w.LPWSTR), ("desktop", w.LPWSTR), ("title", w.LPWSTR),
                ("x", w.DWORD), ("y", w.DWORD), ("xs", w.DWORD), ("ys", w.DWORD),
                ("xc", w.DWORD), ("yc", w.DWORD), ("fill", w.DWORD), ("flags", w.DWORD),
                ("show", w.WORD), ("cbReserved", w.WORD), ("lpReserved", c.POINTER(c.c_byte)),
                ("stdin", w.HANDLE), ("stdout", w.HANDLE), ("stderr", w.HANDLE)]


class ProcessInfo(c.Structure):
    _fields_ = [("process", w.HANDLE), ("thread", w.HANDLE), ("pid", w.DWORD), ("tid", w.DWORD)]


def run_owned(command, *, root, credential, environment, record_path, guard, timeout=300):
    if credential["username"].casefold() != "aiagent":
        raise ValueError("Worker credential username must be AIAGENT")
    guard()
    api, kernel = c.WinDLL("advapi32", use_last_error=True), c.WinDLL("kernel32", use_last_error=True)
    api.CreateProcessWithLogonW.argtypes = [w.LPCWSTR, w.LPCWSTR, w.LPCWSTR, w.DWORD, w.LPCWSTR, w.LPWSTR,
                                          w.DWORD, w.LPVOID, w.LPCWSTR, c.POINTER(StartupInfo), c.POINTER(ProcessInfo)]
    api.CreateProcessWithLogonW.restype = w.BOOL
    kernel.WaitForSingleObject.argtypes = [w.HANDLE, w.DWORD]
    kernel.GetExitCodeProcess.argtypes = [w.HANDLE, c.POINTER(w.DWORD)]
    kernel.TerminateProcess.argtypes = [w.HANDLE, w.UINT]
    kernel.CloseHandle.argtypes = [w.HANDLE]
    startup = StartupInfo()
    startup.cb, startup.flags, startup.show = c.sizeof(startup), 1, 0
    info = ProcessInfo()
    block = c.create_unicode_buffer("\0".join(k + "=" + v for k, v in sorted(environment.items())) + "\0\0")
    if not api.CreateProcessWithLogonW(credential["username"], ".", credential["password"], 1, command[0],
                                     c.create_unicode_buffer(subprocess.list2cmdline(command)), 0x08000400, block,
                                     str(root), c.byref(startup), c.byref(info)):
        raise c.WinError(c.get_last_error())
    record = {"pid": info.pid, "started": datetime.now(timezone.utc).isoformat(), "command": command}
    verified = False
    try:
        identity = query(f'$p=Get-CimInstance Win32_Process -Filter "ProcessId={info.pid}"; $o=Invoke-CimMethod -InputObject $p -MethodName GetOwner; [pscustomobject]@{{owner=$o.User;session=$p.SessionId;pid=$p.ProcessId;command=$p.CommandLine}} | ConvertTo-Json -Compress')
        if not identity or identity["owner"].casefold() != "aiagent" or str(root).casefold() not in identity["command"].casefold():
            raise RuntimeError("Worker owner / workspace identity mismatch")
        verified, record["identity"] = True, identity
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        user = c.WinDLL("user32", use_last_error=True)
        user.GetWindowThreadProcessId.argtypes = [w.HWND, c.POINTER(w.DWORD)]
        user.IsWindowVisible.argtypes = [w.HWND]
        callback_type = c.WINFUNCTYPE(w.BOOL, w.HWND, w.LPARAM)
        started = time.monotonic()
        while kernel.WaitForSingleObject(info.process, 1000) == 258:
            guard()
            visible = []
            def inspect(hwnd, _):
                pid = w.DWORD()
                user.GetWindowThreadProcessId(hwnd, c.byref(pid))
                if pid.value == info.pid and user.IsWindowVisible(hwnd):
                    visible.append(int(hwnd))
                return True
            user.EnumWindows(callback_type(inspect), 0)
            if visible:
                raise RuntimeError("Worker created a visible window on the Human desktop")
            if time.monotonic() - started > timeout:
                raise TimeoutError("AIAGENT Worker timed out")
        exit_code = w.DWORD()
        kernel.GetExitCodeProcess(info.process, c.byref(exit_code))
        record.update(exit_code=exit_code.value, visible_window_guard_pass=True)
        return record
    except (RuntimeError, TimeoutError, OSError) as exc:
        record["error"] = str(exc)
        if verified and kernel.WaitForSingleObject(info.process, 0) == 258:
            kernel.TerminateProcess(info.process, 1)
        raise
    finally:
        record_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        kernel.CloseHandle(info.thread)
        kernel.CloseHandle(info.process)
