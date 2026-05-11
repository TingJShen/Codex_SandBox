from __future__ import annotations

import argparse
import json
import queue
import re
import socket
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlparse

from colang.runner import DEFAULT_CODEX_EXE, DEFAULT_CODEX_HOME, _CodexRpcSession


class RealtimeHTTPServer(ThreadingHTTPServer):
    allow_reuse_address = True


def build_port_report(
    host: str = "127.0.0.1",
    *,
    preferred_port: int = 8765,
    scan_count: int = 12,
) -> dict[str, Any]:
    ports = list(range(preferred_port, preferred_port + scan_count))
    occupied = [port for port in ports if not _is_port_available(host, port)]
    available = [port for port in ports if port not in occupied]
    return {
        "host": host,
        "preferred_port": preferred_port,
        "ports": ports,
        "occupied_ports": occupied,
        "available_ports": available,
        "available_urls": [f"http://{host}:{port}/" for port in available],
    }


def choose_listen_port(
    host: str = "127.0.0.1",
    *,
    preferred_port: int = 8765,
    scan_count: int = 12,
) -> tuple[int, dict[str, Any]]:
    report = build_port_report(host, preferred_port=preferred_port, scan_count=scan_count)
    available = report["available_ports"]
    if not available:
        raise RuntimeError(
            f"no available port in range {preferred_port}-{preferred_port + scan_count - 1}"
        )
    return int(available[0]), report


def _is_port_available(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
        except OSError:
            return False
    return True


@dataclass(frozen=True)
class DemoNode:
    id: str
    label: str
    role: str
    phase: str
    duration_seconds: int
    outputs: tuple[str, ...]
    parallel_group: str | None = None

    def to_public(self) -> dict[str, Any]:
        data = asdict(self)
        data["outputs"] = list(self.outputs)
        return data


DEMO_NODES = [
    DemoNode(
        id="decode",
        label="Decode COL v0.4 Workflow",
        role="orchestrator",
        phase="serial",
        duration_seconds=1,
        outputs=("Loaded workflow roots",),
    ),
    DemoNode(
        id="plan",
        label="Plan Director Handoff",
        role="planner",
        phase="serial",
        duration_seconds=2,
        outputs=("Resolved roles", "Prepared artifacts"),
    ),
    DemoNode(
        id="research",
        label="Research Director",
        role="researcher",
        phase="parallel",
        duration_seconds=4,
        outputs=("Searching local notes", "Checking constraints", "Evidence ready"),
        parallel_group="director_fanout",
    ),
    DemoNode(
        id="build",
        label="Code Director",
        role="builder",
        phase="parallel",
        duration_seconds=7,
        outputs=(
            "Creating placeholder implementation",
            "Applying integration patch",
            "Publishing build artifact",
        ),
        parallel_group="director_fanout",
    ),
    DemoNode(
        id="art",
        label="Art Director",
        role="artist",
        phase="parallel",
        duration_seconds=5,
        outputs=("Sketching asset contract", "Streaming preview notes", "Assets ready"),
        parallel_group="director_fanout",
    ),
    DemoNode(
        id="integrate",
        label="Integrate Art + Code",
        role="builder",
        phase="serial",
        duration_seconds=3,
        outputs=("Replacing placeholder assets", "Integration complete"),
    ),
    DemoNode(
        id="review_stream",
        label="Streaming Test Review",
        role="verifier",
        phase="streaming",
        duration_seconds=6,
        outputs=(
            "test: unit checks started",
            "test: UI smoke opened",
            "test: parallel results collected",
            "test: schema status=passed",
            "test: final report streaming",
            "test: passed",
        ),
    ),
    DemoNode(
        id="human_gate",
        label="Human Gate Snapshot",
        role="current_director",
        phase="serial",
        duration_seconds=1,
        outputs=("QUESTION routed to current director",),
    ),
]

DEMO_EDGES = [
    ("decode", "plan"),
    ("plan", "research"),
    ("plan", "build"),
    ("plan", "art"),
    ("research", "integrate"),
    ("build", "integrate"),
    ("art", "integrate"),
    ("integrate", "review_stream"),
    ("review_stream", "human_gate"),
]

REAL_PARALLEL_GROUP = "real_matrix_workers"
REAL_THREAD_ASSIGNMENTS = {
    "parent_anchor": "019dd817-415a-7873-a4a7-8d4a1be55ced",
    "parent_commit": "019dd817-415a-7873-a4a7-8d4a1be55ced",
    "article_history": "019dd818-4d4f-7571-9df6-59d2d89fab51",
    "article_nutrition": "019dd818-49b1-7233-b369-426907f4f1b8",
    "article_culture": "019dd818-49dc-75d1-bb4b-09b256882226",
    "article_technology": "019dd818-4db8-7291-a057-e93bdaead4c8",
}
ACTIVE_EVENT_LOG = Path("artifacts") / "realtime_real_runs" / "active_events.jsonl"
DEFAULT_DIRECTOR_FLOW_DIRS = (
    Path.cwd() / "Docs" / "DirectorFlow",
    Path(r"D:\Codex_Sandbox\CatLaw\Docs\DirectorFlow"),
)
DIRECTOR_ROLE_ORDER = {
    "Coordinator": 0,
    "DesignDirector": 10,
    "ArtDirector": 20,
    "CodeDirector": 30,
    "TestDirector": 40,
    "DesignDirectorNew": 50,
    "ArtDirectorNew": 60,
    "CodeDirectorNew": 70,
    "TestDirectorNew": 80,
    "TestDirectorVisualNew": 90,
}
DIRECTOR_ROUTE_LOG_LIMIT = 8
DIRECTOR_ROUTE_STREAM_EVENT_LIMIT = 240
DIRECTOR_STREAM_FLUSH_CHARS = 180
DIRECTOR_STREAM_IMPORTANT_OUTPUT = re.compile(
    r"(UNITY_EXIT|ENTITLEMENT_EXIT|HAS_EDITOR|HAS_HEADLESS|LOG_PATH|LOG_EXISTS|"
    r"executeMethod|No licenses|return code 199|Exception|Error|Failed|failed|"
    r"passed|PASS|FAIL|blocked_|artifact|Success\. Updated|CatLaw)",
    re.IGNORECASE,
)
APPROVAL_REQUEST_METHODS = {
    "item/commandExecution/requestApproval",
    "item/fileChange/requestApproval",
    "item/permissions/requestApproval",
}


def build_real_workflow_plan(
    run_id: str | None = None,
    *,
    year: int | None = None,
    topic: str = "apple",
) -> dict[str, Any]:
    actual_run_id = run_id or f"COL_REAL_WORKFLOW_{time.strftime('%Y%m%d_%H%M%S')}"
    actual_year = year or time.localtime().tm_year
    worker_durations = {
        "article_history": 7,
        "article_nutrition": 8,
        "article_culture": 9,
        "article_technology": 10,
    }
    worker_labels = {
        "article_history": "History Writer",
        "article_nutrition": "Nutrition Writer",
        "article_culture": "Culture Writer",
        "article_technology": "Technology Writer",
    }
    nodes = [
        {
            "id": "parent_anchor",
            "label": "Article Parent Orchestrator Thread",
            "role": "orchestrator",
            "phase": "serial",
            "duration_seconds": 2,
            "outputs": [],
            "parallel_group": None,
            "thread_id": REAL_THREAD_ASSIGNMENTS["parent_anchor"],
        },
        *[
            {
                "id": node_id,
                "label": worker_labels[node_id],
                "role": "writer",
                "phase": "parallel",
                "duration_seconds": duration,
                "outputs": [],
                "parallel_group": REAL_PARALLEL_GROUP,
                "thread_id": REAL_THREAD_ASSIGNMENTS[node_id],
            }
            for node_id, duration in worker_durations.items()
        ],
        {
            "id": "parent_commit",
            "label": "Summarize Worker Articles",
            "role": "orchestrator",
            "phase": "serial",
            "duration_seconds": 3,
            "outputs": [],
            "parallel_group": None,
            "thread_id": REAL_THREAD_ASSIGNMENTS["parent_commit"],
        },
    ]
    edges = [
        {"from": "parent_anchor", "to": node_id}
        for node_id in worker_durations
    ] + [
        {"from": node_id, "to": "parent_commit"}
        for node_id in worker_durations
    ]
    return {
        "run_id": actual_run_id,
        "year": actual_year,
        "nodes": nodes,
        "edges": edges,
        "topic": topic,
        "workflow_kind": "article_summary",
    }


def iter_real_workflow_events(
    *,
    cwd: Path | str | None = None,
    year: int | None = None,
    timeout_seconds: int = 120,
):
    workspace = Path(cwd or Path.cwd())
    plan = build_real_workflow_plan(year=year)
    run_state: dict[str, Any] = {
        "run_id": plan["run_id"],
        "year": plan["year"],
        "workspace": str(workspace),
        "results": [],
        "docs_dir": str(workspace / "docs_subagent" / plan["run_id"]),
        "artifact_events": [],
    }
    docs_root = workspace / "docs_subagent" / plan["run_id"]
    inbox_dir = docs_root / "inbox"
    processed_dir = docs_root / "processed"
    inbox_dir.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    yield {
        "type": "run_started",
        "mode": "real",
        "run_id": plan["run_id"],
        "year": plan["year"],
        "workspace": str(workspace),
        "docs_dir": str(docs_root),
        "nodes": plan["nodes"],
        "edges": plan["edges"],
        "message": "Real Codex Desktop thread workflow started.",
    }

    parent_prompt = _real_parent_prompt(plan["run_id"], plan["year"])
    parent_result = yield from _run_real_turn_stream(
        node=_plan_node(plan, "parent_anchor"),
        prompt=parent_prompt,
        cwd=workspace,
        thread_mode="resume",
        thread_id=REAL_THREAD_ASSIGNMENTS["parent_anchor"],
        timeout_seconds=timeout_seconds,
    )
    run_state["parent_thread_id"] = parent_result.get("thread_id")
    run_state["results"].append(parent_result)
    if parent_result.get("status") == "failed" and not parent_result.get("thread_id"):
        yield from _finish_real_run(plan, run_state, status="failed")
        return

    yield {"type": "parallel_started", "group": REAL_PARALLEL_GROUP}
    worker_specs = _real_worker_specs(plan, parent_result.get("thread_id"))
    worker_results = yield from _run_parallel_real_turns(
        worker_specs,
        cwd=workspace,
        timeout_seconds=timeout_seconds,
    )
    run_state["results"].extend(worker_results)
    yield {"type": "parallel_completed", "group": REAL_PARALLEL_GROUP}

    article_paths: dict[str, str] = {}
    for result in worker_results:
        node_id = str(result.get("node_id"))
        article_text = _extract_article_text(str(result.get("text", "")))
        article_path = inbox_dir / f"{node_id}.md"
        article_path.write_text(_format_worker_markdown(node_id, plan, article_text), encoding="utf-8")
        article_paths[node_id] = str(article_path)
        event = {
            "type": "artifact_written",
            "node_id": node_id,
            "path": str(article_path),
            "message": f"worker markdown written: {article_path}",
        }
        run_state["artifact_events"].append(event)
        yield event

    articles: dict[str, str] = {}
    for node_id, path in article_paths.items():
        source_path = Path(path)
        text = source_path.read_text(encoding="utf-8")
        processed_path = processed_dir / source_path.name
        source_path.replace(processed_path)
        articles[node_id] = text
        event = {
            "type": "artifact_processed",
            "node_id": node_id,
            "path": str(processed_path),
            "message": f"coordinator read and moved markdown to processed: {processed_path}",
        }
        run_state["artifact_events"].append(event)
        yield event

    commit_prompt = _real_commit_prompt(plan, parent_result.get("thread_id"), articles)
    commit_result = yield from _run_real_turn_stream(
        node=_plan_node(plan, "parent_commit"),
        prompt=commit_prompt,
        cwd=workspace,
        thread_mode="resume",
        thread_id=REAL_THREAD_ASSIGNMENTS["parent_commit"],
        timeout_seconds=timeout_seconds,
    )
    run_state["results"].append(commit_result)
    summary_path = docs_root / "parent_summary.md"
    summary_path.write_text(
        _format_summary_markdown(plan, str(commit_result.get("text", "")), articles),
        encoding="utf-8",
    )
    event = {
        "type": "artifact_written",
        "node_id": "parent_commit",
        "path": str(summary_path),
        "message": f"parent summary markdown written: {summary_path}",
    }
    run_state["artifact_events"].append(event)
    yield event

    result_statuses = [str(result.get("status")) for result in run_state["results"]]
    if "blocked_quota" in result_statuses:
        status = "blocked_quota"
    elif "failed" in result_statuses:
        status = "failed"
    elif all(len(article) >= 80 for article in articles.values()) and str(
        commit_result.get("text", "")
    ).strip():
        status = "passed"
    else:
        status = "failed"
    yield from _finish_real_run(plan, run_state, status=status, parsed_values=articles)


def _run_parallel_real_turns(
    worker_specs: list[dict[str, Any]],
    *,
    cwd: Path,
    timeout_seconds: int,
):
    events: queue.Queue[dict[str, Any]] = queue.Queue()
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=len(worker_specs)) as pool:
        futures = [
            pool.submit(
                _run_real_turn,
                node=spec["node"],
                prompt=spec["prompt"],
                cwd=cwd,
                thread_mode=str(spec.get("thread_mode", "resume")),
                thread_id=spec.get("thread_id"),
                timeout_seconds=timeout_seconds,
                emit=events.put,
            )
            for spec in worker_specs
        ]
        pending = set(futures)
        while pending or not events.empty():
            try:
                yield events.get(timeout=0.25)
            except queue.Empty:
                pass
            for future in list(pending):
                if future.done():
                    pending.remove(future)
                    results.append(future.result())
    return sorted(results, key=lambda item: str(item.get("node_id", "")))


def _run_real_turn_stream(
    *,
    node: dict[str, Any],
    prompt: str,
    cwd: Path,
    thread_mode: str,
    thread_id: str | None = None,
    timeout_seconds: int,
):
    events: queue.Queue[dict[str, Any]] = queue.Queue()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(
            _run_real_turn,
            node=node,
            prompt=prompt,
            cwd=cwd,
            thread_mode=thread_mode,
            thread_id=thread_id,
            timeout_seconds=timeout_seconds,
            emit=events.put,
        )
        while not future.done() or not events.empty():
            try:
                yield events.get(timeout=0.25)
            except queue.Empty:
                pass
        return future.result()


def _run_real_turn(
    *,
    node: dict[str, Any],
    prompt: str,
    cwd: Path,
    thread_mode: str,
    thread_id: str | None,
    timeout_seconds: int,
    emit: Callable[[dict[str, Any]], None],
) -> dict[str, Any]:
    node_id = str(node["id"])
    started_at = time.time()
    sequence = 0
    observed: list[dict[str, Any]] = []
    assistant_text = ""
    turn_id: str | None = None
    actual_thread_id = thread_id
    quota_blocked = False
    quota_reported = False
    control_timeout_seconds = min(max(timeout_seconds, 60), 120)
    delta_buffer = ""

    def output(chunk: str, *, progress: float | None = None) -> None:
        nonlocal sequence
        sequence += 1
        emit(
            {
                "type": "node_output",
                "node_id": node_id,
                "sequence": sequence,
                "chunk": chunk,
                "progress": progress if progress is not None else min(0.95, 0.08 + sequence * 0.03),
                "parallel_group": node.get("parallel_group"),
            }
        )

    def flush_delta(*, force: bool = False) -> None:
        nonlocal delta_buffer
        text = " ".join(delta_buffer.split())
        if not text:
            delta_buffer = ""
            return
        should_flush = force or len(text) >= 160 or text.endswith((".", "!", "?", ":"))
        if should_flush:
            output(text, progress=None)
            delta_buffer = ""

    emit(
        {
            "type": "node_started",
            "node_id": node_id,
            "label": node["label"],
            "role": node["role"],
            "phase": node["phase"],
            "duration_seconds": node["duration_seconds"],
            "parallel_group": node.get("parallel_group"),
            "thread_mode": thread_mode,
        }
    )

    session: _CodexRpcSession | None = None
    try:
        output("starting codex app-server session", progress=0.03)
        session = _CodexRpcSession(DEFAULT_CODEX_EXE, DEFAULT_CODEX_HOME)
        session.request(
            "init",
            "initialize",
            {
                "clientInfo": {"name": "colang-realtime", "version": "0.3-real"},
                "capabilities": {"experimentalApi": True},
            },
            timeout_seconds=control_timeout_seconds,
            observed=observed,
        )
        if thread_mode == "create":
            response = session.request(
                "thread-start",
                "thread/start",
                {"cwd": str(cwd)},
                timeout_seconds=control_timeout_seconds,
                observed=observed,
            )
            thread = response.get("result", {}).get("thread", {})
            actual_thread_id = thread.get("id")
        elif thread_mode == "resume":
            if not actual_thread_id:
                raise ValueError("thread_mode=resume requires thread_id")
            session.request(
                "thread-resume",
                "thread/resume",
                {"threadId": actual_thread_id},
                timeout_seconds=control_timeout_seconds,
                observed=observed,
            )
        else:
            raise ValueError(f"unsupported thread_mode: {thread_mode}")

        if not actual_thread_id:
            raise RuntimeError("Codex app-server did not return a thread id")
        output(f"thread_id={actual_thread_id}", progress=0.12)
        response = session.request(
            "turn-start",
            "turn/start",
            {
                "threadId": actual_thread_id,
                "input": [{"type": "text", "text": prompt}],
            },
            timeout_seconds=control_timeout_seconds,
            observed=observed,
        )
        turn = response.get("result", {}).get("turn", {})
        turn_id = turn.get("id")
        output(f"turn_id={turn_id}", progress=0.18)

        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            payload = session._next_payload(deadline, observed)
            if not payload:
                continue
            if _payload_has_no_credits(payload):
                quota_blocked = True
                if not quota_reported:
                    quota_reported = True
                    output("blocked_quota: codex app-server reported no credits", progress=0.5)
            method = payload.get("method")
            params = payload.get("params", {})
            if method in APPROVAL_REQUEST_METHODS:
                _reject_approval_request(session, payload)
                output(f"rejected approval request: {method}", progress=0.5)
                continue
            if method == "item/agentMessage/delta":
                if turn_id is None or params.get("turnId") == turn_id:
                    delta = str(params.get("delta", ""))
                    assistant_text += delta
                    delta_buffer += delta
                    flush_delta()
            elif method == "item/completed":
                item = params.get("item", {})
                if item.get("type") == "agentMessage":
                    if turn_id is None or params.get("turnId") == turn_id:
                        assistant_text = str(item.get("text", assistant_text))
            elif method == "turn/completed":
                turn = params.get("turn", {})
                if turn_id is None or turn.get("id") == turn_id:
                    flush_delta(force=True)
                    completion_status = "passed"
                    if not assistant_text.strip():
                        completion_status = "blocked_quota" if quota_blocked else "empty_response"
                    output(f"turn/completed status={completion_status}", progress=1.0)
                    duration = round(time.time() - started_at, 3)
                    emit(
                        {
                            "type": "node_completed",
                            "node_id": node_id,
                            "status": completion_status,
                            "parallel_group": node.get("parallel_group"),
                            "thread_id": actual_thread_id,
                            "turn_id": turn_id,
                            "duration_seconds": duration,
                        }
                    )
                    return {
                        "node_id": node_id,
                        "status": completion_status,
                        "thread_id": actual_thread_id,
                        "turn_id": turn_id,
                        "text": assistant_text,
                        "quota_blocked": quota_blocked,
                        "duration_seconds": duration,
                        "raw_event_count": len(observed),
                    }
            elif method == "turn/aborted":
                raise RuntimeError("turn aborted")
        raise TimeoutError("timed out waiting for turn/completed")
    except Exception as exc:
        duration = round(time.time() - started_at, 3)
        output(f"error: {exc}", progress=1.0)
        emit(
            {
                "type": "node_completed",
                "node_id": node_id,
                "status": "failed",
                "parallel_group": node.get("parallel_group"),
                "thread_id": actual_thread_id,
                "turn_id": turn_id,
                "duration_seconds": duration,
            }
        )
        return {
            "node_id": node_id,
            "status": "failed",
            "thread_id": actual_thread_id,
            "turn_id": turn_id,
            "text": assistant_text,
            "error": str(exc),
            "duration_seconds": duration,
            "raw_event_count": len(observed),
        }
    finally:
        if session is not None:
            session.close()


def _reject_approval_request(session: _CodexRpcSession, payload: dict[str, Any]) -> None:
    request_id = payload.get("id")
    if request_id is None:
        return
    session._send({"jsonrpc": "2.0", "id": request_id, "result": {"decision": "reject"}})


def _payload_has_no_credits(payload: Any) -> bool:
    if isinstance(payload, dict):
        credits = payload.get("credits")
        if isinstance(credits, dict):
            has_credits = credits.get("has_credits")
            balance = str(credits.get("balance", ""))
            if has_credits is False or balance == "0":
                return True
        return any(_payload_has_no_credits(value) for value in payload.values())
    if isinstance(payload, list):
        return any(_payload_has_no_credits(value) for value in payload)
    return False


def _finish_real_run(
    plan: dict[str, Any],
    run_state: dict[str, Any],
    *,
    status: str,
    parsed_values: dict[str, int | None] | None = None,
):
    artifact_path = _write_real_run_artifact(plan, run_state, status, parsed_values or {})
    yield {
        "type": "run_completed",
        "mode": "real",
        "status": status,
        "run_id": plan["run_id"],
        "artifact_path": str(artifact_path),
        "parsed_values": parsed_values or {},
        "message": f"Real workflow {status}; artifact={artifact_path}",
    }


def _write_real_run_artifact(
    plan: dict[str, Any],
    run_state: dict[str, Any],
    status: str,
    parsed_values: dict[str, int | None],
) -> Path:
    artifact_dir = Path.cwd() / "artifacts" / "realtime_real_runs"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    artifact_path = artifact_dir / f"{plan['run_id']}.json"
    payload = {
        "status": status,
        "plan": plan,
        "run_state": run_state,
        "parsed_values": parsed_values,
    }
    artifact_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return artifact_path


def _format_worker_markdown(node_id: str, plan: dict[str, Any], article_text: str) -> str:
    return (
        f"# {node_id}\n\n"
        f"- Run: {plan['run_id']}\n"
        f"- Topic: {plan.get('topic', 'apple')}\n"
        f"- SourceThread: {REAL_THREAD_ASSIGNMENTS.get(node_id, '')}\n\n"
        f"{article_text.strip()}\n"
    )


def _format_summary_markdown(
    plan: dict[str, Any],
    summary_text: str,
    articles: dict[str, str],
) -> str:
    article_list = "\n".join(f"- {name}" for name in sorted(articles))
    return (
        "# Parent Summary\n\n"
        f"- Run: {plan['run_id']}\n"
        f"- Topic: {plan.get('topic', 'apple')}\n"
        f"- SourceThread: {REAL_THREAD_ASSIGNMENTS['parent_commit']}\n"
        f"- Inputs:\n{article_list}\n\n"
        f"{summary_text.strip()}\n"
    )


def reset_active_event_log() -> None:
    ACTIVE_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    ACTIVE_EVENT_LOG.write_text("", encoding="utf-8")


def record_active_event(event: dict[str, Any]) -> None:
    ACTIVE_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with ACTIVE_EVENT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_active_events() -> list[dict[str, Any]]:
    if not ACTIVE_EVENT_LOG.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in ACTIVE_EVENT_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def resolve_director_flow_dir(path: str | None = None) -> Path | None:
    candidates = [Path(path)] if path else list(DEFAULT_DIRECTOR_FLOW_DIRS)
    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue
    return None


def latest_director_flow_events(path: str | None = None) -> list[dict[str, Any]]:
    flow_dir = resolve_director_flow_dir(path)
    if not flow_dir:
        return [
            {
                "type": "run_completed",
                "mode": "directorflow",
                "status": "missing",
                "message": "No DirectorFlow directory found.",
            }
        ]

    roles = _load_director_roles(flow_dir)
    artifacts = _load_director_artifacts(flow_dir)
    for artifact in artifacts:
        for role_key in ("from", "to"):
            role = artifact.get(role_key)
            if role and role not in roles:
                roles[role] = {"role": role, "thread_id": "", "model": "", "reasoning": ""}
    route_streams = _load_director_route_streams(flow_dir, roles)
    for stream in route_streams:
        role = str(stream.get("role") or "")
        if role and role not in roles:
            roles[role] = {"role": role, "thread_id": "", "model": "", "reasoning": ""}

    nodes = [_director_node(role, meta) for role, meta in _ordered_roles(roles)]
    edges = _director_edges(artifacts, roles)
    latest_stamp = _latest_mtime(flow_dir)
    events: list[dict[str, Any]] = [
        {
            "type": "run_started",
            "mode": "directorflow",
            "run_id": f"directorflow-{latest_stamp}",
            "workspace": str(flow_dir.parent.parent),
            "docs_dir": str(flow_dir),
            "nodes": nodes,
            "edges": edges,
            "message": f"Loaded DirectorFlow ledger: {flow_dir}",
        }
    ]

    artifacts_by_sender: dict[str, list[dict[str, Any]]] = {}
    for artifact in artifacts:
        sender = str(artifact.get("from") or "Coordinator")
        artifacts_by_sender.setdefault(sender, []).append(artifact)
    streams_by_role: dict[str, list[dict[str, Any]]] = {}
    for stream in route_streams:
        streams_by_role.setdefault(str(stream.get("role") or "Coordinator"), []).append(stream)

    for node in nodes:
        role = str(node["role"])
        role_artifacts = artifacts_by_sender.get(role, [])
        role_streams = streams_by_role.get(role, [])
        events.append(
            {
                "type": "node_started",
                "node_id": node["id"],
                "label": node["label"],
                "role": role,
                "phase": node["phase"],
                "duration_seconds": node["duration_seconds"],
                "parallel_group": node.get("parallel_group"),
                "thread_mode": "directorflow",
                "thread_id": node.get("thread_id"),
            }
        )
        if node.get("thread_id"):
            events.append(_director_output(node, f"thread_id={node['thread_id']}", 1))
        if not role_artifacts and not role_streams:
            events.append(_director_output(node, "No recent DirectorFlow artifacts for this role.", 2))
            continue
        sequence = 2
        for artifact in role_artifacts[:8]:
            chunk = (
                f"{artifact.get('from')} -> {artifact.get('to')}\n"
                f"Status: {artifact.get('status')}\n"
                f"LoopType: {artifact.get('loop_type')}\n"
                f"Subject: {artifact.get('subject')}\n"
                f"Path: {artifact.get('path')}"
            )
            events.append(_director_output(node, chunk, sequence))
            sequence += 1
            events.append(
                {
                    "type": "artifact_written",
                    "node_id": node["id"],
                    "path": artifact.get("path"),
                    "message": f"{artifact.get('status')}: {artifact.get('subject')}",
                }
            )
        for stream in role_streams:
            events.append(
                _director_output(
                    node,
                    str(stream.get("chunk") or ""),
                    sequence,
                    event_id=str(stream.get("event_id") or ""),
                    source="route_log",
                )
            )
            sequence += 1
        latest_status = str(role_artifacts[0].get("status") or "").lower() if role_artifacts else ""
        if latest_status and _director_terminal_status(latest_status):
            events.append(
                {
                    "type": "node_completed",
                    "node_id": node["id"],
                    "status": _director_public_status(latest_status),
                    "thread_id": node.get("thread_id"),
                }
            )

    run_status = _director_run_status(artifacts)
    events.append(
        {
            "type": "run_completed",
            "mode": "directorflow",
            "status": run_status,
            "run_id": f"directorflow-{latest_stamp}",
            "message": f"DirectorFlow status: {run_status}",
        }
    )
    return events


def _load_director_roles(flow_dir: Path) -> dict[str, dict[str, str]]:
    roles: dict[str, dict[str, str]] = {
        "Coordinator": {"role": "Coordinator", "thread_id": "local-coordinator", "model": "", "reasoning": ""},
    }
    registry_files = sorted(
        flow_dir.glob("Coordinator_AgentRegistry_*.md"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    if not registry_files:
        return roles
    text = registry_files[0].read_text(encoding="utf-8", errors="replace")
    for line in text.splitlines():
        if not line.startswith("|") or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells or cells[0] in {"Role", ""}:
            continue
        role = cells[0]
        codes = re.findall(r"`([^`]+)`", line)
        thread_id = next((code for code in codes if re.fullmatch(r"[0-9a-f-]{36}", code)), "")
        if not thread_id:
            continue
        model = next((code for code in codes if code.startswith("gpt-")), "")
        reasoning = next((code for code in codes if code in {"low", "medium", "high", "xhigh"}), "")
        roles[role] = {
            "role": role,
            "thread_id": thread_id,
            "model": model,
            "reasoning": reasoning,
        }
    return roles


def _load_director_artifacts(flow_dir: Path) -> list[dict[str, Any]]:
    paths = sorted(flow_dir.glob("*.md"), key=lambda item: item.stat().st_mtime, reverse=True)
    artifacts: list[dict[str, Any]] = []
    for path in paths[:80]:
        if path.name.startswith("Coordinator_AgentRegistry_"):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        artifacts.append(
            {
                "path": str(path),
                "mtime": path.stat().st_mtime,
                "from": _read_markdown_field(text, "From") or _filename_role(path.name, 0),
                "to": _read_markdown_field(text, "To") or _filename_role(path.name, 2),
                "subject": _read_markdown_field(text, "Subject") or path.stem,
                "status": _read_markdown_field(text, "Status") or "unknown",
                "loop_type": _read_markdown_field(text, "LoopType") or "unknown",
                "supersedes": _read_markdown_field(text, "Supersedes") or "",
            }
        )
    return artifacts


def _load_director_route_streams(
    flow_dir: Path,
    roles: dict[str, dict[str, str]],
) -> list[dict[str, Any]]:
    thread_to_role = {
        str(meta.get("thread_id")): role
        for role, meta in roles.items()
        if meta.get("thread_id")
    }
    streams: list[dict[str, Any]] = []
    paths = sorted(
        flow_dir.glob("Coordinator_RouteLog_*.jsonl"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )
    for path in paths[:DIRECTOR_ROUTE_LOG_LIMIT]:
        log_mtime = path.stat().st_mtime
        for stream in _parse_director_route_log(path, thread_to_role):
            stream["log_mtime"] = log_mtime
            streams.append(stream)
    streams.sort(key=lambda item: (float(item.get("log_mtime", 0)), int(item.get("line", 0))))
    return streams


def _parse_director_route_log(
    path: Path,
    thread_to_role: dict[str, str],
) -> list[dict[str, Any]]:
    role = _infer_route_role(path, "", thread_to_role)
    events: list[dict[str, Any]] = []
    agent_buffers: dict[str, str] = {}
    command_buffers: dict[str, str] = {}

    def add(line_number: int, ts: str, chunk: str) -> None:
        cleaned = _compact_stream_chunk(chunk)
        if not cleaned:
            return
        prefix = f"[{ts}] " if ts else ""
        events.append(
            {
                "role": role or "Coordinator",
                "chunk": prefix + cleaned,
                "line": line_number,
                "log_path": str(path),
                "event_id": f"{path.name}:{line_number}:{len(events)}",
            }
        )
        if len(events) > DIRECTOR_ROUTE_STREAM_EVENT_LIMIT:
            del events[: len(events) - DIRECTOR_ROUTE_STREAM_EVENT_LIMIT]

    def flush_agent(line_number: int, ts: str, item_id: str, *, force: bool = False) -> None:
        text = agent_buffers.get(item_id, "")
        compact = " ".join(text.split())
        if not compact:
            agent_buffers[item_id] = ""
            return
        if force or len(compact) >= DIRECTOR_STREAM_FLUSH_CHARS or compact.endswith(("。", ".", "!", "?", "：", ":")):
            add(line_number, ts, f"agent> {compact}")
            agent_buffers[item_id] = ""

    def flush_command_output(line_number: int, ts: str, item_id: str, *, force: bool = False) -> None:
        text = command_buffers.get(item_id, "")
        if not text:
            return
        lines = text.splitlines(keepends=True)
        keep_tail = ""
        complete_lines: list[str] = []
        for line in lines:
            if line.endswith(("\n", "\r")):
                complete_lines.append(line.strip())
            else:
                keep_tail = line
        important = [line for line in complete_lines if DIRECTOR_STREAM_IMPORTANT_OUTPUT.search(line)]
        if important:
            add(line_number, ts, "cmd output> " + " | ".join(important[-4:]))
        elif force and text.strip():
            add(line_number, ts, "cmd output> " + text.strip())
            keep_tail = ""
        command_buffers[item_id] = keep_tail

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return events

    for line_number, line in enumerate(lines, 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        ts = str(record.get("ts") or "")
        event_type = str(record.get("event") or "")
        if event_type == "route_start":
            role = _infer_route_role(path, str(record.get("thread_id") or ""), thread_to_role)
            add(
                line_number,
                ts,
                "route started: "
                f"model={record.get('model', '')} effort={record.get('effort', '')} "
                f"thread={record.get('thread_id', '')} expected={record.get('expected_artifact', '')}",
            )
            continue
        if event_type == "approval_auto_accept":
            add(line_number, ts, f"approval accepted: {record.get('method', '')}")
            continue
        if event_type == "artifact_seen":
            add(line_number, ts, f"artifact seen: {record.get('label', '')} {record.get('path', '')}")
            continue
        if event_type == "route_end":
            add(
                line_number,
                ts,
                f"route ended: completed={record.get('turn_completed')} final={record.get('final_status')}",
            )
            continue
        if event_type == "route_timeout_or_exit":
            add(line_number, ts, f"route timeout/exit: returncode={record.get('returncode')}")
            continue
        if event_type == "stderr" and "stream disconnected" in str(record.get("text") or ""):
            add(line_number, ts, "transport stderr: " + str(record.get("text") or ""))
            continue
        if event_type != "notification":
            continue

        method = str(record.get("method") or "")
        params = record.get("params") or {}
        thread_id = str(params.get("threadId") or "")
        if thread_id and thread_id in thread_to_role:
            role = thread_to_role[thread_id]
        item = params.get("item") or {}
        item_id = str(item.get("id") or params.get("itemId") or "item")

        if method == "turn/started":
            turn = params.get("turn") or {}
            add(line_number, ts, f"turn started: {turn.get('id', '')}")
        elif method == "turn/completed":
            turn = params.get("turn") or {}
            add(
                line_number,
                ts,
                f"turn completed: status={turn.get('status', '')} durationMs={turn.get('durationMs', '')}",
            )
        elif method == "error":
            error = params.get("error") or {}
            add(line_number, ts, f"transport error: {error.get('message', '')} {error.get('additionalDetails', '')}")
        elif method == "warning":
            add(line_number, ts, f"transport warning: {params.get('message', '')}")
        elif method == "item/started":
            item_type = str(item.get("type") or "")
            if item_type == "commandExecution":
                add(line_number, ts, "cmd started: " + _short_command(str(item.get("command") or "")))
            elif item_type == "agentMessage":
                add(line_number, ts, "agent message started")
            elif item_type not in {"reasoning", "userMessage"}:
                add(line_number, ts, f"item started: {item_type}")
        elif method == "item/agentMessage/delta":
            delta = str(params.get("delta") or "")
            agent_buffers[item_id] = agent_buffers.get(item_id, "") + delta
            flush_agent(line_number, ts, item_id)
        elif method == "item/commandExecution/outputDelta":
            delta = str(params.get("delta") or "")
            command_buffers[item_id] = command_buffers.get(item_id, "") + delta
            flush_command_output(line_number, ts, item_id)
        elif method == "item/fileChange/outputDelta":
            delta = str(params.get("delta") or "")
            if delta.strip():
                add(line_number, ts, "file change> " + delta.strip())
        elif method == "item/completed":
            item_type = str(item.get("type") or "")
            if item_type == "agentMessage":
                flush_agent(line_number, ts, item_id, force=True)
            elif item_type == "commandExecution":
                flush_command_output(line_number, ts, item_id, force=True)
                add(
                    line_number,
                    ts,
                    "cmd completed: "
                    f"status={item.get('status', '')} exit={item.get('exitCode', '')} "
                    f"durationMs={item.get('durationMs', '')} "
                    f"{_short_command(str(item.get('command') or ''))}",
                )

    for item_id in list(agent_buffers):
        flush_agent(len(lines), "", item_id, force=True)
    for item_id in list(command_buffers):
        flush_command_output(len(lines), "", item_id, force=True)
    return events


def _infer_route_role(path: Path, thread_id: str, thread_to_role: dict[str, str]) -> str:
    if thread_id and thread_id in thread_to_role:
        return thread_to_role[thread_id]
    lower = path.name.lower()
    for role in sorted(DIRECTOR_ROLE_ORDER, key=len, reverse=True):
        if role.lower() in lower or _director_node_id(role) in lower:
            return role
    return "Coordinator"


def _compact_stream_chunk(chunk: str, *, limit: int = 900) -> str:
    text = " ".join(str(chunk).replace("\r", "\n").split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _short_command(command: str, *, limit: int = 220) -> str:
    text = " ".join(command.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def _read_markdown_field(text: str, field: str) -> str:
    match = re.search(rf"(?ms)^# {re.escape(field)}\s*\n(.*?)(?=\n# |\Z)", text)
    if not match:
        return ""
    for line in match.group(1).splitlines():
        cleaned = line.strip().strip("`")
        if cleaned:
            return cleaned
    return ""


def _filename_role(name: str, index: int) -> str:
    parts = name.split("_")
    if len(parts) > index:
        return parts[index]
    return ""


def _ordered_roles(roles: dict[str, dict[str, str]]) -> list[tuple[str, dict[str, str]]]:
    return sorted(
        roles.items(),
        key=lambda item: (DIRECTOR_ROLE_ORDER.get(item[0], 999), item[0].lower()),
    )


def _director_node(role: str, meta: dict[str, str]) -> dict[str, Any]:
    return {
        "id": _director_node_id(role),
        "label": role,
        "role": role,
        "phase": "director",
        "duration_seconds": 1,
        "outputs": [],
        "parallel_group": "catlaw_directors" if role != "Coordinator" else None,
        "thread_id": meta.get("thread_id", ""),
        "model": meta.get("model", ""),
        "reasoning": meta.get("reasoning", ""),
    }


def _director_node_id(role: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", role).strip("_").lower()
    return slug or "unknown"


def _director_edges(artifacts: list[dict[str, Any]], roles: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    edge_keys: set[tuple[str, str]] = set()
    for artifact in artifacts:
        source = str(artifact.get("from") or "")
        target = str(artifact.get("to") or "")
        if source and target and source in roles and target in roles and source != target:
            edge_keys.add((_director_node_id(source), _director_node_id(target)))
    for source, target in [
        ("Coordinator", "DesignDirector"),
        ("Coordinator", "CodeDirector"),
        ("Coordinator", "TestDirector"),
        ("DesignDirector", "ArtDirector"),
        ("DesignDirector", "CodeDirector"),
        ("ArtDirector", "CodeDirector"),
        ("CodeDirector", "TestDirector"),
        ("TestDirector", "CodeDirector"),
        ("CodeDirector", "DesignDirector"),
        ("DesignDirector", "Coordinator"),
    ]:
        if source in roles and target in roles:
            edge_keys.add((_director_node_id(source), _director_node_id(target)))
    return [{"from": source, "to": target} for source, target in sorted(edge_keys)]


def _director_output(
    node: dict[str, Any],
    chunk: str,
    sequence: int,
    *,
    event_id: str = "",
    source: str = "",
) -> dict[str, Any]:
    event = {
        "type": "node_output",
        "node_id": node["id"],
        "sequence": sequence,
        "chunk": chunk,
        "progress": min(0.95, 0.15 + sequence * 0.08),
        "parallel_group": node.get("parallel_group"),
        "thread_id": node.get("thread_id"),
    }
    if event_id:
        event["event_id"] = event_id
    if source:
        event["source"] = source
    return event


def _director_terminal_status(status: str) -> bool:
    return any(token in status for token in ("passed", "failed", "blocked", "closed"))


def _director_public_status(status: str) -> str:
    if "passed" in status or "closed" in status:
        return "passed"
    return status or "failed"


def _director_run_status(artifacts: list[dict[str, Any]]) -> str:
    statuses = [str(artifact.get("status") or "").lower() for artifact in artifacts[:20]]
    if any("blocked_env" in status for status in statuses):
        return "blocked_env"
    if any("blocked_quota" in status for status in statuses):
        return "blocked_quota"
    if any("failed" in status for status in statuses):
        return "failed"
    if any("active" in status or "pending" in status or "ready" in status for status in statuses):
        return "active"
    if any("passed" in status or "closed" in status for status in statuses):
        return "passed"
    return "unknown"


def _latest_mtime(path: Path) -> int:
    try:
        return int(max((item.stat().st_mtime for item in path.glob("*.md")), default=time.time()))
    except OSError:
        return int(time.time())


def load_latest_real_run() -> dict[str, Any] | None:
    artifact_dir = Path.cwd() / "artifacts" / "realtime_real_runs"
    if not artifact_dir.exists():
        return None
    files = sorted(
        artifact_dir.glob("COL_REAL_WORKFLOW_*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not files:
        return None
    try:
        payload = json.loads(files[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    payload["artifact_path"] = str(files[0])
    return payload


def latest_real_run_events() -> list[dict[str, Any]]:
    payload = load_latest_real_run()
    if not payload:
        return [
            {
                "type": "run_completed",
                "mode": "latest",
                "status": "missing",
                "message": "No realtime real run artifact found.",
            }
        ]
    plan = payload.get("plan", {})
    run_state = payload.get("run_state", {})
    events: list[dict[str, Any]] = [
        {
            "type": "run_started",
            "mode": "latest",
            "run_id": plan.get("run_id"),
            "year": plan.get("year"),
            "workspace": run_state.get("workspace"),
            "nodes": plan.get("nodes", []),
            "edges": plan.get("edges", []),
            "message": "Loaded latest real workflow artifact.",
        }
    ]
    for result in run_state.get("results", []):
        node_id = result.get("node_id")
        if not node_id:
            continue
        events.append(
            {
                "type": "node_started",
                "node_id": node_id,
                "label": node_id,
                "role": "",
                "phase": "",
                "duration_seconds": result.get("duration_seconds", 0),
                "parallel_group": _latest_node_group(plan, str(node_id)),
                "thread_mode": "loaded",
            }
        )
        thread_id = result.get("thread_id")
        turn_id = result.get("turn_id")
        if thread_id:
            events.append(_latest_output_event(str(node_id), f"thread_id={thread_id}", 1, plan))
        if turn_id:
            events.append(_latest_output_event(str(node_id), f"turn_id={turn_id}", 2, plan))
        text = str(result.get("text") or "").strip()
        if text:
            events.append(_latest_output_event(str(node_id), _compact_chunk(text), 3, plan))
        if result.get("error"):
            events.append(_latest_output_event(str(node_id), f"error: {result['error']}", 4, plan))
        events.append(
            {
                "type": "node_completed",
                "node_id": node_id,
                "status": result.get("status", "unknown"),
                "parallel_group": _latest_node_group(plan, str(node_id)),
                "thread_id": thread_id,
                "turn_id": turn_id,
                "duration_seconds": result.get("duration_seconds", 0),
            }
        )
    events.append(
        {
            "type": "run_completed",
            "mode": "latest",
            "status": payload.get("status", "unknown"),
            "run_id": plan.get("run_id"),
            "artifact_path": payload.get("artifact_path"),
            "parsed_values": payload.get("parsed_values", {}),
            "message": f"Loaded latest artifact: {payload.get('artifact_path')}",
        }
    )
    return events


def _latest_node_group(plan: dict[str, Any], node_id: str) -> str | None:
    for node in plan.get("nodes", []):
        if node.get("id") == node_id:
            return node.get("parallel_group")
    return None


def _latest_output_event(
    node_id: str,
    chunk: str,
    sequence: int,
    plan: dict[str, Any],
) -> dict[str, Any]:
    return {
        "type": "node_output",
        "node_id": node_id,
        "sequence": sequence,
        "chunk": chunk,
        "progress": min(1.0, sequence * 0.25),
        "parallel_group": _latest_node_group(plan, node_id),
    }


def _plan_node(plan: dict[str, Any], node_id: str) -> dict[str, Any]:
    for node in plan["nodes"]:
        if node["id"] == node_id:
            return node
    raise KeyError(node_id)


def _real_parent_prompt(run_id: str, year: int) -> str:
    return (
        "COL_REAL_WORKFLOW_PARENT\n"
        f"run_id={run_id}\n"
        f"year={year}\n"
        "topic=apple\n"
        "This is a new independent run in this existing thread. Ignore prior workflow content except the safety boundary.\n"
        "You are the parent orchestrator for a real COL article workflow smoke test.\n"
        "Safety boundary: do not use tools, do not run commands, do not read files, "
        "do not write files, and do not modify this repository.\n"
        "Reply with exactly one line:\n"
        f"COL_REAL_PARENT_READY run_id={run_id} topic=apple year={year}"
    )


def _real_worker_specs(plan: dict[str, Any], parent_thread_id: str | None) -> list[dict[str, Any]]:
    assignments = {
        "article_history": (
            "history",
            "Write a concise article about apples in human history: domestication, trade, orchards, and why apples became a durable everyday fruit.",
        ),
        "article_nutrition": (
            "nutrition",
            "Write a concise article about apples as food: texture, fiber, sweetness, storage, and reasonable nutrition claims without exaggeration.",
        ),
        "article_culture": (
            "culture",
            "Write a concise article about apples in culture: stories, symbols, education, technology names, and everyday rituals.",
        ),
        "article_technology": (
            "technology",
            "Write a concise article about apples and technology: sorting, storage, supply chains, breeding, sensors, and modern agriculture.",
        ),
    }
    specs = []
    for node_id, (angle, assignment) in assignments.items():
        prompt = (
            "COL_REAL_WORKFLOW_WORKER\n"
            f"run_id={plan['run_id']}\n"
            f"parent_thread_id={parent_thread_id}\n"
            f"article_id={node_id}\n"
            f"angle={angle}\n"
            f"topic={plan.get('topic', 'apple')}\n"
            "This is a new independent run in this existing writer thread. Ignore prior article drafts and write fresh text.\n"
            "Safety boundary: do not use tools, do not run commands, do not read files, "
            "do not write files, and do not modify this repository.\n"
            "Write visibly and concretely so the realtime dashboard shows the writing process.\n"
            "Return plain text only. Use this exact header on the first line:\n"
            f"ARTICLE {node_id}\n"
            f"{assignment}\n"
            "Length: 180 to 260 English words. End with one sentence beginning 'Key point:'."
        )
        specs.append(
            {
                "node": _plan_node(plan, node_id),
                "prompt": prompt,
                "thread_mode": "resume",
                "thread_id": REAL_THREAD_ASSIGNMENTS[node_id],
            }
        )
    return specs


def _real_commit_prompt(
    plan: dict[str, Any],
    parent_thread_id: str | None,
    articles: dict[str, str],
) -> str:
    return (
        "COL_REAL_WORKFLOW_COMMIT\n"
        f"run_id={plan['run_id']}\n"
        f"parent_thread_id={parent_thread_id}\n"
        f"topic={plan.get('topic', 'apple')}\n"
        f"worker_articles={json.dumps(articles, ensure_ascii=False, sort_keys=True)}\n"
        "This is a new independent summary turn in this existing parent thread. Use only worker_articles for the summary.\n"
        "Safety boundary: do not use tools, do not run commands, do not read files, "
        "do not write files, and do not modify this repository.\n"
        "Write a synthesis in plain text. Summarize the four worker articles about apples, "
        "name the shared themes, and end with 'SUMMARY_STATUS: passed'. "
        "Length: 160 to 230 English words."
    )


def _extract_article_text(text: str) -> str:
    return " ".join(text.split())


def _compact_chunk(text: str) -> str:
    return " ".join(text.split())[:240]


def iter_demo_events(speed: float = 1.0):
    started_at = time.time()
    yield {
        "type": "run_started",
        "run_id": f"demo-{int(started_at)}",
        "nodes": [node.to_public() for node in DEMO_NODES],
        "edges": [{"from": src, "to": dst} for src, dst in DEMO_EDGES],
        "message": "Realtime COL orchestration demo started.",
    }

    serial_prefix = [node for node in DEMO_NODES if node.id in {"decode", "plan"}]
    for node in serial_prefix:
        yield from _run_serial_node(node, speed)

    parallel_nodes = [node for node in DEMO_NODES if node.parallel_group == "director_fanout"]
    yield {"type": "parallel_started", "group": "director_fanout"}
    yield from _run_parallel_nodes(parallel_nodes, speed)
    yield {"type": "parallel_completed", "group": "director_fanout"}

    serial_suffix = [
        node for node in DEMO_NODES if node.id in {"integrate", "review_stream", "human_gate"}
    ]
    for node in serial_suffix:
        yield from _run_serial_node(node, speed)

    yield {
        "type": "run_completed",
        "status": "passed",
        "duration_seconds": sum(node.duration_seconds for node in serial_prefix)
        + max(node.duration_seconds for node in parallel_nodes)
        + sum(node.duration_seconds for node in serial_suffix),
        "message": "All realtime demo nodes completed.",
    }


def _run_serial_node(node: DemoNode, speed: float):
    yield _node_started(node)
    for tick in range(1, node.duration_seconds + 1):
        _sleep_tick(speed)
        yield _node_output(node, tick)
    yield _node_completed(node)


def _run_parallel_nodes(nodes: list[DemoNode], speed: float):
    for node in nodes:
        yield _node_started(node)
    max_duration = max(node.duration_seconds for node in nodes)
    completed: set[str] = set()
    for tick in range(1, max_duration + 1):
        _sleep_tick(speed)
        for node in nodes:
            if tick <= node.duration_seconds:
                yield _node_output(node, tick)
            if tick == node.duration_seconds and node.id not in completed:
                completed.add(node.id)
                yield _node_completed(node)


def _node_started(node: DemoNode) -> dict[str, Any]:
    return {
        "type": "node_started",
        "node_id": node.id,
        "label": node.label,
        "role": node.role,
        "phase": node.phase,
        "duration_seconds": node.duration_seconds,
        "parallel_group": node.parallel_group,
    }


def _node_output(node: DemoNode, tick: int) -> dict[str, Any]:
    output = node.outputs[min(tick - 1, len(node.outputs) - 1)]
    return {
        "type": "node_output",
        "node_id": node.id,
        "sequence": tick,
        "chunk": output,
        "progress": round(tick / node.duration_seconds, 3),
        "parallel_group": node.parallel_group,
    }


def _node_completed(node: DemoNode) -> dict[str, Any]:
    return {
        "type": "node_completed",
        "node_id": node.id,
        "status": "passed",
        "parallel_group": node.parallel_group,
    }


def _sleep_tick(speed: float) -> None:
    if speed > 0:
        time.sleep(speed)


def render_dashboard_html() -> str:
    return DASHBOARD_HTML


def run_server(
    host: str = "127.0.0.1",
    port: int = 8765,
    speed: float = 1.0,
    *,
    scan_count: int = 12,
) -> None:
    listen_port, port_report = choose_listen_port(
        host,
        preferred_port=port,
        scan_count=scan_count,
    )
    handler = _make_handler(speed)
    server = RealtimeHTTPServer((host, listen_port), handler)
    print(
        "COL realtime occupied ports: "
        + (", ".join(map(str, port_report["occupied_ports"])) or "none"),
        flush=True,
    )
    print(
        "COL realtime available URLs: " + ", ".join(port_report["available_urls"]),
        flush=True,
    )
    print(f"COL realtime listening: http://{host}:{listen_port}/", flush=True)
    server.serve_forever()


def _make_handler(default_speed: float):
    class RealtimeHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def do_GET(self) -> None:
            parsed = urlparse(self.path)
            if parsed.path == "/":
                _write_bytes(
                    self,
                    render_dashboard_html().encode("utf-8"),
                    "text/html; charset=utf-8",
                )
                return
            if parsed.path == "/health":
                _write_json(self, {"ok": True, "modes": ["demo", "real", "directorflow"]})
                return
            if parsed.path == "/latest":
                _write_json(self, load_latest_real_run() or {"status": "missing"})
                return
            if parsed.path == "/latest-events":
                params = parse_qs(parsed.query)
                mode = params.get("mode", ["real"])[0]
                events = latest_director_flow_events() if mode == "directorflow" else latest_real_run_events()
                _write_json(self, {"events": events})
                return
            if parsed.path == "/active-events":
                params = parse_qs(parsed.query)
                mode = params.get("mode", ["real"])[0]
                events = latest_director_flow_events() if mode == "directorflow" else load_active_events()
                _write_json(self, {"events": events})
                return
            if parsed.path == "/events":
                params = parse_qs(parsed.query)
                speed = float(params.get("speed", [default_speed])[0])
                mode = params.get("mode", ["demo"])[0]
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "close")
                self.end_headers()
                if mode == "real":
                    events = iter_real_workflow_events(cwd=Path.cwd())
                elif mode == "directorflow":
                    events = iter(latest_director_flow_events())
                else:
                    events = iter_demo_events(speed=speed)
                for event in events:
                    if event.get("type") == "run_started":
                        reset_active_event_log()
                    record_active_event(event)
                    payload = json.dumps(event, ensure_ascii=False)
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                    self.wfile.flush()
                self.close_connection = True
                return
            self.send_error(HTTPStatus.NOT_FOUND)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return RealtimeHandler


def _write_json(handler: BaseHTTPRequestHandler, payload: dict[str, Any]) -> None:
    _write_bytes(
        handler,
        json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        "application/json; charset=utf-8",
    )


def _write_bytes(handler: BaseHTTPRequestHandler, body: bytes, content_type: str) -> None:
    handler.send_response(HTTPStatus.OK)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Serve the COL realtime dashboard")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--scan-count", type=int, default=12)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args(argv)
    run_server(args.host, args.port, args.speed, scan_count=args.scan_count)
    return 0


DASHBOARD_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>COL Realtime Orchestration</title>
  <style>
    :root {
      --bg: #f5f7fa;
      --panel: #ffffff;
      --line: #d8dee8;
      --ink: #1f2933;
      --muted: #657386;
      --blue: #2f6fbd;
      --green: #20865f;
      --amber: #a05e00;
      --red: #a33c3c;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: "Segoe UI", Arial, sans-serif;
      letter-spacing: 0;
    }
    header {
      height: 68px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      border-bottom: 1px solid var(--line);
      background: var(--panel);
    }
    h1 { margin: 0; font-size: 20px; font-weight: 650; }
    main {
      display: grid;
      grid-template-columns: minmax(760px, 1fr) 460px;
      gap: 16px;
      padding: 16px;
    }
    section {
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      min-width: 0;
    }
    .toolbar {
      display: flex;
      align-items: center;
      gap: 8px;
      color: var(--muted);
      font-size: 13px;
    }
    button, select {
      height: 34px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #fff;
      color: var(--ink);
      padding: 0 10px;
      font: inherit;
    }
    button { cursor: pointer; }
    .section-head {
      height: 46px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 14px;
      border-bottom: 1px solid var(--line);
    }
    .section-head h2 { margin: 0; font-size: 15px; }
    .node-grid {
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      padding: 14px;
      max-height: calc(100vh - 150px);
      overflow: auto;
    }
    .node {
      min-height: 168px;
      border: 1px solid var(--line);
      border-radius: 8px;
      display: grid;
      grid-template-columns: 240px minmax(0, 1fr);
      grid-template-rows: minmax(154px, auto) 8px;
      overflow: hidden;
      background: #fcfdff;
    }
    .node-inspect {
      height: 28px;
      margin: 10px 12px 0;
      padding: 0 8px;
      font-size: 12px;
    }
    .node.running { border-color: var(--blue); box-shadow: inset 0 3px 0 var(--blue); }
    .node.done { border-color: #9fd2bb; box-shadow: inset 0 3px 0 var(--green); }
    .node.blocked { border-color: #d6a74d; box-shadow: inset 0 3px 0 var(--amber); }
    .node.failed { border-color: #d79a9a; box-shadow: inset 0 3px 0 var(--red); }
    .node-title {
      padding: 12px 12px 6px;
      font-size: 15px;
      font-weight: 650;
      min-height: 48px;
      overflow-wrap: anywhere;
    }
    .node-meta {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      padding: 0 12px 12px;
      color: var(--muted);
      font-size: 12px;
      align-content: flex-start;
    }
    .pill {
      padding: 2px 6px;
      border-radius: 4px;
      background: #eef2f7;
      white-space: nowrap;
    }
    .node-output {
      grid-row: 1;
      grid-column: 2;
      border-left: 1px solid #eef1f5;
      padding: 10px 12px;
      overflow: auto;
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 13px;
      line-height: 1.55;
      color: #263241;
      min-height: 154px;
      max-height: 260px;
      white-space: pre-wrap;
    }
    .progress {
      grid-column: 1 / -1;
      grid-row: 2;
      height: 8px;
      background: #edf1f5;
    }
    .bar {
      height: 100%;
      width: 0;
      background: var(--blue);
      transition: width 160ms linear;
    }
    .node.done .bar { background: var(--green); }
    .node.blocked .bar { background: var(--amber); }
    .node.failed .bar { background: var(--red); }
    .side {
      display: grid;
      grid-template-rows: 30vh 28vh minmax(280px, 1fr);
      gap: 16px;
      max-height: calc(100vh - 100px);
    }
    .flow-graph {
      padding: 0;
      overflow: hidden;
      height: 100%;
      font-size: 13px;
    }
    .graph-toolbar {
      height: 38px;
      display: flex;
      align-items: center;
      gap: 6px;
      padding: 6px 8px;
      border-bottom: 1px solid #eef1f5;
      background: #fbfcfe;
    }
    .graph-toolbar button {
      height: 26px;
      padding: 0 8px;
      font-size: 12px;
    }
    .graph-viewport {
      position: relative;
      height: calc(100% - 38px);
      min-height: 210px;
      overflow: hidden;
      cursor: grab;
      background:
        linear-gradient(#f6f8fb 1px, transparent 1px),
        linear-gradient(90deg, #f6f8fb 1px, transparent 1px);
      background-size: 24px 24px;
    }
    .graph-viewport.dragging { cursor: grabbing; }
    .graph-canvas {
      position: relative;
      width: 820px;
      height: 320px;
      transform-origin: 0 0;
    }
    .graph-svg {
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      overflow: visible;
      pointer-events: none;
    }
    .graph-edge {
      stroke: #aeb8c6;
      stroke-width: 1.5;
      fill: none;
    }
    .graph-edge.loop {
      stroke: var(--amber);
      stroke-dasharray: 5 4;
    }
    .graph-node {
      position: absolute;
      display: grid;
      grid-template-columns: 16px minmax(0, 1fr) auto;
      gap: 8px;
      align-items: center;
      width: 240px;
      padding: 7px 0;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      padding: 8px 10px;
      box-shadow: 0 5px 16px rgba(31, 41, 51, 0.06);
      cursor: pointer;
    }
    .graph-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: #c8d0db;
    }
    .graph-node.running .graph-dot { background: var(--blue); }
    .graph-node.done .graph-dot { background: var(--green); }
    .graph-node.blocked .graph-dot { background: var(--amber); }
    .graph-node.failed .graph-dot { background: var(--red); }
    .graph-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-weight: 650;
    }
    .graph-status { color: var(--muted); font-size: 12px; }
    .timeline, .event-log {
      padding: 12px 14px;
      overflow: auto;
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 12px;
      line-height: 1.55;
      white-space: pre-wrap;
      height: 100%;
    }
    .status-dot {
      width: 10px;
      height: 10px;
      border-radius: 50%;
      background: var(--amber);
      display: inline-block;
      margin-right: 6px;
    }
    .status-dot.live { background: var(--green); }
    .status-dot.done { background: var(--blue); }
    .agent-detail {
      position: fixed;
      inset: 28px;
      z-index: 20;
      display: none;
      grid-template-rows: auto minmax(0, 1fr);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 24px 70px rgba(31, 41, 51, 0.28);
      overflow: hidden;
    }
    .agent-detail.open { display: grid; }
    .agent-detail-head {
      display: grid;
      grid-template-columns: minmax(0, 1fr) auto;
      gap: 12px;
      align-items: center;
      padding: 14px 16px;
      border-bottom: 1px solid var(--line);
      background: #fbfcfe;
    }
    .agent-detail-title {
      display: flex;
      flex-wrap: wrap;
      align-items: baseline;
      gap: 8px;
      min-width: 0;
    }
    .agent-detail-title strong {
      font-size: 17px;
      overflow-wrap: anywhere;
    }
    .agent-detail-actions {
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .agent-detail-actions button {
      height: 28px;
      padding: 0 8px;
      font-size: 12px;
    }
    .agent-detail-body {
      display: grid;
      grid-template-columns: 300px minmax(0, 1fr);
      min-height: 0;
    }
    .agent-detail-meta {
      border-right: 1px solid var(--line);
      padding: 14px;
      overflow: auto;
      background: #fcfdff;
    }
    .agent-detail-meta dl {
      display: grid;
      grid-template-columns: 92px minmax(0, 1fr);
      gap: 8px 10px;
      margin: 0;
      font-size: 13px;
    }
    .agent-detail-meta dt { color: var(--muted); }
    .agent-detail-meta dd { margin: 0; overflow-wrap: anywhere; }
    .agent-detail-output {
      padding: 16px;
      overflow: auto;
      font-family: Consolas, "Cascadia Mono", monospace;
      font-size: 15px;
      line-height: 1.6;
      white-space: pre-wrap;
      color: #1f2a37;
    }
    .detail-backdrop {
      position: fixed;
      inset: 0;
      z-index: 19;
      display: none;
      background: rgba(31, 41, 51, 0.32);
    }
    .detail-backdrop.open { display: block; }
    @media (max-width: 980px) {
      main { grid-template-columns: 1fr; }
      .node-grid { max-height: none; }
      .side { max-height: none; }
      .agent-detail { inset: 12px; }
      .agent-detail-body { grid-template-columns: 1fr; grid-template-rows: auto minmax(0, 1fr); }
      .agent-detail-meta { border-right: 0; border-bottom: 1px solid var(--line); max-height: 210px; }
    }
    @media (max-width: 620px) {
      header { height: auto; align-items: flex-start; flex-direction: column; gap: 10px; padding: 14px; }
      .node {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto 220px 8px;
      }
      .node-output {
        grid-row: 3;
        grid-column: 1;
        border-left: 0;
        border-top: 1px solid #eef1f5;
      }
    }
  </style>
</head>
<body>
  <header>
    <h1>COL Realtime Orchestration</h1>
    <div class="toolbar">
      <span><span id="status-dot" class="status-dot"></span><span id="status-text">idle</span></span>
      <select id="mode">
        <option value="directorflow" selected>CatLaw DirectorFlow</option>
        <option value="demo">Demo Simulation</option>
        <option value="real">Real Codex Threads</option>
      </select>
      <select id="speed">
        <option value="1" selected>1x</option>
        <option value="0.5">2x</option>
        <option value="0.2">5x</option>
      </select>
      <button id="latest" type="button">Load Latest</button>
      <button id="restart" type="button">Start</button>
    </div>
  </header>
  <main>
    <section>
      <div class="section-head">
        <h2>Live Node State</h2>
        <span id="summary" class="pill">waiting</span>
      </div>
      <div id="node-grid" class="node-grid"></div>
    </section>
    <div class="side">
      <section>
        <div class="section-head"><h2>Flow Graph</h2></div>
        <div id="flow-graph" class="flow-graph"></div>
      </section>
      <section>
        <div class="section-head"><h2>Timeline</h2></div>
        <div id="timeline" class="timeline"></div>
      </section>
      <section>
        <div class="section-head"><h2>Streaming Output</h2></div>
        <div id="event-log" class="event-log"></div>
      </section>
    </div>
  </main>
  <div id="detail-backdrop" class="detail-backdrop"></div>
  <aside id="agent-detail" class="agent-detail" aria-hidden="true">
    <div class="agent-detail-head">
      <div class="agent-detail-title">
        <strong id="detail-title">Agent Detail</strong>
        <span id="detail-status" class="pill">waiting</span>
      </div>
      <div class="agent-detail-actions">
        <button id="detail-zoom-out" type="button">-</button>
        <button id="detail-zoom-reset" type="button">100%</button>
        <button id="detail-zoom-in" type="button">+</button>
        <button id="detail-close" type="button">Close</button>
      </div>
    </div>
    <div class="agent-detail-body">
      <div class="agent-detail-meta">
        <dl id="detail-meta"></dl>
      </div>
      <div id="detail-output" class="agent-detail-output"></div>
    </div>
  </aside>
  <script>
    const nodes = new Map();
    const nodeModels = new Map();
    const graphNodes = new Map();
    const graphState = { scale: 1, x: 0, y: 0, dragging: false, lastX: 0, lastY: 0 };
    const detailState = { nodeId: null, scale: 1 };
    let source = null;
    let pollTimer = null;
    let activeRunId = null;
    let activeEventCount = 0;
    let activeEventKeys = new Set();

    function byId(id) { return document.getElementById(id); }

    async function loadLatest() {
      if (source) source.close();
      nodes.clear();
      nodeModels.clear();
      graphNodes.clear();
      closeAgentDetail();
      activeEventKeys.clear();
      byId("node-grid").innerHTML = "";
      byId("flow-graph").innerHTML = "";
      byId("timeline").textContent = "";
      byId("event-log").textContent = "";
      byId("summary").textContent = "loading latest";
      byId("status-text").textContent = "loading";
      byId("status-dot").className = "status-dot live";
      const params = new URLSearchParams({ mode: byId("mode").value });
      const response = await fetch(`/latest-events?${params.toString()}`, { cache: "no-store" });
      const payload = await response.json();
      const events = payload.events || [];
      events.forEach((event, index) => applyEventOnce(event, index));
      activeEventCount = events.length;
    }

    function startRun() {
      if (source) source.close();
      nodes.clear();
      nodeModels.clear();
      graphNodes.clear();
      closeAgentDetail();
      activeEventKeys.clear();
      byId("node-grid").innerHTML = "";
      byId("flow-graph").innerHTML = "";
      byId("timeline").textContent = "";
      byId("event-log").textContent = "";
      byId("summary").textContent = "connecting";
      byId("status-text").textContent = "live";
      byId("status-dot").className = "status-dot live";
      const params = new URLSearchParams({
        mode: byId("mode").value,
        speed: byId("speed").value
      });
      source = new EventSource(`/events?${params.toString()}`);
      source.onmessage = event => {
        const payload = JSON.parse(event.data);
        applyEventOnce(payload, activeEventCount++);
      };
      source.onerror = () => {
        byId("status-text").textContent = "disconnected";
        byId("status-dot").className = "status-dot";
      };
    }

    function eventKey(event, index) {
      if (event.event_id) return String(event.event_id);
      return [
        event.type || "",
        event.node_id || event.group || "",
        event.sequence || index || 0,
        event.path || "",
        event.message || "",
        event.chunk || "",
        event.status || ""
      ].join("|");
    }

    function applyEventOnce(event, index = 0) {
      const key = eventKey(event, index);
      if (activeEventKeys.has(key)) return;
      activeEventKeys.add(key);
      applyEvent(event);
    }

    function applyEvent(event) {
      appendTimeline(event);
      if (event.type === "run_started") {
        for (const node of event.nodes) createNode(node);
        createFlowGraph(event.nodes || [], event.edges || []);
        byId("summary").textContent = `${event.nodes.length} nodes`;
        activeRunId = event.run_id || activeRunId;
      }
      if (event.type === "node_started") markNode(event.node_id, "running", event);
      if (event.type === "node_output") appendNodeOutput(event);
      if (event.type === "artifact_written" || event.type === "artifact_processed") {
        appendLog(`${event.node_id}> ${event.message || event.path}`);
        recordArtifact(event);
        markGraphNode(event.node_id, "running", event.type);
      }
      if (event.type === "node_completed") {
        markNode(event.node_id, statusClass(event.status), event);
      }
      if (event.type === "run_completed") {
        byId("summary").textContent = event.status;
        byId("status-text").textContent = "completed";
        byId("status-dot").className = "status-dot done";
        if (source) source.close();
      }
    }

    function createNode(node) {
      nodeModels.set(node.id, {
        ...node,
        status: "waiting",
        output: "",
        artifacts: []
      });
      const card = document.createElement("article");
      card.className = "node";
      card.id = `node-${node.id}`;
      card.innerHTML = `
        <div>
          <div class="node-title"></div>
          <div class="node-meta"></div>
          <button type="button" class="node-inspect">Inspect</button>
        </div>
        <div class="node-output"></div>
        <div class="progress"><div class="bar"></div></div>
      `;
      card.querySelector(".node-title").textContent = node.label;
      card.querySelector(".node-meta").innerHTML = `
        <span class="pill">${node.role}</span>
        <span class="pill">${node.phase}</span>
        <span class="pill">${node.duration_seconds}s est</span>
      `;
      card.querySelector(".node-inspect").onclick = () => openAgentDetail(node.id);
      card.ondblclick = () => openAgentDetail(node.id);
      nodes.set(node.id, card);
      byId("node-grid").appendChild(card);
    }

    function statusClass(status) {
      const value = String(status || "").toLowerCase();
      if (value === "passed" || value === "done" || value === "closed") return "done";
      if (value.includes("blocked")) return "blocked";
      if (value.includes("fail") || value.includes("error")) return "failed";
      if (value.includes("waiting") || value.includes("idle")) return "waiting";
      return "running";
    }

    function createFlowGraph(nodesList, edges) {
      const graph = byId("flow-graph");
      graph.innerHTML = "";
      graphNodes.clear();
      const toolbar = document.createElement("div");
      toolbar.className = "graph-toolbar";
      toolbar.innerHTML = `
        <button type="button" data-action="zoom-in">+</button>
        <button type="button" data-action="zoom-out">-</button>
        <button type="button" data-action="fit">Fit</button>
        <button type="button" data-action="reset">Reset</button>
      `;
      const viewport = document.createElement("div");
      viewport.className = "graph-viewport";
      const canvas = document.createElement("div");
      canvas.className = "graph-canvas";
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.classList.add("graph-svg");
      svg.setAttribute("viewBox", "0 0 820 320");
      svg.innerHTML = `<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#aeb8c6"></path></marker></defs>`;
      canvas.appendChild(svg);
      viewport.appendChild(canvas);
      graph.appendChild(toolbar);
      graph.appendChild(viewport);

      const positions = layoutGraph(nodesList, edges);
      for (const edge of edges || []) {
        const from = positions.get(edge.from);
        const to = positions.get(edge.to);
        if (!from || !to) continue;
        const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
        const isLoop = to.x <= from.x;
        path.classList.add("graph-edge");
        if (isLoop) path.classList.add("loop");
        const startX = from.x + 240;
        const startY = from.y + 18;
        const endX = to.x;
        const endY = to.y + 18;
        const midX = isLoop ? Math.max(startX, endX) + 44 : (startX + endX) / 2;
        path.setAttribute("d", `M ${startX} ${startY} C ${midX} ${startY}, ${midX} ${endY}, ${endX} ${endY}`);
        path.setAttribute("marker-end", "url(#arrow)");
        svg.appendChild(path);
      }

      for (const node of nodesList) {
        const pos = positions.get(node.id);
        if (!pos) continue;
        const row = document.createElement("div");
        row.className = "graph-node";
        row.id = `graph-${node.id}`;
        row.style.left = `${pos.x}px`;
        row.style.top = `${pos.y}px`;
        row.innerHTML = `
          <span class="graph-dot"></span>
          <span class="graph-label"></span>
          <span class="graph-status">waiting</span>
        `;
        row.querySelector(".graph-label").textContent = node.label || node.id;
        row.onclick = () => openAgentDetail(node.id);
        graphNodes.set(node.id, row);
        canvas.appendChild(row);
      }
      wireGraphControls(graph, viewport, canvas);
      fitGraph(viewport, canvas);
    }

    function wireGraphControls(graph, viewport, canvas) {
      graph.querySelector('[data-action="zoom-in"]').onclick = () => zoomGraph(viewport, canvas, 1.18);
      graph.querySelector('[data-action="zoom-out"]').onclick = () => zoomGraph(viewport, canvas, 0.84);
      graph.querySelector('[data-action="fit"]').onclick = () => fitGraph(viewport, canvas);
      graph.querySelector('[data-action="reset"]').onclick = () => {
        graphState.scale = 1;
        graphState.x = 0;
        graphState.y = 0;
        applyGraphTransform(canvas);
      };
      viewport.onwheel = event => {
        event.preventDefault();
        zoomGraph(viewport, canvas, event.deltaY < 0 ? 1.08 : 0.92, event.offsetX, event.offsetY);
      };
      viewport.onpointerdown = event => {
        graphState.dragging = true;
        graphState.lastX = event.clientX;
        graphState.lastY = event.clientY;
        viewport.classList.add("dragging");
        viewport.setPointerCapture(event.pointerId);
      };
      viewport.onpointermove = event => {
        if (!graphState.dragging) return;
        graphState.x += event.clientX - graphState.lastX;
        graphState.y += event.clientY - graphState.lastY;
        graphState.lastX = event.clientX;
        graphState.lastY = event.clientY;
        applyGraphTransform(canvas);
      };
      viewport.onpointerup = event => {
        graphState.dragging = false;
        viewport.classList.remove("dragging");
        viewport.releasePointerCapture(event.pointerId);
      };
    }

    function zoomGraph(viewport, canvas, factor, originX = viewport.clientWidth / 2, originY = viewport.clientHeight / 2) {
      const previous = graphState.scale;
      const next = Math.max(0.35, Math.min(2.4, previous * factor));
      graphState.x = originX - (originX - graphState.x) * (next / previous);
      graphState.y = originY - (originY - graphState.y) * (next / previous);
      graphState.scale = next;
      applyGraphTransform(canvas);
    }

    function fitGraph(viewport, canvas) {
      const scaleX = (viewport.clientWidth - 24) / canvas.offsetWidth;
      const scaleY = (viewport.clientHeight - 24) / canvas.offsetHeight;
      graphState.scale = Math.max(0.35, Math.min(1.25, Math.min(scaleX, scaleY)));
      graphState.x = 12;
      graphState.y = 12;
      applyGraphTransform(canvas);
    }

    function applyGraphTransform(canvas) {
      canvas.style.transform = `translate(${graphState.x}px, ${graphState.y}px) scale(${graphState.scale})`;
    }

    function layoutGraph(nodesList, edges) {
      const positions = new Map();
      const children = new Set((edges || []).map(edge => edge.to));
      const roots = nodesList.filter(node => !children.has(node.id));
      const middle = nodesList.filter(node => node.parallel_group);
      const sinks = nodesList.filter(node => !node.parallel_group && !roots.includes(node));
      const columns = [roots, middle, sinks].filter(group => group.length);
      const xValues = [12, 260, 508];
      columns.forEach((group, col) => {
        const gap = Math.max(58, 250 / Math.max(1, group.length));
        group.forEach((node, index) => {
          positions.set(node.id, { x: xValues[col] || 12 + col * 248, y: 28 + index * gap });
        });
      });
      return positions;
    }

    function markNode(id, state, event) {
      const card = nodes.get(id);
      if (!card) return;
      updateNodeModel(id, {
        status: event.status || state,
        thread_id: event.thread_id || (nodeModels.get(id) && nodeModels.get(id).thread_id),
        progress: state === "done" ? 1 : (nodeModels.get(id) && nodeModels.get(id).progress) || 0
      });
      card.classList.remove("running", "done", "blocked", "failed", "waiting");
      if (state !== "waiting") card.classList.add(state);
      if (state === "running") card.querySelector(".bar").style.width = "2%";
      if (state === "done") card.querySelector(".bar").style.width = "100%";
      if (state === "failed") card.querySelector(".bar").style.width = "100%";
      appendLog(`${event.type}: ${id}`);
      markGraphNode(id, state, event.status || state);
      refreshAgentDetail(id);
    }

    function markGraphNode(id, state, status) {
      const row = graphNodes.get(id);
      if (!row) return;
      row.classList.remove("running", "done", "blocked", "failed", "waiting");
      if (state !== "waiting") row.classList.add(state);
      row.querySelector(".graph-status").textContent = status || state;
    }

    function appendNodeOutput(event) {
      const card = nodes.get(event.node_id);
      if (!card) return;
      card.querySelector(".node-output").textContent += `${event.chunk}\n\n`;
      card.querySelector(".node-output").scrollTop = card.querySelector(".node-output").scrollHeight;
      card.querySelector(".bar").style.width = `${Math.round(event.progress * 100)}%`;
      const model = nodeModels.get(event.node_id);
      if (model) {
        model.output += `${event.chunk}\n\n`;
        if (event.thread_id) model.thread_id = event.thread_id;
        model.progress = event.progress;
      }
      appendLog(`${event.node_id}> ${event.chunk}`);
      refreshAgentDetail(event.node_id);
    }

    function updateNodeModel(id, patch) {
      const model = nodeModels.get(id);
      if (!model) return;
      Object.assign(model, patch);
    }

    function recordArtifact(event) {
      const model = nodeModels.get(event.node_id);
      if (!model) return;
      model.artifacts.push({
        type: event.type,
        path: event.path || "",
        message: event.message || ""
      });
      refreshAgentDetail(event.node_id);
    }

    function openAgentDetail(nodeId) {
      const model = nodeModels.get(nodeId);
      if (!model) return;
      detailState.nodeId = nodeId;
      byId("agent-detail").classList.add("open");
      byId("agent-detail").setAttribute("aria-hidden", "false");
      byId("detail-backdrop").classList.add("open");
      refreshAgentDetail(nodeId, true);
    }

    function closeAgentDetail() {
      detailState.nodeId = null;
      byId("agent-detail").classList.remove("open");
      byId("agent-detail").setAttribute("aria-hidden", "true");
      byId("detail-backdrop").classList.remove("open");
    }

    function refreshAgentDetail(nodeId, force = false) {
      if (detailState.nodeId !== nodeId && !force) return;
      const model = nodeModels.get(nodeId);
      if (!model) return;
      byId("detail-title").textContent = model.label || model.id;
      byId("detail-status").textContent = model.status || "waiting";
      const artifacts = (model.artifacts || [])
        .map(item => `${item.type}: ${item.path || item.message}`)
        .join("\\n") || "none";
      byId("detail-meta").innerHTML = `
        <dt>Node</dt><dd>${escapeHtml(model.id)}</dd>
        <dt>Role</dt><dd>${escapeHtml(model.role || "")}</dd>
        <dt>Phase</dt><dd>${escapeHtml(model.phase || "")}</dd>
        <dt>Thread</dt><dd>${escapeHtml(model.thread_id || "not assigned")}</dd>
        <dt>Progress</dt><dd>${Math.round((model.progress || 0) * 100)}%</dd>
        <dt>Artifacts</dt><dd>${escapeHtml(artifacts)}</dd>
      `;
      const output = model.output || "No output yet.";
      const detailOutput = byId("detail-output");
      const atBottom = detailOutput.scrollTop + detailOutput.clientHeight >= detailOutput.scrollHeight - 24;
      detailOutput.textContent = output;
      detailOutput.style.fontSize = `${Math.round(15 * detailState.scale)}px`;
      if (atBottom || force) detailOutput.scrollTop = detailOutput.scrollHeight;
    }

    function zoomAgentDetail(factor) {
      detailState.scale = Math.max(0.7, Math.min(2.4, detailState.scale * factor));
      byId("detail-zoom-reset").textContent = `${Math.round(detailState.scale * 100)}%`;
      if (detailState.nodeId) refreshAgentDetail(detailState.nodeId, true);
    }

    function resetAgentDetailZoom() {
      detailState.scale = 1;
      byId("detail-zoom-reset").textContent = "100%";
      if (detailState.nodeId) refreshAgentDetail(detailState.nodeId, true);
    }

    function escapeHtml(value) {
      return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;");
    }

    function appendTimeline(event) {
      const label = event.node_id || event.group || event.status || "";
      byId("timeline").textContent += `${event.type} ${label}\n`;
    }

    function appendLog(line) {
      const log = byId("event-log");
      log.textContent += `${line}\n`;
      log.scrollTop = log.scrollHeight;
    }

    async function pollActiveEvents() {
      if (source) return;
      const params = new URLSearchParams({ mode: byId("mode").value });
      const response = await fetch(`/active-events?${params.toString()}`, { cache: "no-store" });
      const payload = await response.json();
      const events = payload.events || [];
      if (!events.length) return;
      const runStarted = events.find(event => event.type === "run_started");
      const runId = runStarted && runStarted.run_id ? runStarted.run_id : "active";
      if (runId !== activeRunId) {
        activeRunId = runId;
        activeEventCount = 0;
        nodes.clear();
        nodeModels.clear();
        graphNodes.clear();
        closeAgentDetail();
        activeEventKeys.clear();
        byId("node-grid").innerHTML = "";
        byId("flow-graph").innerHTML = "";
        byId("timeline").textContent = "";
        byId("event-log").textContent = "";
      }
      events.forEach((event, index) => applyEventOnce(event, index));
      activeEventCount = events.length;
    }

    byId("latest").addEventListener("click", () => loadLatest().catch(error => {
      byId("summary").textContent = "latest failed";
      appendLog(`latest error: ${error.message}`);
    }));
    byId("restart").addEventListener("click", startRun);
    byId("detail-close").addEventListener("click", closeAgentDetail);
    byId("detail-backdrop").addEventListener("click", closeAgentDetail);
    byId("detail-zoom-in").addEventListener("click", () => zoomAgentDetail(1.15));
    byId("detail-zoom-out").addEventListener("click", () => zoomAgentDetail(0.87));
    byId("detail-zoom-reset").addEventListener("click", resetAgentDetailZoom);
    window.addEventListener("keydown", event => {
      if (event.key === "Escape") closeAgentDetail();
    });
    byId("mode").addEventListener("change", () => {
      if (source) source.close();
      source = null;
      activeRunId = null;
      activeEventCount = 0;
      activeEventKeys.clear();
      byId("summary").textContent = "waiting";
      byId("status-text").textContent = "idle";
      byId("status-dot").className = "status-dot";
    });
    loadLatest().catch(() => {
      byId("summary").textContent = "waiting";
      byId("status-text").textContent = "idle";
      byId("status-dot").className = "status-dot";
    });
    pollTimer = setInterval(() => pollActiveEvents().catch(() => {}), 1000);
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    raise SystemExit(main())
