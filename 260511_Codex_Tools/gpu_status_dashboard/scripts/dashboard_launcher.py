#!/usr/bin/env python3
"""One-click Windows launcher for the local GPU status dashboard."""

from __future__ import annotations

import argparse
import json
import sys
import threading
import time
import webbrowser
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from typing import Any


if getattr(sys, "frozen", False):
    RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", Path(sys.executable).resolve().parent))
else:
    RESOURCE_ROOT = Path(__file__).resolve().parents[1]

SCRIPTS_DIR = RESOURCE_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import status_dashboard  # noqa: E402

ICON_PATH = RESOURCE_ROOT / "assets" / "gpu-card.ico"


def probe_status(host: str, port: int, timeout: float = 0.8) -> bool:
    conn = HTTPConnection(host, port, timeout=timeout)
    try:
        conn.request("GET", "/api/status")
        response = conn.getresponse()
        if response.status != 200:
            return False
        payload = json.loads(response.read().decode("utf-8"))
        return "summary" in payload and "hosts" in payload
    except Exception:
        return False
    finally:
        conn.close()


def open_browser_later(url: str, delay: float = 0.8) -> None:
    def worker() -> None:
        time.sleep(delay)
        webbrowser.open(url, new=2)

    threading.Thread(target=worker, daemon=True).start()


def start_server(host: str, port: int, auto_query_seconds: int) -> ThreadingHTTPServer:
    status_dashboard.ensure_auto_query_thread()
    if auto_query_seconds > 0:
        status_dashboard.configure_auto_query(auto_query_seconds, run_now=True)

    server = ThreadingHTTPServer((host, port), status_dashboard.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def show_window(url: str, server: ThreadingHTTPServer | None, message: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
    except Exception:
        print(message)
        print(url)
        open_browser_later(url, 0.1)
        try:
            while True:
                time.sleep(3600)
        except KeyboardInterrupt:
            if server:
                server.shutdown()
                server.server_close()
        return

    root = tk.Tk()
    root.title("GPU Status Dashboard")
    root.geometry("430x245")
    root.resizable(False, False)
    root.configure(bg="#fbf7ec")

    if ICON_PATH.exists():
        try:
            root.iconbitmap(default=str(ICON_PATH))
        except Exception:
            pass

    def open_dashboard() -> None:
        webbrowser.open(url, new=2)

    def refresh_snapshot() -> None:
        try:
            conn = HTTPConnection("127.0.0.1", int(url.rsplit(":", 1)[-1]), timeout=1.0)
            conn.request("POST", "/api/refresh")
            conn.getresponse().read()
            conn.close()
            status_var.set("已触发重新查询，页面会自动刷新。")
        except Exception as exc:
            messagebox.showerror("刷新失败", str(exc))

    def on_close() -> None:
        if server is not None:
            try:
                server.shutdown()
                server.server_close()
            except Exception:
                pass
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    title = tk.Label(
        root,
        text="GPU Status Dashboard",
        bg="#fbf7ec",
        fg="#17211c",
        font=("Segoe UI", 18, "bold"),
    )
    title.pack(pady=(20, 4))

    subtitle = tk.Label(
        root,
        text=message,
        bg="#fbf7ec",
        fg="#5f6b63",
        font=("Microsoft YaHei UI", 10),
        wraplength=370,
        justify="center",
    )
    subtitle.pack(pady=(0, 10))

    url_label = tk.Label(root, text=url, bg="#fbf7ec", fg="#245a7a", font=("Consolas", 10))
    url_label.pack(pady=(0, 14))

    row = tk.Frame(root, bg="#fbf7ec")
    row.pack()

    button_style = {
        "font": ("Microsoft YaHei UI", 10, "bold"),
        "relief": "flat",
        "padx": 14,
        "pady": 8,
        "cursor": "hand2",
    }
    tk.Button(row, text="打开网页端", command=open_dashboard, bg="#17211c", fg="#fff9e8", **button_style).pack(side="left", padx=5)
    tk.Button(row, text="重新查询", command=refresh_snapshot, bg="#d9e8dc", fg="#17211c", **button_style).pack(side="left", padx=5)
    tk.Button(row, text="退出服务", command=on_close, bg="#f0ded2", fg="#7a2d24", **button_style).pack(side="left", padx=5)

    status_var = tk.StringVar(value="关闭这个窗口会停止本地服务。")
    status = tk.Label(root, textvariable=status_var, bg="#fbf7ec", fg="#6b756f", font=("Microsoft YaHei UI", 9))
    status.pack(pady=(14, 0))

    open_browser_later(url, 0.7)
    root.mainloop()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Launch GPU status dashboard and open browser.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=status_dashboard.DEFAULT_PORT)
    parser.add_argument("--auto-query-seconds", type=int, default=status_dashboard.DEFAULT_AUTO_QUERY_SECONDS)
    args = parser.parse_args(argv)

    url = f"http://{args.host}:{args.port}"
    if probe_status(args.host, args.port):
        show_window(url, None, "服务已经在运行，已为你打开网页端。")
        return 0

    server = start_server(args.host, args.port, args.auto_query_seconds)
    show_window(url, server, "本地服务已启动，可以固定这个程序到任务栏。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
