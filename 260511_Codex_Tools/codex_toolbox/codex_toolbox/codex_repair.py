from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


DEFAULT_CODEX_HOME = Path.home() / ".codex"
DEFAULT_ROAMING_ROOT = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")) / "com.carry.codex-tools"
DEFAULT_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "CodexThreadRepairGui.ps1"


@dataclass(frozen=True)
class AccountSummary:
    exists: bool
    current_account_id: str
    active_account_id: str
    effective_account_id: str
    account_count: int
    effective_label: str
    path: Path


@dataclass(frozen=True)
class ProcessInfo:
    name: str
    pid: int


@dataclass(frozen=True)
class RepairToolStatus:
    ready: bool
    health: str
    summary: str
    details: Sequence[str]
    account_summary: AccountSummary
    codex_processes: Sequence[ProcessInfo]
    script_path: Path


def _text(value: object) -> str:
    return str(value or "").strip()


def read_account_summary(roaming_root: Path = DEFAULT_ROAMING_ROOT) -> AccountSummary:
    path = Path(roaming_root) / "accounts.json"
    if not path.exists():
        return AccountSummary(False, "", "", "", 0, "", path)

    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    current_id = _text(payload.get("currentAccountId"))
    settings = payload.get("settings") if isinstance(payload.get("settings"), dict) else {}
    active_id = _text(settings.get("activeAccountId"))
    effective_id = active_id or current_id

    accounts = payload.get("accounts") or []
    effective_label = ""
    for account in accounts:
        if _text(account.get("id")) == effective_id:
            effective_label = _text(account.get("label")) or _text(account.get("email"))
            break

    return AccountSummary(
        exists=True,
        current_account_id=current_id,
        active_account_id=active_id,
        effective_account_id=effective_id,
        account_count=len(accounts),
        effective_label=effective_label,
        path=path,
    )


def get_codex_processes() -> list[ProcessInfo]:
    command = [
        "powershell",
        "-NoProfile",
        "-Command",
        "Get-Process Codex,codex -ErrorAction SilentlyContinue | "
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


def build_repair_command(
    script_path: Path = DEFAULT_SCRIPT_PATH,
    powershell_exe: str = "powershell",
) -> list[str]:
    return [
        powershell_exe,
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(Path(script_path)),
    ]


def get_repair_tool_status(
    script_path: Path = DEFAULT_SCRIPT_PATH,
    roaming_root: Path = DEFAULT_ROAMING_ROOT,
) -> RepairToolStatus:
    script_path = Path(script_path)
    account = read_account_summary(roaming_root)
    processes = get_codex_processes()

    details: list[str] = []
    if script_path.exists():
        details.append(f"Repair script: {script_path}")
    else:
        details.append(f"Repair script missing: {script_path}")

    if account.exists:
        label = account.effective_label or account.effective_account_id or "not selected"
        details.append(f"Active account: {label}")
        details.append(f"activeAccountId: {account.active_account_id or '<empty>'}")
        details.append(f"currentAccountId: {account.current_account_id or '<empty>'}")
        details.append(f"Account count: {account.account_count}")
    else:
        details.append(f"Account file missing: {account.path}")

    if processes:
        details.append("Codex processes: " + ", ".join(f"{p.name} pid={p.pid}" for p in processes))
    else:
        details.append("Codex processes: not running")

    ready = script_path.exists() and account.exists
    if not script_path.exists():
        health = "error"
        summary = "Repair script missing"
    elif not account.exists:
        health = "warning"
        summary = "Account file unavailable"
    elif processes:
        health = "warning"
        summary = "Codex is running; repair will wait for exit"
    else:
        health = "ok"
        summary = "Repair tool is ready"

    return RepairToolStatus(
        ready=ready,
        health=health,
        summary=summary,
        details=details,
        account_summary=account,
        codex_processes=processes,
        script_path=script_path,
    )


def launch_repair_gui(script_path: Path = DEFAULT_SCRIPT_PATH) -> subprocess.Popen:
    command = build_repair_command(script_path)
    return subprocess.Popen(
        command,
        cwd=str(Path(script_path).resolve().parent),
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
    )
