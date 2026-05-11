from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_COL_PROJECT_ROOT = Path(r"D:\Codex_Sandbox\260421_Codex_Language")
DEFAULT_COL_REALTIME_SCRIPT = DEFAULT_COL_PROJECT_ROOT / "colang" / "realtime.py"
DEFAULT_COL_HOST = "127.0.0.1"
DEFAULT_COL_PORT = 8765
DEFAULT_COL_SCAN_COUNT = 12


@dataclass(frozen=True)
class ProcessInfo:
    pid: int
    command_line: str


@dataclass(frozen=True)
class ColRealtimeStatus:
    ready: bool
    health: str
    summary: str
    details: Sequence[str]
    running: bool
    reachable_url: str | None
    script_path: Path
    processes: Sequence[ProcessInfo]


def candidate_urls(
    host: str = DEFAULT_COL_HOST,
    port: int = DEFAULT_COL_PORT,
    scan_count: int = DEFAULT_COL_SCAN_COUNT,
) -> list[str]:
    return [f"http://{host}:{candidate}/" for candidate in range(port, port + scan_count)]


def build_col_realtime_command(
    script_path: Path = DEFAULT_COL_REALTIME_SCRIPT,
    *,
    host: str = DEFAULT_COL_HOST,
    port: int = DEFAULT_COL_PORT,
    scan_count: int = DEFAULT_COL_SCAN_COUNT,
    python_exe: str | None = None,
) -> list[str]:
    return [
        python_exe or sys.executable,
        str(Path(script_path)),
        "--host",
        host,
        "--port",
        str(port),
        "--scan-count",
        str(scan_count),
        "--speed",
        "1",
    ]


def probe_col_realtime(url: str, timeout: float = 0.8) -> bool:
    try:
        with urllib.request.urlopen(f"{url.rstrip('/')}/health", timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
            return payload.get("ok") is True and "real" in payload.get("modes", [])
    except (OSError, urllib.error.URLError, TimeoutError, ValueError):
        return False


def find_reachable_url(
    host: str = DEFAULT_COL_HOST,
    port: int = DEFAULT_COL_PORT,
    scan_count: int = DEFAULT_COL_SCAN_COUNT,
) -> str | None:
    for url in candidate_urls(host, port, scan_count):
        if probe_col_realtime(url):
            return url
    return None


def get_col_realtime_processes() -> list[ProcessInfo]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-CimInstance Win32_Process -Filter \"name = 'python.exe'\" | "
        "Where-Object { $_.CommandLine -like '*colang*realtime.py*' } | "
        "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress",
    ]
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        check=False,
    )
    if completed.returncode != 0 or not completed.stdout.strip():
        return []
    payload = json.loads(completed.stdout)
    rows = payload if isinstance(payload, list) else [payload]
    processes: list[ProcessInfo] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        pid = int(row.get("ProcessId") or 0)
        command_line = str(row.get("CommandLine") or "").strip()
        if pid and command_line:
            processes.append(ProcessInfo(pid=pid, command_line=command_line))
    return sorted(processes, key=lambda item: item.pid)


def get_col_realtime_status(
    script_path: Path = DEFAULT_COL_REALTIME_SCRIPT,
    *,
    host: str = DEFAULT_COL_HOST,
    port: int = DEFAULT_COL_PORT,
    scan_count: int = DEFAULT_COL_SCAN_COUNT,
) -> ColRealtimeStatus:
    script_path = Path(script_path)
    processes = get_col_realtime_processes()
    reachable_url = find_reachable_url(host, port, scan_count)
    running = bool(processes)
    ready = script_path.exists()

    details = [
        f"COL project root: {script_path.parents[1] if len(script_path.parents) > 1 else script_path.parent}",
        f"Realtime script: {script_path}",
        "Candidate URLs: " + ", ".join(candidate_urls(host, port, scan_count)),
        f"HTTP status: {reachable_url or 'not reachable'}",
    ]
    if processes:
        details.append("Processes:")
        details.extend(f"  pid={item.pid} {item.command_line}" for item in processes)
    else:
        details.append("Processes: not running")

    if not ready:
        health = "error"
        summary = "COL realtime script missing"
    elif reachable_url:
        health = "ok"
        summary = f"COL realtime is running at {reachable_url}"
    elif running:
        health = "warning"
        summary = "COL realtime process is running but HTTP is not ready"
    else:
        health = "warning"
        summary = "COL realtime dashboard is available to launch"

    return ColRealtimeStatus(
        ready=ready,
        health=health,
        summary=summary,
        details=details,
        running=running,
        reachable_url=reachable_url,
        script_path=script_path,
        processes=processes,
    )


def launch_col_realtime(script_path: Path = DEFAULT_COL_REALTIME_SCRIPT) -> subprocess.Popen:
    script_path = Path(script_path)
    command = build_col_realtime_command(script_path)
    env = os.environ.copy()
    env["PYTHONPATH"] = str(script_path.parents[1])
    process = subprocess.Popen(
        command,
        cwd=str(script_path.parents[1]),
        env=env,
        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
    )
    for _ in range(20):
        url = find_reachable_url()
        if url:
            webbrowser.open(url)
            break
        time.sleep(0.25)
    return process
