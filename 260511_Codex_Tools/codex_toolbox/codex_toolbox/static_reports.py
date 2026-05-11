from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


CATLAW_PIPELINE_REPORT = Path(r"D:\Codex_Sandbox\CatLaw\Docs\CatLaw_Pipeline_Comparative_Report.html")


@dataclass(frozen=True)
class StaticReportStatus:
    ready: bool
    health: str
    summary: str
    details: Sequence[str]
    report_path: Path


def build_static_report_command(report_path: Path = CATLAW_PIPELINE_REPORT) -> list[str]:
    return ["powershell", "-NoProfile", "-Command", f"Start-Process -FilePath '{Path(report_path)}'"]


def get_static_report_status(report_path: Path = CATLAW_PIPELINE_REPORT) -> StaticReportStatus:
    report_path = Path(report_path)
    exists = report_path.exists()
    details = [
        f"Report HTML: {report_path}",
        f"Containing folder: {report_path.parent}",
        f"Exists: {'yes' if exists else 'no'}",
    ]
    if exists:
        details.append(f"Size: {report_path.stat().st_size} bytes")

    return StaticReportStatus(
        ready=exists,
        health="ok" if exists else "error",
        summary="Static report is available" if exists else "Static report is missing",
        details=details,
        report_path=report_path,
    )


def launch_static_report(report_path: Path = CATLAW_PIPELINE_REPORT) -> subprocess.Popen:
    report_path = Path(report_path)
    if os.name == "nt":
        return subprocess.Popen(
            build_static_report_command(report_path),
            cwd=str(report_path.parent),
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
    return subprocess.Popen(["xdg-open", str(report_path)], cwd=str(report_path.parent))
