#!/usr/bin/env python3
"""
Local dashboard for GPU/CPU status snapshots.

The server reads ./current_status/latest, exposes parsed JSON, and can trigger
scripts/query_gpu_status.ps1 so every manual refresh is also persisted.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import threading
import time
from datetime import datetime
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


if getattr(sys, "frozen", False):
    ROOT = Path(sys.executable).resolve().parent
    RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", ROOT))
else:
    ROOT = Path(__file__).resolve().parents[1]
    RESOURCE_ROOT = ROOT
CURRENT_STATUS = ROOT / "current_status"
LATEST = CURRENT_STATUS / "latest"
QUERY_SCRIPT = RESOURCE_ROOT / "scripts" / "query_gpu_status.ps1"
OWNER = "tjshen"

HOSTS = [
    ("5A100", "5A100_a100"),
    ("8A100", "8A100_young"),
    ("5090_Hao", "5090_Hao_victory"),
    ("5090_Lian", "5090_Lian_marathon"),
]
DEFAULT_PORT = 8766
DEFAULT_PAGE_REFRESH_SECONDS = 5
DEFAULT_AUTO_QUERY_SECONDS = 60
MIN_PAGE_REFRESH_SECONDS = 1
MIN_AUTO_QUERY_SECONDS = 10
MAX_INTERVAL_SECONDS = 3600

SECTION_RE = re.compile(r"^=== ([A-Z_]+) ===$", re.M)
PID_RE = re.compile(r"^PID=(\d+)\s*$")

query_lock = threading.Lock()
query_state: dict[str, Any] = {
    "running": False,
    "last_started": None,
    "last_finished": None,
    "last_error": None,
    "last_output": "",
}
auto_query_lock = threading.Lock()
auto_query_event = threading.Event()
auto_query_thread_started = False
auto_query_state: dict[str, Any] = {
    "enabled": False,
    "interval_seconds": 0,
    "last_configured": None,
}


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def split_sections(text: str) -> dict[str, str]:
    matches = list(SECTION_RE.finditer(text))
    sections: dict[str, str] = {}
    for idx, match in enumerate(matches):
        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[start:end].strip("\n")
    return sections


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(value.strip())
    except Exception:
        return default


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value.strip())
    except Exception:
        return default


def clamp_interval(value: Any, *, minimum: int, maximum: int, default: int) -> int:
    try:
        interval = int(value)
    except Exception:
        interval = default
    if interval <= 0:
        return 0
    return max(minimum, min(maximum, interval))


def parse_gpu(section: str) -> list[dict[str, Any]]:
    gpus = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",")]
        if len(parts) < 5:
            continue
        gpus.append(
            {
                "index": parse_int(parts[0]),
                "name": parts[1],
                "util": parse_int(parts[2]),
                "mem_used": parse_int(parts[3]),
                "mem_total": parse_int(parts[4]),
                "apps": [],
            }
        )
    return gpus


def parse_apps(section: str) -> dict[str, dict[str, Any]]:
    apps: dict[str, dict[str, Any]] = {}
    for raw in section.splitlines():
        line = raw.strip()
        if not line:
            continue
        parts = [part.strip() for part in line.split(",", 2)]
        if len(parts) < 3:
            continue
        pid = parts[0]
        apps[pid] = {
            "pid": pid,
            "process_name": parts[1],
            "gpu_mem": parse_int(parts[2]),
            "gpus": [],
            "user": "",
            "etime": "",
            "command": parts[1],
        }
    return apps


def parse_pmon(section: str) -> list[tuple[int, str]]:
    rows: list[tuple[int, str]] = []
    for raw in section.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2 or parts[1] == "-":
            continue
        rows.append((parse_int(parts[0]), parts[1]))
    return rows


def parse_user_line(line: str) -> dict[str, str] | None:
    parts = line.split(None, 5)
    if len(parts) < 5:
        return None
    args = parts[5] if len(parts) > 5 else parts[4]
    return {
        "user": parts[0],
        "pid": parts[1],
        "ppid": parts[2],
        "etime": parts[3],
        "comm": parts[4],
        "command": args,
    }


def parse_users(section: str) -> dict[str, dict[str, str]]:
    users: dict[str, dict[str, str]] = {}
    current_pid = ""
    for raw in section.splitlines():
        line = raw.rstrip()
        pid_match = PID_RE.match(line)
        if pid_match:
            current_pid = pid_match.group(1)
            continue
        if current_pid and line.strip():
            parsed = parse_user_line(line.strip())
            if parsed:
                users[current_pid] = parsed
            current_pid = ""
    return users


def parse_cpu_line(line: str) -> dict[str, Any] | None:
    parts = line.split(None, 7)
    if len(parts) < 7:
        return None
    args = parts[7] if len(parts) > 7 else parts[6]
    return {
        "pid": parts[0],
        "ppid": parts[1],
        "stat": parts[2],
        "pcpu": parse_float(parts[3]),
        "pmem": parse_float(parts[4]),
        "etime": parts[5],
        "comm": parts[6],
        "command": args,
    }


def is_noise_cpu(row: dict[str, Any]) -> bool:
    command = row.get("command", "")
    comm = row.get("comm", "")
    noise = {
        "systemd",
        "(sd-pam)",
        "dbus-daemon",
        "pulseaudio",
        "sshd",
        "ps",
        "grep",
        "awk",
        "bash",
    }
    if comm in noise:
        return True
    return any(token in command for token in ("ps -u tjshen", "grep -E", "grep -Ev", "bash -s"))


def parse_cpu(section: str) -> list[dict[str, Any]]:
    rows = []
    for raw in section.splitlines():
        parsed = parse_cpu_line(raw.strip())
        if parsed:
            rows.append(parsed)
    return rows


def compact_command(command: str, max_len: int = 180) -> str:
    command = re.sub(r"\s+", " ", command).strip()
    if len(command) <= max_len:
        return command
    return command[: max_len - 1].rstrip() + "…"


def read_latest_snapshot_dir() -> Path:
    pointer = CURRENT_STATUS / "latest_snapshot.txt"
    if pointer.exists():
        value = pointer.read_text(encoding="utf-8-sig", errors="ignore").strip()
        if value:
            return Path(value)
    return LATEST


def parse_host_file(path: Path, alias: str, label: str) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="ignore") if path.exists() else ""
    sections = split_sections(text)
    gpus = parse_gpu(sections.get("GPU", ""))
    apps = parse_apps(sections.get("APPS", ""))
    users = parse_users(sections.get("USERS", ""))

    for gpu_index, pid in parse_pmon(sections.get("PMON", "")):
        if pid in apps:
            apps[pid]["gpus"].append(gpu_index)

    for pid, info in users.items():
        if pid not in apps:
            continue
        apps[pid].update(info)

    gpu_by_index = {gpu["index"]: gpu for gpu in gpus}
    for app in apps.values():
        for gpu_index in app["gpus"]:
            if gpu_index in gpu_by_index:
                gpu_by_index[gpu_index]["apps"].append(app)

    cpu_rows = parse_cpu(sections.get("TJSHEN_CPU_PROCS", ""))
    wait_rows = parse_cpu(sections.get("TJSHEN_CPU_WAIT_POSSIBLE", ""))
    meaningful_cpu = [row for row in cpu_rows if not is_noise_cpu(row)]
    meaningful_wait = [row for row in wait_rows if not is_noise_cpu(row)]

    owner_gpu_apps = [
        app for app in apps.values() if app.get("user") == OWNER or OWNER in app.get("command", "")
    ]

    return {
        "alias": alias,
        "label": label,
        "path": str(path),
        "gpus": gpus,
        "apps": sorted(apps.values(), key=lambda item: (item.get("user", ""), item.get("pid", ""))),
        "owner_gpu_apps": owner_gpu_apps,
        "owner_cpu": meaningful_cpu,
        "owner_wait": meaningful_wait,
    }


def load_status() -> dict[str, Any]:
    snapshot_dir = read_latest_snapshot_dir()
    hosts = []
    for alias, label in HOSTS:
        hosts.append(parse_host_file(snapshot_dir / f"{label}.txt", alias, label))

    owner_gpu_total = sum(len(host["owner_gpu_apps"]) for host in hosts)
    owner_cpu_total = sum(len(host["owner_cpu"]) for host in hosts)
    owner_wait_total = sum(len(host["owner_wait"]) for host in hosts)
    total_gpus = sum(len(host["gpus"]) for host in hosts)
    busy_gpus = sum(1 for host in hosts for gpu in host["gpus"] if gpu["mem_used"] > 512)

    return {
        "generated_at": now_iso(),
        "snapshot_dir": str(snapshot_dir),
        "snapshot_name": snapshot_dir.name,
        "hosts": hosts,
        "summary": {
            "total_gpus": total_gpus,
            "busy_gpus": busy_gpus,
            "free_gpus": total_gpus - busy_gpus,
            "owner_gpu_total": owner_gpu_total,
            "owner_cpu_total": owner_cpu_total,
            "owner_wait_total": owner_wait_total,
        },
        "query": query_state.copy(),
        "auto_query": get_auto_query_state(),
    }


def get_auto_query_state() -> dict[str, Any]:
    with auto_query_lock:
        return auto_query_state.copy()


def configure_auto_query(interval_seconds: Any, *, run_now: bool = False) -> dict[str, Any]:
    interval = clamp_interval(
        interval_seconds,
        minimum=MIN_AUTO_QUERY_SECONDS,
        maximum=MAX_INTERVAL_SECONDS,
        default=DEFAULT_AUTO_QUERY_SECONDS,
    )
    with auto_query_lock:
        auto_query_state.update(
            {
                "enabled": interval > 0,
                "interval_seconds": interval,
                "last_configured": now_iso(),
            }
        )
    auto_query_event.set()
    if run_now and interval > 0:
        start_query_background()
    return get_auto_query_state()


def ensure_auto_query_thread() -> None:
    global auto_query_thread_started
    with auto_query_lock:
        if auto_query_thread_started:
            return
        auto_query_thread_started = True
    threading.Thread(target=auto_query_loop, daemon=True).start()


def build_query_subprocess_kwargs(platform_name: str | None = None) -> dict[str, Any]:
    if platform_name is None:
        platform_name = os.name
    if platform_name != "nt":
        return {}

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = 0
    return {
        "startupinfo": startupinfo,
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
    }


def run_query() -> None:
    with query_lock:
        if query_state["running"]:
            return
        query_state.update(
            {
                "running": True,
                "last_started": now_iso(),
                "last_error": None,
                "last_output": "",
            }
        )

    try:
        if os.name == "nt":
            cmd = [
                "powershell",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(QUERY_SCRIPT),
            ]
        else:
            cmd = ["pwsh", "-ExecutionPolicy", "Bypass", "-File", str(QUERY_SCRIPT)]
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=180,
            check=False,
            **build_query_subprocess_kwargs(),
        )
        with query_lock:
            query_state["last_output"] = proc.stdout[-5000:]
            if proc.returncode != 0:
                query_state["last_error"] = f"query exited with code {proc.returncode}"
    except Exception as exc:
        with query_lock:
            query_state["last_error"] = str(exc)
    finally:
        with query_lock:
            query_state["running"] = False
            query_state["last_finished"] = now_iso()


def start_query_background() -> bool:
    with query_lock:
        if query_state["running"]:
            return False
    thread = threading.Thread(target=run_query, daemon=True)
    thread.start()
    return True


HTML = r"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GPU Fleet Live Board</title>
  <style>
    :root {
      --ink: #17211c;
      --muted: #6b756f;
      --paper: #fbf7ec;
      --panel: rgba(255, 252, 242, 0.82);
      --line: rgba(23, 33, 28, 0.14);
      --green: #276749;
      --amber: #b7791f;
      --red: #b83232;
      --blue: #245a7a;
      --shadow: 0 24px 70px rgba(42, 38, 26, 0.14);
    }

    * { box-sizing: border-box; }
    body {
      margin: 0;
      color: var(--ink);
      font-family: "Aptos", "Segoe UI", "Microsoft YaHei", sans-serif;
      background:
        radial-gradient(circle at 8% 10%, rgba(252, 196, 87, 0.38), transparent 32rem),
        radial-gradient(circle at 88% 8%, rgba(84, 144, 132, 0.28), transparent 28rem),
        linear-gradient(145deg, #fcf6e6 0%, #edf3ee 48%, #f8efe0 100%);
      min-height: 100vh;
    }

    .shell { width: min(1560px, calc(100vw - 32px)); margin: 0 auto; padding: 28px 0 42px; }
    .hero {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 24px;
      align-items: end;
      padding: 26px;
      border: 1px solid var(--line);
      border-radius: 30px;
      background: rgba(255, 250, 238, 0.68);
      box-shadow: var(--shadow);
      backdrop-filter: blur(12px);
    }

    h1 {
      margin: 0;
      font-family: "Cambria", "Microsoft YaHei", serif;
      font-size: clamp(34px, 5vw, 72px);
      line-height: 0.94;
      letter-spacing: -0.055em;
    }

    .subtitle { margin: 14px 0 0; color: var(--muted); font-size: 15px; }
    .controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; justify-content: flex-end; }
    .interval-control {
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 999px;
      background: rgba(255, 255, 255, 0.35);
      color: var(--muted);
      font-size: 12px;
      font-weight: 800;
      white-space: nowrap;
    }
    .interval-control input {
      width: 72px;
      border: 0;
      border-radius: 999px;
      padding: 7px 9px;
      background: rgba(23, 33, 28, 0.08);
      color: var(--ink);
      font-weight: 900;
      text-align: right;
      outline: none;
    }
    button {
      border: 0;
      border-radius: 999px;
      padding: 12px 18px;
      background: var(--ink);
      color: #fff9e8;
      font-weight: 800;
      cursor: pointer;
      box-shadow: 0 12px 28px rgba(23, 33, 28, 0.18);
    }
    button.secondary { background: rgba(23, 33, 28, 0.08); color: var(--ink); box-shadow: none; }
    button:disabled { opacity: 0.55; cursor: wait; }

    .stamp { color: var(--muted); font-size: 13px; text-align: right; }
    .cards { display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 14px; margin: 18px 0; }
    .card {
      border: 1px solid var(--line);
      border-radius: 24px;
      padding: 18px;
      background: var(--panel);
      box-shadow: 0 14px 36px rgba(44, 40, 30, 0.08);
    }
    .card .label { color: var(--muted); font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; }
    .card .value { font-size: 34px; font-weight: 900; margin-top: 8px; }

    .owner-banner {
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 16px;
      align-items: center;
      margin-bottom: 18px;
      padding: 18px 20px;
      border: 2px solid rgba(184, 50, 50, 0.28);
      border-radius: 26px;
      background:
        linear-gradient(135deg, rgba(255, 244, 226, 0.92), rgba(255, 232, 220, 0.72)),
        radial-gradient(circle at 0 0, rgba(184, 50, 50, 0.12), transparent 18rem);
      box-shadow: 0 18px 50px rgba(107, 38, 25, 0.13);
    }
    .owner-banner.clean {
      border-color: rgba(39, 103, 73, 0.24);
      background: linear-gradient(135deg, rgba(239, 250, 242, 0.92), rgba(247, 252, 237, 0.74));
    }
    .owner-badge {
      width: 74px;
      height: 74px;
      border-radius: 22px;
      display: grid;
      place-items: center;
      background: var(--red);
      color: #fff9e8;
      font-size: 30px;
      font-weight: 950;
      box-shadow: 0 16px 38px rgba(184, 50, 50, 0.22);
    }
    .owner-banner.clean .owner-badge { background: var(--green); box-shadow: 0 16px 38px rgba(39, 103, 73, 0.18); }
    .owner-title { font-size: 20px; font-weight: 950; margin-bottom: 8px; }
    .owner-detail { color: var(--muted); line-height: 1.55; }
    .owner-detail strong { color: var(--ink); }

    .grid { display: grid; grid-template-columns: 1.2fr 0.8fr; gap: 16px; align-items: start; }
    .panel {
      border: 1px solid var(--line);
      border-radius: 28px;
      background: var(--panel);
      box-shadow: var(--shadow);
      overflow: hidden;
    }
    .panel-head { display: flex; justify-content: space-between; gap: 12px; align-items: center; padding: 18px 20px; border-bottom: 1px solid var(--line); }
    .panel-title { font-size: 18px; font-weight: 900; }
    .pill { border-radius: 999px; padding: 6px 10px; background: rgba(39, 103, 73, 0.12); color: var(--green); font-weight: 800; font-size: 12px; }
    .pill.warn { background: rgba(183, 121, 31, 0.14); color: var(--amber); }
    .pill.hot { background: rgba(184, 50, 50, 0.13); color: var(--red); }

    table { width: 100%; border-collapse: collapse; font-size: 13px; }
    th, td { padding: 11px 12px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }
    th { color: var(--muted); font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; background: rgba(255, 255, 255, 0.28); position: sticky; top: 0; }
    tr:last-child td { border-bottom: 0; }
    .table-wrap { max-height: 520px; overflow: auto; }
    .host-tag { font-weight: 900; color: var(--blue); }
    .cmd { color: #31443a; max-width: 720px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .empty { padding: 28px; color: var(--muted); text-align: center; }

    .gpu-map { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 16px; }
    .host-card { border: 1px solid var(--line); border-radius: 22px; background: rgba(255, 255, 255, 0.34); overflow: hidden; }
    .host-card h3 { margin: 0; padding: 13px 14px; border-bottom: 1px solid var(--line); font-size: 16px; }
    .gpu-tile { padding: 11px 14px; border-bottom: 1px solid var(--line); }
    .gpu-tile.owner-hit {
      background: linear-gradient(90deg, rgba(184, 50, 50, 0.12), rgba(255, 255, 255, 0.1));
      box-shadow: inset 4px 0 0 var(--red);
    }
    .gpu-tile:last-child { border-bottom: 0; }
    .gpu-line { display: flex; justify-content: space-between; gap: 12px; font-weight: 800; }
    .meter { height: 8px; background: rgba(23, 33, 28, 0.08); border-radius: 999px; overflow: hidden; margin-top: 8px; }
    .meter > span { display: block; height: 100%; border-radius: inherit; background: linear-gradient(90deg, #3e8f6f, #d39b2b, #b83232); width: 0%; transition: width 350ms ease; }
    .gpu-meta { margin-top: 7px; color: var(--muted); font-size: 12px; }

    .toast { position: fixed; right: 18px; bottom: 18px; padding: 12px 14px; border-radius: 18px; background: var(--ink); color: #fff9e8; box-shadow: var(--shadow); opacity: 0; transform: translateY(8px); transition: 180ms ease; }
    .toast.show { opacity: 1; transform: translateY(0); }

    @media (max-width: 1100px) {
      .hero, .grid { grid-template-columns: 1fr; }
      .cards { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .owner-banner { grid-template-columns: 1fr; }
      .gpu-map { grid-template-columns: 1fr; }
      .stamp { text-align: left; }
    }

    @media (max-width: 640px) {
      .shell { width: min(100vw - 18px, 1560px); padding-top: 10px; }
      .hero { padding: 18px; border-radius: 22px; }
      .cards { grid-template-columns: 1fr; }
      th, td { padding: 9px; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <h1>GPU Fleet<br>Live Board</h1>
        <p class="subtitle">读取 <code>./current_status/latest</code>，前端自动轮询；点击“重新查询”会触发 SSH 采集并存入 <code>./current_status</code>。</p>
      </div>
      <div>
        <div class="controls">
          <label class="interval-control">Page refresh <input id="pageRefreshSeconds" type="number" min="1" max="3600" step="1" value="5"> s</label>
          <label class="interval-control">SSH collect <input id="queryRefreshSeconds" type="number" min="0" max="3600" step="10" value="60"> s</label>
          <button class="secondary" id="applyIntervalsBtn">Apply</button>
          <button id="refreshBtn">重新查询并保存</button>
          <button class="secondary" id="toggleBtn">暂停自动刷新</button>
        </div>
        <p class="stamp" id="stamp">等待数据…</p>
      </div>
    </section>

    <section class="cards">
      <div class="card"><div class="label">总 GPU</div><div class="value" id="totalGpus">-</div></div>
      <div class="card"><div class="label">忙碌 GPU</div><div class="value" id="busyGpus">-</div></div>
      <div class="card"><div class="label">我们 GPU 进程</div><div class="value" id="ownerGpu">-</div></div>
      <div class="card"><div class="label">我们 CPU/等待</div><div class="value" id="ownerCpu">-</div></div>
    </section>

    <section class="owner-banner clean" id="ownerBanner">
      <div class="owner-badge" id="ownerBadge">0</div>
      <div>
        <div class="owner-title" id="ownerBannerTitle">我们当前没有 GPU 占用</div>
        <div class="owner-detail" id="ownerBannerDetail">等待最新快照。</div>
      </div>
    </section>

    <section class="grid">
      <section class="panel">
        <div class="panel-head"><div class="panel-title">总体 GPU 占用</div><span class="pill" id="snapshotName">snapshot</span></div>
        <div class="gpu-map" id="gpuMap"></div>
      </section>

      <section class="panel">
        <div class="panel-head"><div class="panel-title">我们 tjshen</div><span class="pill" id="ownerState">clean</span></div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>机器</th><th>类型</th><th>PID</th><th>说明</th></tr></thead>
            <tbody id="ownerRows"></tbody>
          </table>
        </div>
      </section>
    </section>

    <section class="panel" style="margin-top: 16px;">
      <div class="panel-head"><div class="panel-title">总体任务表</div><span class="pill warn">all users</span></div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>机器</th><th>GPU</th><th>用户</th><th>PID</th><th>显存</th><th>任务</th></tr></thead>
          <tbody id="taskRows"></tbody>
        </table>
      </div>
    </section>
  </main>

  <div class="toast" id="toast"></div>

  <script>
    const DEFAULT_PAGE_REFRESH_SECONDS = 5;
    const DEFAULT_QUERY_REFRESH_SECONDS = 60;
    const state = {
      paused: false,
      timer: null,
      pageRefreshSeconds: DEFAULT_PAGE_REFRESH_SECONDS,
    };
    const $ = (id) => document.getElementById(id);

    function clampSeconds(value, minValue, maxValue, fallback) {
      const parsed = Number.parseInt(value, 10);
      if (!Number.isFinite(parsed)) return fallback;
      if (parsed <= 0) return 0;
      return Math.max(minValue, Math.min(maxValue, parsed));
    }

    function readSavedPageRefreshSeconds() {
      try {
        return clampSeconds(localStorage.getItem("gpuDashboardPageRefreshSeconds"), 1, 3600, DEFAULT_PAGE_REFRESH_SECONDS);
      } catch {
        return DEFAULT_PAGE_REFRESH_SECONDS;
      }
    }

    function savePageRefreshSeconds(value) {
      try {
        localStorage.setItem("gpuDashboardPageRefreshSeconds", String(value));
      } catch {
        // localStorage can be unavailable in hardened browser profiles.
      }
    }

    function showToast(text) {
      const node = $("toast");
      node.textContent = text;
      node.classList.add("show");
      setTimeout(() => node.classList.remove("show"), 2600);
    }

    function fmtMem(used, total) {
      return `${used}/${total} MiB`;
    }

    function esc(value) {
      return String(value ?? "").replace(/[&<>"']/g, ch => ({
        "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
      }[ch]));
    }

    function compact(value, n = 150) {
      const text = String(value ?? "").replace(/\s+/g, " ").trim();
      return text.length > n ? text.slice(0, n - 1) + "…" : text;
    }

    function renderGpuMap(hosts) {
      $("gpuMap").innerHTML = hosts.map(host => `
        <article class="host-card">
          <h3>${esc(host.alias)}</h3>
          ${host.gpus.map(gpu => {
            const pct = gpu.mem_total ? Math.round(gpu.mem_used * 100 / gpu.mem_total) : 0;
            const ownerHit = gpu.apps.some(app => app.user === "tjshen" || String(app.command || "").includes("tjshen"));
            const apps = gpu.apps.length ? gpu.apps.map(app => `${app.user || "?"}:${app.pid}${app.user === "tjshen" ? " 我们" : ""}`).join(", ") : "空";
            return `
              <div class="gpu-tile ${ownerHit ? "owner-hit" : ""}">
                <div class="gpu-line"><span>GPU ${gpu.index}</span><span>${gpu.util}% / ${pct}% mem</span></div>
                <div class="meter"><span style="width:${Math.min(100, pct)}%"></span></div>
                <div class="gpu-meta">${fmtMem(gpu.mem_used, gpu.mem_total)} · ${esc(apps)}</div>
              </div>`;
          }).join("")}
        </article>
      `).join("");
    }

    function renderOwnerBanner(hosts, summary) {
      const hits = [];
      for (const host of hosts) {
        for (const app of host.owner_gpu_apps) {
          const gpuText = (app.gpus || []).length ? `GPU${app.gpus.join(",")}` : "GPU?";
          hits.push(`<strong>${esc(host.alias)} ${esc(gpuText)}</strong> PID ${esc(app.pid)} · ${esc(app.gpu_mem)} MiB · ${esc(compact(app.command, 80))}`);
        }
      }

      const banner = $("ownerBanner");
      const badge = $("ownerBadge");
      badge.textContent = summary.owner_gpu_total;
      if (hits.length) {
        banner.classList.remove("clean");
        $("ownerBannerTitle").textContent = `我们当前有 ${summary.owner_gpu_total} 个 GPU 进程`;
        $("ownerBannerDetail").innerHTML = hits.join("<br>");
      } else {
        banner.classList.add("clean");
        $("ownerBannerTitle").textContent = "我们当前没有 GPU 占用";
        $("ownerBannerDetail").textContent = summary.owner_cpu_total || summary.owner_wait_total
          ? `GPU 已清空；CPU/等待侧还有 ${summary.owner_cpu_total}/${summary.owner_wait_total} 条记录。`
          : "GPU、CPU 实际任务和等待任务都没有发现。";
      }
    }

    function renderTasks(hosts) {
      const rows = [];
      for (const host of hosts) {
        for (const app of host.apps) {
          rows.push(`<tr>
            <td><span class="host-tag">${esc(host.alias)}</span></td>
            <td>${esc((app.gpus || []).join(",") || "-")}</td>
            <td>${esc(app.user || "?")}</td>
            <td>${esc(app.pid)}</td>
            <td>${esc(app.gpu_mem)} MiB</td>
            <td class="cmd" title="${esc(app.command)}">${esc(compact(app.command))}</td>
          </tr>`);
        }
      }
      $("taskRows").innerHTML = rows.length ? rows.join("") : `<tr><td colspan="6" class="empty">没有 GPU 任务</td></tr>`;
    }

    function renderOwner(hosts, summary) {
      const rows = [];
      for (const host of hosts) {
        for (const app of host.owner_gpu_apps) {
          const gpuText = (app.gpus || []).length ? `GPU ${app.gpus.join(",")}` : "GPU ?";
          rows.push(`<tr><td>${esc(host.alias)}</td><td>${esc(gpuText)}</td><td>${esc(app.pid)}</td><td class="cmd">${esc(app.gpu_mem)} MiB · ${esc(compact(app.command, 110))}</td></tr>`);
        }
        for (const row of host.owner_cpu) {
          rows.push(`<tr><td>${esc(host.alias)}</td><td>CPU</td><td>${esc(row.pid)}</td><td class="cmd">${esc(compact(row.command, 110))}</td></tr>`);
        }
        for (const row of host.owner_wait) {
          rows.push(`<tr><td>${esc(host.alias)}</td><td>WAIT</td><td>${esc(row.pid)}</td><td class="cmd">${esc(compact(row.command, 110))}</td></tr>`);
        }
      }
      $("ownerRows").innerHTML = rows.length ? rows.join("") : `<tr><td colspan="4" class="empty">没有发现 tjshen 的 GPU/CPU 实际任务</td></tr>`;
      const ownerBusy = summary.owner_gpu_total + summary.owner_cpu_total + summary.owner_wait_total;
      const pill = $("ownerState");
      pill.textContent = ownerBusy ? "busy" : "clean";
      pill.className = ownerBusy ? "pill hot" : "pill";
    }

    async function loadStatus() {
      const res = await fetch("/api/status", { cache: "no-store" });
      if (!res.ok) throw new Error(`status ${res.status}`);
      const data = await res.json();
      const s = data.summary;
      const autoQuery = data.auto_query || {};
      $("totalGpus").textContent = s.total_gpus;
      $("busyGpus").textContent = `${s.busy_gpus}/${s.free_gpus} 空`;
      $("ownerGpu").textContent = s.owner_gpu_total;
      $("ownerCpu").textContent = `${s.owner_cpu_total}/${s.owner_wait_total}`;
      $("snapshotName").textContent = data.snapshot_name || "latest";
      $("stamp").textContent = `snapshot: ${data.snapshot_name} | page updated: ${data.generated_at} | page interval: ${state.pageRefreshSeconds}s | SSH collect: ${autoQuery.enabled ? `${autoQuery.interval_seconds}s` : "off"}${data.query.running ? " | querying..." : ""}`;
      $("refreshBtn").disabled = !!data.query.running;
      if (document.activeElement !== $("queryRefreshSeconds")) {
        $("queryRefreshSeconds").value = autoQuery.enabled ? autoQuery.interval_seconds : 0;
      }
      renderGpuMap(data.hosts);
      renderTasks(data.hosts);
      renderOwnerBanner(data.hosts, s);
      renderOwner(data.hosts, s);
    }

    async function triggerRefresh() {
      $("refreshBtn").disabled = true;
      showToast("已开始重新查询，结果会自动刷新");
      const res = await fetch("/api/refresh", { method: "POST" });
      if (!res.ok) showToast("触发查询失败");
      setTimeout(loadStatus, 1000);
    }

    async function applyIntervals() {
      const pageSeconds = clampSeconds($("pageRefreshSeconds").value, 1, 3600, DEFAULT_PAGE_REFRESH_SECONDS);
      const querySeconds = clampSeconds($("queryRefreshSeconds").value, 10, 3600, DEFAULT_QUERY_REFRESH_SECONDS);
      state.pageRefreshSeconds = pageSeconds || DEFAULT_PAGE_REFRESH_SECONDS;
      $("pageRefreshSeconds").value = state.pageRefreshSeconds;
      $("queryRefreshSeconds").value = querySeconds;
      savePageRefreshSeconds(state.pageRefreshSeconds);
      schedule();

      const res = await fetch("/api/config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ auto_query_seconds: querySeconds, run_now: true }),
      });
      if (!res.ok) throw new Error(`config ${res.status}`);
      showToast(`Intervals updated: page ${state.pageRefreshSeconds}s, SSH ${querySeconds ? `${querySeconds}s` : "off"}`);
      setTimeout(loadStatus, 500);
    }

    function schedule() {
      if (state.timer) clearInterval(state.timer);
      state.timer = setInterval(() => {
        if (!state.paused) loadStatus().catch(err => showToast(err.message));
      }, state.pageRefreshSeconds * 1000);
    }

    $("refreshBtn").addEventListener("click", triggerRefresh);
    $("applyIntervalsBtn").addEventListener("click", () => {
      applyIntervals().catch(err => showToast(err.message));
    });
    $("toggleBtn").addEventListener("click", () => {
      state.paused = !state.paused;
      $("toggleBtn").textContent = state.paused ? "恢复自动刷新" : "暂停自动刷新";
    });

    state.pageRefreshSeconds = readSavedPageRefreshSeconds() || DEFAULT_PAGE_REFRESH_SECONDS;
    $("pageRefreshSeconds").value = state.pageRefreshSeconds;
    loadStatus().catch(err => showToast(err.message));
    schedule();
  </script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "GpuStatusDashboard/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        print(f"[{now_iso()}] {self.address_string()} {fmt % args}")

    def send_json(self, payload: Any, status: HTTPStatus = HTTPStatus.OK) -> None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def send_html(self) -> None:
        data = HTML.encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def read_json_body(self) -> dict[str, Any]:
        length = parse_int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        if not raw:
            return {}
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.send_html()
            return
        if parsed.path == "/api/status":
            self.send_json(load_status())
            return
        self.send_error(HTTPStatus.NOT_FOUND, "not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path == "/api/refresh":
            started = start_query_background()
            self.send_json({"started": started, "query": query_state.copy()})
            return
        if parsed.path == "/api/config":
            try:
                payload = self.read_json_body()
                auto_query = configure_auto_query(
                    payload.get("auto_query_seconds", DEFAULT_AUTO_QUERY_SECONDS),
                    run_now=bool(payload.get("run_now", False)),
                )
            except Exception as exc:
                self.send_json({"error": str(exc)}, HTTPStatus.BAD_REQUEST)
                return
            self.send_json({"auto_query": auto_query})
            return
        self.send_error(HTTPStatus.NOT_FOUND, "not found")


def auto_query_loop() -> None:
    while True:
        state = get_auto_query_state()
        if not state["enabled"]:
            auto_query_event.wait()
            auto_query_event.clear()
            continue
        interval = state["interval_seconds"]
        if auto_query_event.wait(interval):
            auto_query_event.clear()
            continue
        run_query()


def main() -> int:
    parser = argparse.ArgumentParser(description="Serve a local live GPU status dashboard.")
    parser.add_argument("--host", default="127.0.0.1", help="Bind host, default: 127.0.0.1")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"Bind port, default: {DEFAULT_PORT}")
    parser.add_argument(
        "--auto-query-seconds",
        type=int,
        default=0,
        help="If >0, automatically run the SSH query at this interval.",
    )
    args = parser.parse_args()

    ensure_auto_query_thread()
    if args.auto_query_seconds > 0:
        configure_auto_query(args.auto_query_seconds, run_now=True)

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"Dashboard: http://{args.host}:{args.port}")
    print(f"Reading snapshots from: {CURRENT_STATUS}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
