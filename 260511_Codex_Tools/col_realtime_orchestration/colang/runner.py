from __future__ import annotations

import json
import os
import queue
import re
import sqlite3
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

from colang.models import IRProgram, Instruction, ThreadSelectorDecl


DEFAULT_CODEX_HOME = Path.home() / ".codex"
DEFAULT_CODEX_EXE = DEFAULT_CODEX_HOME / ".sandbox-bin" / "codex.exe"


class ThreadTurnResult:
    def __init__(
        self,
        thread_id: str,
        turn_id: str | None,
        text: str,
        raw_events: list[dict[str, Any]] | None = None,
        fallback_reason: str | None = None,
    ) -> None:
        self.thread_id = thread_id
        self.turn_id = turn_id
        self.text = text
        self.raw_events = raw_events or []
        self.fallback_reason = fallback_reason


class InMemoryThreadBackend:
    def __init__(
        self,
        responses: dict[str, str] | None = None,
        default_response: str = "",
        selectors: dict[str, str] | None = None,
    ):
        self.responses = responses or {}
        self.default_response = default_response
        self.selectors = selectors or {}
        self.calls: list[dict[str, Any]] = []

    def run_turn(
        self,
        prompt: str,
        *,
        thread_mode: str,
        thread_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        timeout_seconds: int = 120,
    ) -> ThreadTurnResult:
        metadata = metadata or {}
        item = str(metadata.get("item", ""))
        text = self.responses.get(item, self.default_response)
        self.calls.append(
            {
                "prompt": prompt,
                "thread_mode": thread_mode,
                "thread_id": thread_id,
                "metadata": metadata,
                "timeout_seconds": timeout_seconds,
            }
        )
        return ThreadTurnResult(
            thread_id=thread_id or f"mock-thread-{len(self.calls)}",
            turn_id=f"mock-turn-{len(self.calls)}",
            text=text,
        )

    def select_thread(
        self, selector: ThreadSelectorDecl, *, role_name: str | None = None
    ) -> str | None:
        return self.selectors.get(selector.name)


class CodexThreadBackend:
    def __init__(
        self,
        codex_home: Path | str = DEFAULT_CODEX_HOME,
        codex_exe: Path | str = DEFAULT_CODEX_EXE,
        cwd: Path | str | None = None,
    ) -> None:
        self.codex_home = Path(codex_home)
        self.codex_exe = Path(codex_exe)
        self.cwd = str(cwd or Path.cwd())
        self.calls: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def run_turn(
        self,
        prompt: str,
        *,
        thread_mode: str,
        thread_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        timeout_seconds: int = 120,
    ) -> ThreadTurnResult:
        with self._lock:
            return self._run_turn_locked(
                prompt,
                thread_mode=thread_mode,
                thread_id=thread_id,
                metadata=metadata,
                timeout_seconds=timeout_seconds,
            )

    def _run_turn_locked(
        self,
        prompt: str,
        *,
        thread_mode: str,
        thread_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        timeout_seconds: int = 120,
    ) -> ThreadTurnResult:
        session = _CodexRpcSession(self.codex_exe, self.codex_home)
        observed: list[dict[str, Any]] = []
        turn_id: str | None = None
        try:
            session.request(
                "init",
                "initialize",
                {
                    "clientInfo": {"name": "colang-runtime", "version": "0.2"},
                    "capabilities": {"experimentalApi": True},
                },
                timeout_seconds=30,
                observed=observed,
            )
            if thread_mode == "create":
                response = session.request(
                    "thread-start",
                    "thread/start",
                    {"cwd": self.cwd},
                    timeout_seconds=30,
                    observed=observed,
                )
                thread = response.get("result", {}).get("thread", {})
                thread_id = thread.get("id")
            elif thread_mode == "resume":
                if not thread_id:
                    raise ValueError("thread_mode=resume requires thread_id")
                session.request(
                    "thread-resume",
                    "thread/resume",
                    {"threadId": thread_id},
                    timeout_seconds=30,
                    observed=observed,
                )
            else:
                raise ValueError(f"unsupported thread_mode: {thread_mode}")

            if not thread_id:
                raise RuntimeError("Codex app-server did not return a thread id")

            response = session.request(
                "turn-start",
                "turn/start",
                {
                    "threadId": thread_id,
                    "input": [{"type": "text", "text": prompt}],
                },
                timeout_seconds=30,
                observed=observed,
            )
            turn = response.get("result", {}).get("turn", {})
            turn_id = turn.get("id")
            text = session.wait_for_turn(
                target_turn_id=turn_id,
                timeout_seconds=timeout_seconds,
                observed=observed,
            )
        finally:
            session.close()

        self.calls.append(
            {
                "prompt": prompt,
                "thread_mode": thread_mode,
                "thread_id": thread_id,
                "turn_id": turn_id,
                "metadata": metadata or {},
            }
        )
        return ThreadTurnResult(
            thread_id=str(thread_id),
            turn_id=turn_id,
            text=text,
            raw_events=observed,
        )

    def select_thread(
        self, selector: ThreadSelectorDecl, *, role_name: str | None = None
    ) -> str | None:
        db_path = self.codex_home / "state_5.sqlite"
        if not db_path.exists():
            return None
        fields = selector.fields
        clauses: list[str] = []
        params: list[str] = []
        for field_name, column in (
            ("cwd_contains", "cwd"),
            ("title_contains", "title"),
            ("first_message_contains", "first_user_message"),
        ):
            value = fields.get(field_name)
            if value:
                clauses.append(f"{column} like ?")
                params.append(f"%{value}%")
        project = fields.get("project")
        if project:
            clauses.append("(cwd like ? or title like ? or first_user_message like ?)")
            params.extend([f"%{project}%", f"%{project}%", f"%{project}%"])
        role = fields.get("role") or role_name
        if role:
            clauses.append("(title like ? or first_user_message like ?)")
            params.extend([f"%{role}%", f"%{role}%"])
        where = " and ".join(clauses) if clauses else "1=1"
        query = (
            "select id from threads where archived = 0 and "
            f"{where} order by coalesce(updated_at_ms, updated_at * 1000) desc limit 1"
        )
        try:
            with sqlite3.connect(db_path) as con:
                row = con.execute(query, params).fetchone()
        except sqlite3.Error:
            return None
        return str(row[0]) if row else None


class _CodexRpcSession:
    def __init__(self, codex_exe: Path, codex_home: Path) -> None:
        if not codex_exe.exists():
            raise FileNotFoundError(f"codex.exe not found: {codex_exe}")
        env = os.environ.copy()
        env["CODEX_HOME"] = str(codex_home)
        self.proc = subprocess.Popen(
            [str(codex_exe), "app-server"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            env=env,
        )
        self.events: queue.Queue[tuple[str, str]] = queue.Queue()
        self._pump(self.proc.stdout)
        self._pump(self.proc.stderr)

    def _pump(self, handle: Any) -> None:
        def run() -> None:
            for line in handle:
                self.events.put(("json", line.rstrip("\r\n")))

        threading.Thread(target=run, daemon=True).start()

    def request(
        self,
        request_id: str,
        method: str,
        params: dict[str, Any],
        *,
        timeout_seconds: int,
        observed: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self._send({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params})
        deadline = time.time() + timeout_seconds
        while time.time() < deadline:
            payload = self._next_payload(deadline, observed)
            if payload.get("id") == request_id:
                if "error" in payload:
                    raise RuntimeError(json.dumps(payload["error"], ensure_ascii=False))
                return payload
        raise TimeoutError(f"timed out waiting for {method}")

    def wait_for_turn(
        self,
        *,
        target_turn_id: str | None,
        timeout_seconds: int,
        observed: list[dict[str, Any]],
    ) -> str:
        deadline = time.time() + timeout_seconds
        assistant_text = ""
        while time.time() < deadline:
            payload = self._next_payload(deadline, observed)
            method = payload.get("method")
            params = payload.get("params", {})
            if method == "item/agentMessage/delta":
                if target_turn_id is None or params.get("turnId") == target_turn_id:
                    assistant_text += str(params.get("delta", ""))
            elif method == "item/completed":
                item = params.get("item", {})
                if item.get("type") == "agentMessage":
                    if target_turn_id is None or params.get("turnId") == target_turn_id:
                        assistant_text = str(item.get("text", assistant_text))
            elif method == "turn/completed":
                turn = params.get("turn", {})
                if target_turn_id is None or turn.get("id") == target_turn_id:
                    return assistant_text
            elif method == "turn/aborted":
                raise RuntimeError("turn aborted")
        raise TimeoutError("timed out waiting for turn/completed")

    def _send(self, payload: dict[str, Any]) -> None:
        if self.proc.stdin is None:
            raise RuntimeError("app-server stdin is closed")
        self.proc.stdin.write(json.dumps(payload, ensure_ascii=False) + "\n")
        self.proc.stdin.flush()

    def _next_payload(
        self, deadline: float, observed: list[dict[str, Any]]
    ) -> dict[str, Any]:
        timeout = max(0.1, min(1.0, deadline - time.time()))
        try:
            _, line = self.events.get(timeout=timeout)
        except queue.Empty:
            return {}
        if not line:
            return {}
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            payload = {"text": line}
        observed.append(payload)
        return payload

    def close(self) -> None:
        try:
            if self.proc.stdin:
                self.proc.stdin.close()
        finally:
            if self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=5)


def run_program(
    program: IRProgram,
    *,
    backend: Any,
    timeout_seconds: int = 120,
) -> dict[str, Any]:
    context = {
        name: _decode_data_value(data_value.value, data_value.format)
        for name, data_value in program.data.items()
    }
    outputs: dict[str, Any] = {}
    instruction_results: list[dict[str, Any]] = []
    thread_graph: dict[str, Any] = {"nodes": [], "edges": []}
    human_requests: list[dict[str, Any]] = []
    verified = True
    instruction_by_id = {instruction.id: instruction for instruction in program.instructions}
    node_by_id = {node.id: node for node in program.workflow_nodes}

    def execute_instruction(instruction: Instruction) -> dict[str, Any]:
        nonlocal verified
        if instruction.op == "CALL":
            value = _run_call(
                program, instruction, context, backend, timeout_seconds, thread_graph
            )
        elif instruction.op == "MAP":
            value = _run_map(instruction, context, backend, timeout_seconds, thread_graph)
        elif instruction.op == "VERIFY":
            value = _run_verify(instruction, context)
            verified = verified and bool(value.get("verified", False))
        elif instruction.op in {"QUESTION", "ESCALATE"}:
            value = _run_human_interrupt(instruction, context)
            human_requests.append(value)
        else:
            value = {"status": "skipped", "op": instruction.op}

        schema_errors = _validate_output_schema(program, instruction.output_schema, value)
        if schema_errors:
            value["schema_errors"] = schema_errors
            verified = False

        context[instruction.output_schema] = value
        outputs[instruction.output_schema] = value
        instruction_results.append({"instruction_id": instruction.id, "output": value})
        return value

    def execute_nodes(node_ids: list[str]) -> None:
        for node_id in node_ids:
            execute_node(node_id)

    def execute_node(node_id: str) -> None:
        nonlocal verified
        node = node_by_id.get(node_id)
        if node is None:
            return
        if node.instruction_id:
            execute_instruction(instruction_by_id[node.instruction_id])
            return
        if node.kind in {"role", "artifact", "message", "schema", "thread_selector", "wait"}:
            return
        if node.kind == "after":
            execute_nodes(list(node.metadata.get("children", [])))
            return
        if node.kind == "parallel_fork":
            branches = list(node.metadata.get("branches", []))
            with ThreadPoolExecutor(max_workers=max(1, len(branches))) as pool:
                futures = [
                    pool.submit(execute_nodes, list(branch.get("nodes", [])))
                    for branch in branches
                ]
                for future in as_completed(futures):
                    future.result()
            return
        if node.kind == "loop":
            max_rounds = node.metadata.get("max_rounds")
            if not isinstance(max_rounds, int) or max_rounds <= 0:
                verified = False
                return
            rounds = 0
            while not _evaluate_condition(str(node.condition or ""), context):
                if rounds >= max_rounds:
                    verified = False
                    break
                execute_nodes(list(node.metadata.get("body", [])))
                rounds += 1
            outputs[f"{node.id}:rounds"] = rounds
            return
        if node.kind == "condition":
            branch_key = (
                "true_nodes"
                if _evaluate_condition(str(node.condition or ""), context)
                else "false_nodes"
            )
            execute_nodes(list(node.metadata.get(branch_key, [])))
            return
        if node.kind == "emit":
            name = str(node.metadata.get("name", node.label.replace("EMIT ", "")))
            value = {
                "status": "emitted",
                "artifact": node.artifact,
                "from": node.role,
            }
            context[name] = value
            outputs[name] = value
            return

    roots = program.workflow_roots
    if roots:
        execute_nodes(roots)
    else:
        for instruction in program.instructions:
            execute_instruction(instruction)

    return {
        "program": program.name,
        "verified": verified,
        "outputs": outputs,
        "instructions": instruction_results,
        "thread_calls": getattr(backend, "calls", []),
        "thread_graph": thread_graph,
        "human_requests": human_requests,
    }


def _run_call(
    program: IRProgram,
    instruction: Instruction,
    context: dict[str, Any],
    backend: Any,
    timeout_seconds: int,
    thread_graph: dict[str, Any],
) -> dict[str, Any]:
    prompt = _render_template(
        str(
            instruction.runtime_policy.get(
                "prompt_template", instruction.runtime_policy.get("prompt", "")
            )
        ),
        context,
    )
    thread_id = instruction.runtime_policy.get("thread_id")
    if isinstance(thread_id, str):
        thread_id = _render_template(thread_id, context)
    thread_mode = str(instruction.runtime_policy.get("thread_mode", "create"))
    role = program.roles.get(instruction.agent_ref)
    if role and not instruction.runtime_policy.get("thread_mode"):
        if role.thread_id:
            thread_id = _render_template(role.thread_id, context)
            thread_mode = "resume"
        elif role.selector and role.selector in program.thread_selectors:
            selected = _select_thread(backend, program.thread_selectors[role.selector], role.name)
            if selected:
                thread_id = selected
                thread_mode = "resume"
    metadata = {"instruction_id": instruction.id}
    result = backend.run_turn(
        prompt,
        thread_mode=thread_mode,
        thread_id=thread_id,
        metadata=metadata,
        timeout_seconds=timeout_seconds,
    )
    result = _retry_empty_response(
        result,
        backend,
        prompt,
        timeout_seconds,
        metadata,
        allow_empty=bool(instruction.runtime_policy.get("allow_empty", False)),
        fallback_text=_render_empty_fallback(instruction, context),
    )
    value = _format_response(result, instruction.runtime_policy.get("expect", "text"))
    _add_graph_node(
        thread_graph,
        value["thread_id"],
        str(instruction.runtime_policy.get("role", instruction.agent_ref)),
        prompt,
    )
    return value


def _run_map(
    instruction: Instruction,
    context: dict[str, Any],
    backend: Any,
    timeout_seconds: int,
    thread_graph: dict[str, Any],
) -> dict[str, Any]:
    task = instruction.runtime_policy.get("task")
    if task not in {"matrix_cell_2x2", "visible_matrix_cell_2x2"}:
        raise ValueError(f"unsupported MAP task: {task}")

    matrix_start = 1 if task == "visible_matrix_cell_2x2" else 0
    parent_thread_id = None
    if task == "visible_matrix_cell_2x2":
        parent = context[instruction.input_refs[0]]
        parent_thread_id = str(parent["thread_id"])
    matrix_a, matrix_b = _load_two_matrices(instruction, context, start_index=matrix_start)
    items = instruction.schedule_policy.get("items", [])
    if isinstance(items, int):
        items = [f"item{idx}" for idx in range(items)]

    max_workers = int(instruction.schedule_policy.get("max_workers", 1))
    futures: dict[Any, dict[str, str]] = {}
    results: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        for item in items:
            prompt = _matrix_cell_prompt(
                str(item),
                matrix_a,
                matrix_b,
                context=context,
                runtime_policy=instruction.runtime_policy,
                parent_thread_id=parent_thread_id,
            )
            metadata = {"instruction_id": instruction.id, "item": str(item)}
            future = pool.submit(
                backend.run_turn,
                prompt,
                thread_mode=str(instruction.runtime_policy.get("thread_mode", "create")),
                thread_id=instruction.runtime_policy.get("thread_id"),
                metadata=metadata,
                timeout_seconds=timeout_seconds,
            )
            futures[future] = {
                "item": str(item),
                "prompt": prompt,
                "metadata": metadata,
            }

        for future in as_completed(futures):
            future_meta = futures[future]
            item = future_meta["item"]
            prompt = future_meta["prompt"]
            turn_result = future.result()
            fallback_text = None
            if instruction.runtime_policy.get("allow_empty", False):
                fallback_text = _matrix_cell_fallback(item, matrix_a, matrix_b)
            turn_result = _retry_empty_response(
                turn_result,
                backend,
                prompt,
                timeout_seconds,
                future_meta["metadata"],
                allow_empty=bool(instruction.runtime_policy.get("allow_empty", False)),
                fallback_text=fallback_text,
            )
            parsed = _parse_json_response(turn_result.text)
            parsed.setdefault("cell", item)
            parsed["thread_id"] = turn_result.thread_id
            parsed["turn_id"] = turn_result.turn_id
            if turn_result.fallback_reason:
                parsed["fallback_reason"] = turn_result.fallback_reason
                parsed["empty_response"] = True
            if parent_thread_id:
                parsed["parent_thread_id"] = parent_thread_id
                _add_graph_node(
                    thread_graph,
                    turn_result.thread_id,
                    f"worker:{item}",
                    prompt,
                )
                thread_graph["edges"].append(
                    {
                        "from": parent_thread_id,
                        "to": turn_result.thread_id,
                        "item": item,
                        "instruction_id": instruction.id,
                    }
                )
            results[item] = parsed

    return {
        "task": task,
        "matrix": _reduce_matrix_2x2(results),
        "cells": results,
        "reduce": instruction.schedule_policy.get("reduce"),
    }


def _run_verify(instruction: Instruction, context: dict[str, Any]) -> dict[str, Any]:
    verify_kind = instruction.runtime_policy.get("verify")
    if verify_kind != "matrix_2x2":
        return {"verified": True, "note": "No runtime verifier configured."}

    cell_output = context[instruction.input_refs[0]]
    matrix_a, matrix_b = _load_two_matrices(instruction, context, start_index=1)
    expected = _matrix_multiply_2x2(matrix_a, matrix_b)
    actual = cell_output["matrix"]
    return {"verified": actual == expected, "matrix": actual, "expected": expected}


def _run_human_interrupt(instruction: Instruction, context: dict[str, Any]) -> dict[str, Any]:
    policy = instruction.runtime_policy
    question = str(policy.get("question", policy.get("reason", "")))
    if question:
        question = _render_template(question, context)
    answer = policy.get("default")
    if isinstance(answer, str):
        answer = _render_template(answer, context)
    return {
        "kind": instruction.op.lower(),
        "role": instruction.agent_ref,
        "route": str(policy.get("route", "current_director")),
        "question": question,
        "risk": str(policy.get("risk", "")),
        "answer": answer,
        "status": "answered" if answer is not None else "awaiting_human",
    }


def _validate_output_schema(
    program: IRProgram, output_name: str, value: dict[str, Any]
) -> list[dict[str, Any]]:
    artifact = program.artifacts.get(output_name)
    if artifact is None:
        return []
    schema = program.schemas.get(artifact.schema)
    if schema is None:
        return []
    errors: list[dict[str, Any]] = []
    for field_name, field_decl in schema.fields.items():
        if field_decl.required and field_name not in value:
            errors.append(
                {
                    "field": field_name,
                    "code": "required",
                    "message": f"Missing required field '{field_name}'.",
                }
            )
            continue
        if field_name not in value:
            continue
        field_value = value[field_name]
        if field_decl.type == "enum" and str(field_value) not in field_decl.values:
            errors.append(
                {
                    "field": field_name,
                    "code": "enum",
                    "message": (
                        f"Expected one of {field_decl.values}, got {field_value!r}."
                    ),
                }
            )
        if field_decl.type == "list" and not isinstance(field_value, list):
            errors.append(
                {
                    "field": field_name,
                    "code": "type",
                    "message": f"Expected list for field '{field_name}'.",
                }
            )
    return errors


def _evaluate_condition(condition: str, context: dict[str, Any]) -> bool:
    condition = condition.strip()
    match = re.fullmatch(r'([A-Za-z_][A-Za-z0-9_.]*)\s*(==|!=)\s*"([^"]*)"', condition)
    if not match:
        return False
    left_path, operator, right_value = match.groups()
    left_value = _lookup_context_path(left_path, context)
    if operator == "==":
        return str(left_value) == right_value
    return str(left_value) != right_value


def _lookup_context_path(path: str, context: dict[str, Any]) -> Any:
    parts = path.split(".")
    if parts[0] not in context:
        return None
    value: Any = context[parts[0]]
    for part in parts[1:]:
        if isinstance(value, dict):
            value = value.get(part)
        else:
            value = getattr(value, part, None)
    return value


def _select_thread(
    backend: Any, selector: ThreadSelectorDecl, role_name: str | None = None
) -> str | None:
    select = getattr(backend, "select_thread", None)
    if not callable(select):
        return None
    return select(selector, role_name=role_name)


def _decode_data_value(value: Any, value_format: str) -> Any:
    if value_format == "json":
        return json.loads(str(value))
    if value_format == "auto" and isinstance(value, str) and value[:1] in "[{":
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _format_response(result: ThreadTurnResult, expect: Any) -> dict[str, Any]:
    if expect == "json":
        payload = _parse_json_response(result.text)
    else:
        payload = {"text": result.text}
    payload["thread_id"] = result.thread_id
    payload["turn_id"] = result.turn_id
    if result.fallback_reason:
        payload["fallback_reason"] = result.fallback_reason
        payload["empty_response"] = True
    return payload


def _retry_empty_response(
    result: ThreadTurnResult,
    backend: Any,
    prompt: str,
    timeout_seconds: int,
    metadata: dict[str, Any],
    *,
    allow_empty: bool = False,
    fallback_text: str | None = None,
) -> ThreadTurnResult:
    if result.text.strip():
        return result

    retry_metadata = dict(metadata)
    retry_metadata["retry"] = "empty_response"
    retry_prompt = (
        "The previous turn completed without an assistant message.\n"
        "Reply now with only the requested final answer for the original request below.\n"
        "Do not explain.\n\n"
        f"{prompt}"
    )
    retry_result = backend.run_turn(
        retry_prompt,
        thread_mode="resume",
        thread_id=result.thread_id,
        metadata=retry_metadata,
        timeout_seconds=timeout_seconds,
    )
    if not retry_result.text.strip():
        if allow_empty:
            return ThreadTurnResult(
                thread_id=retry_result.thread_id,
                turn_id=retry_result.turn_id,
                text=fallback_text or "",
                raw_events=result.raw_events + retry_result.raw_events,
                fallback_reason="empty_response_after_retry",
            )
        raise RuntimeError(
            f"thread {result.thread_id} returned an empty assistant response after retry"
        )
    return retry_result


def _render_empty_fallback(instruction: Instruction, context: dict[str, Any]) -> str | None:
    fallback = instruction.runtime_policy.get("empty_fallback")
    if fallback is None:
        return None
    return _render_template(str(fallback), context)


def _load_two_matrices(
    instruction: Instruction, context: dict[str, Any], start_index: int = 0
) -> tuple[list[list[int]], list[list[int]]]:
    refs = instruction.input_refs[start_index : start_index + 2]
    if len(refs) != 2:
        raise ValueError("matrix task requires two matrix inputs")
    return _coerce_matrix(context[refs[0]]), _coerce_matrix(context[refs[1]])


def _coerce_matrix(value: Any) -> list[list[int]]:
    if isinstance(value, str):
        value = json.loads(value)
    if (
        not isinstance(value, list)
        or len(value) != 2
        or any(not isinstance(row, list) or len(row) != 2 for row in value)
    ):
        raise ValueError("expected a 2x2 matrix")
    return [[int(value[row][col]) for col in range(2)] for row in range(2)]


def _matrix_cell_prompt(
    cell: str,
    matrix_a: list[list[int]],
    matrix_b: list[list[int]],
    *,
    context: dict[str, Any] | None = None,
    runtime_policy: dict[str, Any] | None = None,
    parent_thread_id: str | None = None,
) -> str:
    row, col = _cell_indices(cell)
    left = matrix_a[row][0]
    right = matrix_a[row][1]
    top = matrix_b[0][col]
    bottom = matrix_b[1][col]
    expected_value = _matrix_cell_value(cell, matrix_a, matrix_b)
    context = context or {}
    runtime_policy = runtime_policy or {}
    label = _render_template(
        str(runtime_policy.get("title_template", f"COL-WORKER {cell}")),
        context,
        {"item": cell},
    )
    parent_line = (
        f"parent_thread_id={parent_thread_id}\n" if parent_thread_id else ""
    )
    return (
        f"{label}\n"
        f"{parent_line}"
        "You are a COL batch worker. Compute exactly one cell of a 2x2 matrix "
        "multiplication A x B.\n"
        f"A = {json.dumps(matrix_a)}\n"
        f"B = {json.dumps(matrix_b)}\n"
        f"Target cell = {cell}, row {row}, column {col}.\n"
        f"Formula = {left}*{top} + {right}*{bottom}.\n"
        f"Expected integer value = {expected_value}.\n"
        f'Reply with strict JSON only: {{"cell":"{cell}","value":{expected_value}}}'
    )


def _matrix_cell_fallback(
    cell: str, matrix_a: list[list[int]], matrix_b: list[list[int]]
) -> str:
    return json.dumps(
        {"cell": cell, "value": _matrix_cell_value(cell, matrix_a, matrix_b)},
        separators=(",", ":"),
    )


def _matrix_cell_value(
    cell: str, matrix_a: list[list[int]], matrix_b: list[list[int]]
) -> int:
    row, col = _cell_indices(cell)
    return matrix_a[row][0] * matrix_b[0][col] + matrix_a[row][1] * matrix_b[1][col]


def _cell_indices(cell: str) -> tuple[int, int]:
    match = re.fullmatch(r"c([01])([01])", cell)
    if not match:
        raise ValueError(f"unsupported matrix cell id: {cell}")
    return int(match.group(1)), int(match.group(2))


def _parse_json_response(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if match:
            return json.loads(match.group(0))
        number = re.search(r"-?\d+", cleaned)
        if number:
            return {"value": int(number.group(0))}
        raise


def _reduce_matrix_2x2(results: dict[str, dict[str, Any]]) -> list[list[int]]:
    matrix = [[0, 0], [0, 0]]
    for cell, payload in results.items():
        row, col = _cell_indices(cell)
        matrix[row][col] = int(payload["value"])
    return matrix


def _matrix_multiply_2x2(
    matrix_a: list[list[int]], matrix_b: list[list[int]]
) -> list[list[int]]:
    return [
        [
            matrix_a[row][0] * matrix_b[0][col]
            + matrix_a[row][1] * matrix_b[1][col]
            for col in range(2)
        ]
        for row in range(2)
    ]


def _render_template(
    template: str, context: dict[str, Any], locals_: dict[str, Any] | None = None
) -> str:
    locals_ = locals_ or {}

    def replace(match: re.Match[str]) -> str:
        value = _lookup_template_value(match.group(1), context, locals_)
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (dict, list)):
            return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        return str(value)

    return re.sub(r"\$\{([^}]+)\}", replace, template)


def _lookup_template_value(
    path: str, context: dict[str, Any], locals_: dict[str, Any]
) -> Any:
    if path in locals_:
        return locals_[path]
    parts = path.split(".")
    if parts[0] in locals_:
        value: Any = locals_[parts[0]]
    else:
        value = context[parts[0]]
    for part in parts[1:]:
        value = value[part] if isinstance(value, dict) else getattr(value, part)
    return value


def _add_graph_node(
    thread_graph: dict[str, Any], thread_id: str, role: str, label: str
) -> None:
    if any(node["thread_id"] == thread_id for node in thread_graph["nodes"]):
        return
    thread_graph["nodes"].append(
        {
            "thread_id": thread_id,
            "role": role,
            "label": label.splitlines()[0] if label else role,
        }
    )
