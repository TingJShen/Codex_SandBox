from __future__ import annotations

import argparse
import os
import sys
import threading
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Any, Callable

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from codex_toolbox.codex_repair import (
    build_repair_command,
    get_repair_tool_status,
    launch_repair_gui,
)
from codex_toolbox.col_realtime import (
    DEFAULT_COL_REALTIME_SCRIPT,
    build_col_realtime_command,
    get_col_realtime_status,
    launch_col_realtime,
)
from codex_toolbox.gpu_dashboard import (
    DEFAULT_GPU_DASHBOARD_EXE,
    build_gpu_dashboard_command,
    get_gpu_dashboard_status,
    launch_gpu_dashboard,
)
from codex_toolbox.static_reports import (
    CATLAW_PIPELINE_REPORT,
    build_static_report_command,
    get_static_report_status,
    launch_static_report,
)


APP_TITLE = "Codex Toolbox"


@dataclass(frozen=True)
class ToolSpec:
    tool_id: str
    display_name: str
    description: str
    primary_path: Path
    get_status: Callable[[], Any]
    launch: Callable[[], Any]
    build_command: Callable[[], list[str]]


def app_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def default_repair_script_path() -> Path:
    root = app_root()
    candidates = [
        root / "CodexThreadRepairGui.ps1",
        Path(__file__).resolve().parents[1] / "CodexThreadRepairGui.ps1",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]


def get_tool_specs() -> list[ToolSpec]:
    repair_script_path = default_repair_script_path()
    gpu_dashboard_path = DEFAULT_GPU_DASHBOARD_EXE
    col_realtime_path = DEFAULT_COL_REALTIME_SCRIPT

    return [
        ToolSpec(
            tool_id="codex_thread_repair",
            display_name="Codex Thread Repair",
            description="Repair Codex Desktop thread visibility, active profile, and session index state.",
            primary_path=repair_script_path,
            get_status=lambda: get_repair_tool_status(repair_script_path),
            launch=lambda: launch_repair_gui(repair_script_path),
            build_command=lambda: build_repair_command(repair_script_path),
        ),
        ToolSpec(
            tool_id="gpu_status_dashboard",
            display_name="GPU Status Dashboard",
            description="Launch the live GPU dashboard and open the local web view on port 8766.",
            primary_path=gpu_dashboard_path,
            get_status=lambda: get_gpu_dashboard_status(gpu_dashboard_path),
            launch=lambda: launch_gpu_dashboard(gpu_dashboard_path),
            build_command=lambda: build_gpu_dashboard_command(gpu_dashboard_path),
        ),
        ToolSpec(
            tool_id="col_realtime_orchestration",
            display_name="COL Realtime Orchestration",
            description="Launch the COL multi-agent workflow dashboard with graph monitoring and docs_subagent artifacts.",
            primary_path=col_realtime_path,
            get_status=lambda: get_col_realtime_status(col_realtime_path),
            launch=lambda: launch_col_realtime(col_realtime_path),
            build_command=lambda: build_col_realtime_command(col_realtime_path),
        ),
        ToolSpec(
            tool_id="catlaw_pipeline_report",
            display_name="CatLaw Pipeline Report",
            description="Open the static HTML comparison of Endfield, Assembly Line, Dyson Sphere Program, and Factorio pipeline design.",
            primary_path=CATLAW_PIPELINE_REPORT,
            get_status=lambda: get_static_report_status(CATLAW_PIPELINE_REPORT),
            launch=lambda: launch_static_report(CATLAW_PIPELINE_REPORT),
            build_command=lambda: build_static_report_command(CATLAW_PIPELINE_REPORT),
        ),
    ]


class CodexToolboxApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("980x620")
        self.minsize(860, 540)

        self.tools = get_tool_specs()
        self.selected_index = 0
        self._status_request_id = 0
        self._status_cache: dict[str, Any] = {}

        self._configure_style()
        self._build_layout()
        self.refresh_status()

    def _configure_style(self) -> None:
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass
        self.configure(bg="#f6f7f9")
        self.style.configure("Root.TFrame", background="#f6f7f9")
        self.style.configure("Panel.TFrame", background="#ffffff", borderwidth=1, relief="solid")
        self.style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"), background="#ffffff", foreground="#18202b")
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 10), background="#ffffff", foreground="#596273")
        self.style.configure("Status.TLabel", font=("Segoe UI", 10, "bold"), background="#ffffff")
        self.style.configure("Body.TLabel", font=("Segoe UI", 10), background="#ffffff", foreground="#243040")
        self.style.configure("Tool.TLabel", font=("Segoe UI", 11, "bold"), background="#f6f7f9", foreground="#18202b")
        self.style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=16, style="Root.TFrame")
        root.pack(fill=tk.BOTH, expand=True)
        root.columnconfigure(1, weight=1)
        root.rowconfigure(0, weight=1)

        nav = ttk.Frame(root, padding=(0, 0, 14, 0), style="Root.TFrame")
        nav.grid(row=0, column=0, sticky="ns")
        ttk.Label(nav, text="Tools", style="Tool.TLabel").pack(anchor="w", pady=(0, 8))

        self.tool_list = tk.Listbox(
            nav,
            width=28,
            height=18,
            activestyle="none",
            borderwidth=0,
            highlightthickness=1,
            highlightbackground="#d8dde6",
            selectbackground="#2457d6",
            selectforeground="#ffffff",
            font=("Segoe UI", 10),
        )
        self.tool_list.pack(fill=tk.Y, expand=True)
        for tool in self.tools:
            self.tool_list.insert(tk.END, tool.display_name)
        self.tool_list.selection_set(0)
        self.tool_list.bind("<<ListboxSelect>>", self._on_select_tool)

        detail = ttk.Frame(root, padding=18, style="Panel.TFrame")
        detail.grid(row=0, column=1, sticky="nsew")
        detail.columnconfigure(0, weight=1)
        detail.rowconfigure(4, weight=1)

        header = ttk.Frame(detail, style="Panel.TFrame")
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(header, text="", style="Title.TLabel")
        self.title_label.grid(row=0, column=0, sticky="w")
        self.status_label = ttk.Label(header, text="Checking...", style="Status.TLabel")
        self.status_label.grid(row=0, column=1, sticky="e")

        self.subtitle_label = ttk.Label(
            detail,
            text="",
            style="Subtitle.TLabel",
            wraplength=680,
        )
        self.subtitle_label.grid(row=1, column=0, sticky="ew", pady=(8, 18))

        actions = ttk.Frame(detail, style="Panel.TFrame")
        actions.grid(row=2, column=0, sticky="ew", pady=(0, 14))
        ttk.Button(actions, text="Refresh Status", command=self.refresh_status).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Launch Tool", style="Accent.TButton", command=self.launch_selected_tool).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(actions, text="Open Tool Folder", command=self.open_selected_tool_folder).pack(side=tk.LEFT)

        ttk.Label(detail, text="Current Status", style="Body.TLabel").grid(row=3, column=0, sticky="w")
        self.details = tk.Text(
            detail,
            height=11,
            wrap=tk.WORD,
            borderwidth=1,
            relief=tk.SOLID,
            highlightthickness=0,
            font=("Consolas", 10),
            bg="#fbfcfe",
            fg="#18202b",
        )
        self.details.grid(row=4, column=0, sticky="nsew", pady=(6, 14))
        self.details.configure(state=tk.DISABLED)

        ttk.Label(detail, text="Activity Log", style="Body.TLabel").grid(row=5, column=0, sticky="w")
        self.log = tk.Text(
            detail,
            height=8,
            wrap=tk.WORD,
            borderwidth=1,
            relief=tk.SOLID,
            highlightthickness=0,
            font=("Consolas", 10),
            bg="#101722",
            fg="#d8e2f0",
            insertbackground="#d8e2f0",
        )
        self.log.grid(row=6, column=0, sticky="ew", pady=(6, 0))
        self.log.configure(state=tk.DISABLED)

    def _on_select_tool(self, _event: object) -> None:
        selection = self.tool_list.curselection()
        if selection:
            self.selected_index = int(selection[0])
        self.refresh_status()

    def _selected_tool(self) -> ToolSpec:
        return self.tools[self.selected_index]

    def _set_details(self, lines: list[str]) -> None:
        self.details.configure(state=tk.NORMAL)
        self.details.delete("1.0", tk.END)
        self.details.insert(tk.END, "\n".join(lines))
        self.details.configure(state=tk.DISABLED)

    def _append_log(self, text: str) -> None:
        self.log.configure(state=tk.NORMAL)
        self.log.insert(tk.END, text.rstrip() + "\n")
        self.log.see(tk.END)
        self.log.configure(state=tk.DISABLED)

    def refresh_status(self) -> None:
        tool = self._selected_tool()
        self._status_request_id += 1
        request_id = self._status_request_id
        selected_index = self.selected_index

        self.title_label.configure(text=tool.display_name)
        self.subtitle_label.configure(text=tool.description)
        self.status_label.configure(text="Checking...", foreground="#596273")
        self._set_details(
            [
                f"Tool ID: {tool.tool_id}",
                "",
                "Checking status in the background...",
            ]
        )

        thread = threading.Thread(
            target=self._load_status,
            args=(request_id, selected_index, tool),
            daemon=True,
        )
        thread.start()

    def _load_status(self, request_id: int, selected_index: int, tool: ToolSpec) -> None:
        try:
            status = tool.get_status()
            command = tool.build_command()
            error: str | None = None
        except Exception as exc:  # pragma: no cover - defensive UI boundary
            status = None
            command = []
            error = str(exc)

        try:
            self.after(
                0,
                lambda: self._apply_status_result(
                    request_id=request_id,
                    selected_index=selected_index,
                    tool=tool,
                    status=status,
                    command=command,
                    error=error,
                ),
            )
        except tk.TclError:
            return

    def _apply_status_result(
        self,
        *,
        request_id: int,
        selected_index: int,
        tool: ToolSpec,
        status: Any | None,
        command: list[str],
        error: str | None,
    ) -> None:
        if request_id != self._status_request_id or selected_index != self.selected_index:
            return

        if error or status is None:
            self.status_label.configure(text="Status check failed", foreground="#b42318")
            self._set_details(
                [
                    f"Tool ID: {tool.tool_id}",
                    "",
                    f"Error: {error or 'unknown status error'}",
                ]
            )
            self._append_log(f"Status check failed for {tool.display_name}: {error or 'unknown error'}.")
            return

        self._status_cache[tool.tool_id] = status
        colors = {
            "ok": "#18733b",
            "warning": "#9a5b00",
            "error": "#b42318",
        }
        self.title_label.configure(text=tool.display_name)
        self.subtitle_label.configure(text=tool.description)
        self.status_label.configure(text=status.summary, foreground=colors.get(status.health, "#243040"))
        lines = [
            f"Tool ID: {tool.tool_id}",
            f"Ready: {'yes' if status.ready else 'no'}",
            "",
            *status.details,
            "",
            "Launch command:",
            " ".join(command),
        ]
        self._set_details(lines)
        self._append_log(f"Refreshed status for {tool.display_name}.")

    def launch_selected_tool(self) -> None:
        tool = self._selected_tool()
        status = self._status_cache.get(tool.tool_id)
        if status is None:
            messagebox.showwarning(APP_TITLE, f"{tool.display_name} status is still checking. Try again in a moment.")
            return
        if not status.ready:
            messagebox.showwarning(APP_TITLE, f"{tool.display_name} is not ready. Check the current status first.")
            return

        self.status_label.configure(text="Launching...", foreground="#596273")
        self._append_log(f"Launching {tool.display_name}...")
        thread = threading.Thread(target=self._launch_tool, args=(tool,), daemon=True)
        thread.start()

    def _launch_tool(self, tool: ToolSpec) -> None:
        try:
            process = tool.launch()
        except OSError as exc:
            try:
                self.after(0, lambda: self._launch_failed(tool, str(exc)))
            except tk.TclError:
                pass
            return
        try:
            self.after(0, lambda: self._launch_finished(tool, process.pid))
        except tk.TclError:
            return

    def _launch_failed(self, tool: ToolSpec, error: str) -> None:
        messagebox.showerror(APP_TITLE, f"Launch failed: {error}")
        self._append_log(f"Launch failed for {tool.display_name}: {error}")

    def _launch_finished(self, tool: ToolSpec, pid: int) -> None:
        self._append_log(f"Launched {tool.display_name}, pid={pid}.")
        self.refresh_status()

    def open_selected_tool_folder(self) -> None:
        folder = self._selected_tool().primary_path.resolve().parent
        if os.name == "nt":
            os.startfile(str(folder))
        else:
            messagebox.showinfo(APP_TITLE, str(folder))


def run_self_test() -> int:
    tools = get_tool_specs()
    if not tools or tools[0].tool_id != "codex_thread_repair":
        print("CodexToolbox self-test failed: repair tool is not the first entry")
        return 1

    for tool in tools:
        print(f"tool={tool.tool_id}")
        print(f"path={tool.primary_path}")
        print(f"command={' '.join(tool.build_command())}")
        if tool.tool_id == "codex_thread_repair" and not tool.primary_path.exists():
            print(f"CodexToolbox self-test failed: missing {tool.primary_path}")
            return 1
        if tool.tool_id == "gpu_status_dashboard" and not tool.primary_path.exists():
            print(f"CodexToolbox self-test failed: missing {tool.primary_path}")
            return 1
        if tool.tool_id == "col_realtime_orchestration" and not tool.primary_path.exists():
            print(f"CodexToolbox self-test failed: missing {tool.primary_path}")
            return 1

    print("CodexToolbox self-test ok")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_TITLE)
    parser.add_argument("--self-test", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(sys.argv[1:] if argv is None else argv))
    if args.self_test:
        return run_self_test()
    app = CodexToolboxApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
