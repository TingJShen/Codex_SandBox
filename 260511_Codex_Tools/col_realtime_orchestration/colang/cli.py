from __future__ import annotations

import argparse
import json
from pathlib import Path

from colang.parser import parse_col
from colang.simulator import simulate_program
from colang.runner import CodexThreadBackend, InMemoryThreadBackend, run_program
from colang.validator import validate_program
from colang.visualizer import render_html


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="COL v0.2 compiler and simulator")
    sub = parser.add_subparsers(dest="command", required=True)

    compile_cmd = sub.add_parser("compile", help="Compile COL source to JSON IR")
    compile_cmd.add_argument("source")
    compile_cmd.add_argument("--out")

    check_cmd = sub.add_parser("check", help="Run static checks")
    check_cmd.add_argument("source")

    trace_cmd = sub.add_parser("trace", help="Simulate a trace")
    trace_cmd.add_argument("source")
    trace_cmd.add_argument("--out")

    viz_cmd = sub.add_parser("viz", help="Render an HTML trace visualizer")
    viz_cmd.add_argument("source")
    viz_cmd.add_argument("--out", required=True)

    run_cmd = sub.add_parser("run", help="Run COL through a thread backend")
    run_cmd.add_argument("source")
    run_cmd.add_argument("--out")
    run_cmd.add_argument("--backend", choices=["codex", "mock"], default="codex")
    run_cmd.add_argument("--mock-response", default="")
    run_cmd.add_argument("--timeout-seconds", type=int, default=120)
    run_cmd.add_argument("--graph-out")
    run_cmd.add_argument("--cwd", help="Workspace cwd for visible Codex Desktop threads")

    args = parser.parse_args(argv)
    program = parse_col(Path(args.source).read_text(encoding="utf-8"))

    if args.command == "compile":
        return _write_or_print(program.to_ir(), args.out)

    if args.command == "check":
        diagnostics = [diagnostic.to_ir() for diagnostic in validate_program(program)]
        print(json.dumps(diagnostics, indent=2, ensure_ascii=False))
        return 1 if diagnostics else 0

    if args.command == "trace":
        trace = simulate_program(program)
        return _write_or_print(trace.to_ir(), args.out)

    if args.command == "viz":
        trace = simulate_program(program)
        _write_text(args.out, render_html(program, trace))
        return 0

    if args.command == "run":
        diagnostics = validate_program(program)
        if diagnostics:
            print(json.dumps([diagnostic.to_ir() for diagnostic in diagnostics], indent=2))
            return 1
        if args.backend == "mock":
            backend = InMemoryThreadBackend(default_response=args.mock_response)
        else:
            backend = CodexThreadBackend(cwd=Path(args.cwd).resolve() if args.cwd else Path.cwd())
        result = run_program(
            program,
            backend=backend,
            timeout_seconds=args.timeout_seconds,
        )
        if args.graph_out:
            _write_text(
                args.graph_out,
                json.dumps(result.get("thread_graph", {}), indent=2, ensure_ascii=False)
                + "\n",
            )
        return _write_or_print(result, args.out)

    return 2


def _write_or_print(payload: dict, out: str | None) -> int:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if out:
        _write_text(out, text + "\n")
    else:
        print(text)
    return 0


def _write_text(out: str, text: str) -> None:
    target = Path(out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
