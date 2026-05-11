from __future__ import annotations

import json
import os
import subprocess
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_GPU_DASHBOARD_EXE = Path(r"D:\Codex_Sandbox\Huawei_Hard\GPUStatusDashboard.exe")
DEFAULT_GPU_DASHBOARD_URL = "http://127.0.0.1:8766"
DEFAULT_GPU_DASHBOARD_PORT = 8766


@dataclass(frozen=True)
class ProcessInfo:
    name: str
    pid: int


@dataclass(frozen=True)
class DashboardToolStatus:
    ready: bool
    health: str
    summary: str
    details: Sequence[str]
    running: bool
    reachable: bool
    exe_path: Path
    url: str
    processes: Sequence[ProcessInfo]


def _text(value: object) -> str:
    return str(value or "").strip()


def build_gpu_dashboard_command(exe_path: Path = DEFAULT_GPU_DASHBOARD_EXE) -> list[str]:
    return [str(Path(exe_path))]


def get_gpu_dashboard_processes() -> list[ProcessInfo]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process GPUStatusDashboard -ErrorAction SilentlyContinue | "
        "Select-Object ProcessName,Id | ConvertTo-Json -Compress",
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
        name = _text(row.get("ProcessName"))
        pid = int(row.get("Id") or 0)
        if name and pid:
            processes.append(ProcessInfo(name=name, pid=pid))
    return sorted(processes, key=lambda item: (item.name.lower(), item.pid))


def probe_gpu_dashboard(url: str = DEFAULT_GPU_DASHBOARD_URL, timeout: float = 1.0) -> bool:
    try:
        with urllib.request.urlopen(f"{url}/api/status", timeout=timeout) as response:
            if response.status != 200:
                return False
            payload = json.loads(response.read().decode("utf-8"))
            return "summary" in payload and "hosts" in payload
    except (OSError, urllib.error.URLError, TimeoutError, ValueError):
        return False


def get_gpu_dashboard_status(
    exe_path: Path = DEFAULT_GPU_DASHBOARD_EXE,
    url: str = DEFAULT_GPU_DASHBOARD_URL,
) -> DashboardToolStatus:
    exe_path = Path(exe_path)
    processes = get_gpu_dashboard_processes()
    reachable = probe_gpu_dashboard(url)
    running = bool(processes)

    details = [
        f"Dashboard exe: {exe_path}",
        f"Dashboard URL: {url}",
        f"Expected port: {DEFAULT_GPU_DASHBOARD_PORT}",
    ]
    if processes:
        details.append("Processes: " + ", ".join(f"{p.name} pid={p.pid}" for p in processes))
    else:
        details.append("Processes: not running")
    details.append(f"HTTP status: {'reachable' if reachable else 'not reachable'}")

    ready = exe_path.exists()
    if not exe_path.exists():
        health = "error"
        summary = "GPU dashboard exe missing"
    elif reachable:
        health = "ok"
        summary = "GPU dashboard is running"
    elif running:
        health = "warning"
        summary = "GPU dashboard process is running but HTTP is not ready"
    else:
        health = "warning"
        summary = "GPU dashboard is available to launch"

    return DashboardToolStatus(
        ready=ready,
        health=health,
        summary=summary,
        details=details,
        running=running,
        reachable=reachable,
        exe_path=exe_path,
        url=url,
        processes=processes,
    )


def launch_gpu_dashboard(exe_path: Path = DEFAULT_GPU_DASHBOARD_EXE) -> subprocess.Popen:
    command = build_gpu_dashboard_command(exe_path)
    return subprocess.Popen(
        command,
        cwd=str(Path(exe_path).resolve().parent),
    )
