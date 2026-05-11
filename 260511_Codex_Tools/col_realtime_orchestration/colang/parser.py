from __future__ import annotations

import re
from typing import Any

from colang.models import (
    ArtifactDecl,
    ControlBlock,
    REGISTER_AGENTS,
    Capability,
    DataValue,
    HumanGate,
    IRProgram,
    INSTRUCTION_OPS,
    Instruction,
    MessageDecl,
    MemoryRef,
    RoleDecl,
    SchemaDecl,
    SchemaFieldDecl,
    ThreadSelectorDecl,
    WorkflowEdge,
    WorkflowNode,
)


PROGRAM_RE = re.compile(r'^program\s+"(?P<name>[^"]+)"\s*\{\s*$')
KV_RE = re.compile(r'(?P<key>[A-Za-z_][A-Za-z0-9_]*)=(?P<value>"[^"]*"|\[[^\]]*\]|[^\s]+)')


def parse_col(source: str) -> IRProgram:
    source = source.lstrip("\ufeff")
    nonempty = _logical_lines(source)
    if not nonempty:
        raise ValueError("COL source is empty")

    first_line, first = nonempty[0]
    match = PROGRAM_RE.match(first)
    if not match:
        raise ValueError(f"line {first_line}: expected program header")

    if nonempty[-1][1] != "}":
        raise ValueError(f"line {nonempty[-1][0]}: expected closing '}}'")

    capabilities: dict[str, Capability] = {}
    data: dict[str, DataValue] = {}
    memory: dict[str, MemoryRef] = {}
    human_gates: dict[str, HumanGate] = {}
    instructions: list[Instruction] = []
    roles: dict[str, RoleDecl] = {}
    artifacts: dict[str, ArtifactDecl] = {}
    messages: dict[str, MessageDecl] = {}
    thread_selectors: dict[str, ThreadSelectorDecl] = {}
    schemas: dict[str, SchemaDecl] = {}
    workflow_nodes: list[WorkflowNode] = []
    workflow_edges: list[WorkflowEdge] = []
    control_blocks: list[ControlBlock] = []
    counters = {"node": 0, "edge": 0, "block": 0}

    body = nonempty[1:-1]

    def add_node(
        kind: str,
        label: str,
        line: int | None,
        **kwargs: Any,
    ) -> str:
        counters["node"] += 1
        node_id = f"W{counters['node']:03d}"
        workflow_nodes.append(
            WorkflowNode(id=node_id, kind=kind, label=label, line=line, **kwargs)
        )
        return node_id

    def add_edge(
        from_node: str,
        to_node: str,
        kind: str,
        label: str | None = None,
    ) -> None:
        counters["edge"] += 1
        workflow_edges.append(
            WorkflowEdge(
                id=f"E{counters['edge']:03d}",
                from_node=from_node,
                to_node=to_node,
                kind=kind,
                label=label,
            )
        )

    def add_block(
        kind: str,
        line: int,
        **kwargs: Any,
    ) -> str:
        counters["block"] += 1
        block_id = f"B{counters['block']:03d}"
        control_blocks.append(ControlBlock(id=block_id, kind=kind, line=line, **kwargs))
        return block_id

    def get_node(node_id: str) -> WorkflowNode:
        for node in workflow_nodes:
            if node.id == node_id:
                return node
        raise KeyError(node_id)

    def parse_block(index: int) -> tuple[int, list[str]]:
        local_nodes: list[str] = []
        while index < len(body):
            line_number, line = body[index]
            if line == "}":
                return index + 1, local_nodes
            next_index, nodes = parse_statement(index)
            local_nodes.extend(nodes)
            index = next_index
        return index, local_nodes

    def parse_statement(index: int) -> tuple[int, list[str]]:
        line_number, line = body[index]
        head, rest = _split_head(line, line_number)
        head_upper = head.upper()
        if head == "cap":
            capability = _parse_capability(rest, line_number)
            capabilities[capability.name] = capability
            return index + 1, []
        if head == "data":
            data_value = _parse_data(rest, line_number)
            data[data_value.name] = data_value
            return index + 1, []
        if head == "memory":
            memory_ref = _parse_memory(rest, line_number)
            memory[memory_ref.name] = memory_ref
            return index + 1, []
        if head == "gate":
            gate = _parse_gate(rest, line_number)
            human_gates[gate.name] = gate
            return index + 1, []
        if head_upper == "ROLE":
            role = _parse_role(rest, line_number)
            roles[role.name] = role
            node_id = add_node(
                "role",
                f"ROLE {role.name}",
                line_number,
                role=role.name,
                metadata={"register": role.register, "kind": role.kind},
            )
            return index + 1, [node_id]
        if head_upper == "THREAD_SELECTOR":
            selector = _parse_thread_selector(rest, line_number)
            thread_selectors[selector.name] = selector
            node_id = add_node(
                "thread_selector",
                f"THREAD_SELECTOR {selector.name}",
                line_number,
                metadata=selector.fields,
            )
            return index + 1, [node_id]
        if head_upper == "SCHEMA":
            return parse_schema(index, line_number, line)
        if head_upper == "ARTIFACT":
            artifact = _parse_artifact(rest, line_number)
            artifacts[artifact.name] = artifact
            node_id = add_node(
                "artifact",
                f"ARTIFACT {artifact.name}",
                line_number,
                artifact=artifact.name,
                metadata={"path": artifact.path, "schema": artifact.schema},
            )
            return index + 1, [node_id]
        if head_upper == "MESSAGE":
            message = _parse_message(rest, line_number)
            messages[message.name] = message
            node_id = add_node(
                "message",
                f"MESSAGE {message.name}",
                line_number,
                artifact=message.artifact,
                metadata={
                    "from": message.from_role,
                    "to": message.to_role,
                    "require_docs": message.require_docs,
                },
            )
            add_edge(
                f"role:{message.from_role}",
                f"role:{message.to_role}",
                "message",
                message.artifact,
            )
            return index + 1, [node_id]
        if head_upper == "WAIT":
            artifact_name = rest.strip()
            if not artifact_name:
                raise ValueError(f"line {line_number}: WAIT requires an artifact")
            node_id = add_node(
                "wait",
                f"WAIT {artifact_name}",
                line_number,
                artifact=artifact_name,
            )
            add_edge(f"artifact:{artifact_name}", node_id, "wait", artifact_name)
            return index + 1, [node_id]
        if head_upper == "AFTER":
            match = re.match(r"^(?P<artifact>[A-Za-z_][A-Za-z0-9_]*)\s*\{$", rest)
            if not match:
                raise ValueError(f"line {line_number}: AFTER requires an artifact block")
            artifact_name = match.group("artifact")
            node_id = add_node(
                "after",
                f"AFTER {artifact_name}",
                line_number,
                artifact=artifact_name,
            )
            add_edge(f"artifact:{artifact_name}", node_id, "wait", artifact_name)
            add_block("AFTER", line_number, artifact=artifact_name)
            next_index, child_nodes = parse_block(index + 1)
            get_node(node_id).metadata["children"] = child_nodes
            if child_nodes:
                add_edge(node_id, child_nodes[0], "control")
            return next_index, [node_id]
        if head_upper == "PARALLEL":
            if rest.strip() != "{":
                raise ValueError(f"line {line_number}: PARALLEL requires a block")
            return parse_parallel(index, line_number)
        if head_upper == "LOOP":
            return parse_loop(index, line_number, line)
        if head_upper == "IF":
            return parse_if(index, line_number, line)
        if head_upper == "ELSE":
            return parse_orphan_else(index, line_number, line)
        if head_upper == "EMIT":
            name, fields = _parse_named_fields(rest, line_number, "emit")
            fields["name"] = name
            node_id = add_node(
                "emit",
                f"EMIT {name}",
                line_number,
                artifact=str(fields.get("artifact", "")) or None,
                role=str(fields.get("from", "")) or None,
                metadata=fields,
            )
            return index + 1, [node_id]
        if head_upper in INSTRUCTION_OPS:
            instruction = _parse_instruction(
                op=head_upper,
                rest=rest,
                line=line_number,
                index=len(instructions) + 1,
            )
            instructions.append(instruction)
            node_id = add_node(
                instruction.op.lower(),
                f"{instruction.op} {instruction.agent_ref} -> {instruction.output_schema}",
                line_number,
                role=str(instruction.runtime_policy.get("role", instruction.agent_ref)),
                instruction_id=instruction.id,
            )
            return index + 1, [node_id]
        raise ValueError(f"line {line_number}: unknown statement '{head}'")

    def parse_schema(index: int, line_number: int, line: str) -> tuple[int, list[str]]:
        match = re.match(r"^SCHEMA\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\{$", line, flags=re.I)
        if not match:
            raise ValueError(f"line {line_number}: SCHEMA requires a named block")
        schema_name = match.group("name")
        fields: dict[str, SchemaFieldDecl] = {}
        next_index = index + 1
        while next_index < len(body):
            field_line_number, field_line = body[next_index]
            if field_line == "}":
                break
            field_head, field_rest = _split_head(field_line, field_line_number)
            if field_head.upper() != "FIELD":
                raise ValueError(f"line {field_line_number}: SCHEMA body requires FIELD")
            field = _parse_schema_field(field_rest, field_line_number)
            fields[field.name] = field
            next_index += 1
        if next_index >= len(body) or body[next_index][1] != "}":
            raise ValueError(f"line {line_number}: SCHEMA block is not closed")
        schemas[schema_name] = SchemaDecl(name=schema_name, fields=fields)
        node_id = add_node(
            "schema",
            f"SCHEMA {schema_name}",
            line_number,
            metadata={"fields": list(fields)},
        )
        return next_index + 1, [node_id]

    def parse_parallel(index: int, line_number: int) -> tuple[int, list[str]]:
        fork_id = add_node("parallel_fork", "PARALLEL fork", line_number)
        branch_names: list[str] = []
        branch_last_nodes: list[str] = []
        branch_entries: list[dict[str, Any]] = []
        next_index = index + 1
        while next_index < len(body):
            branch_line_number, branch_line = body[next_index]
            if branch_line == "}":
                break
            match = re.match(
                r"^BRANCH\s+(?P<name>[A-Za-z_][A-Za-z0-9_-]*)\s*\{$",
                branch_line,
                flags=re.I,
            )
            if not match:
                raise ValueError(
                    f"line {branch_line_number}: PARALLEL body requires BRANCH blocks"
                )
            branch_name = match.group("name")
            branch_id = add_node(
                "branch",
                f"BRANCH {branch_name}",
                branch_line_number,
                branch=branch_name,
            )
            add_edge(fork_id, branch_id, "control")
            branch_names.append(branch_name)
            next_index, branch_nodes = parse_block(next_index + 1)
            branch_entries.append({"name": branch_name, "nodes": branch_nodes})
            if branch_nodes:
                add_edge(branch_id, branch_nodes[0], "control")
                branch_last_nodes.append(branch_nodes[-1])
            else:
                branch_last_nodes.append(branch_id)
        if next_index >= len(body) or body[next_index][1] != "}":
            raise ValueError(f"line {line_number}: PARALLEL block is not closed")
        join_id = add_node("parallel_join", "PARALLEL join", line_number)
        for last_node in branch_last_nodes:
            add_edge(last_node, join_id, "control")
        get_node(fork_id).metadata["branches"] = branch_entries
        get_node(fork_id).metadata["join"] = join_id
        add_block("PARALLEL", line_number, branches=branch_names)
        return next_index + 1, [fork_id]

    def parse_loop(index: int, line_number: int, line: str) -> tuple[int, list[str]]:
        match = re.match(
            r'^LOOP\s+UNTIL\s+(?P<condition>.+?)(?:\s+MAX_ROUNDS\s+(?P<max_rounds>-?\d+))?\s*\{$',
            line,
            flags=re.I,
        )
        if not match:
            raise ValueError(f"line {line_number}: LOOP requires UNTIL ... block")
        condition = match.group("condition").strip()
        max_rounds = (
            int(match.group("max_rounds"))
            if match.group("max_rounds") is not None
            else None
        )
        loop_id = add_node(
            "loop",
            f"LOOP UNTIL {condition}",
            line_number,
            condition=condition,
            metadata={"max_rounds": max_rounds},
        )
        add_block("LOOP", line_number, condition=condition, max_rounds=max_rounds)
        next_index, child_nodes = parse_block(index + 1)
        get_node(loop_id).metadata["body"] = child_nodes
        if child_nodes:
            add_edge(loop_id, child_nodes[0], "control")
            add_edge(child_nodes[-1], loop_id, "loop_back", f"max_rounds={max_rounds}")
        add_edge(loop_id, "loop:exit", "exit", condition)
        return next_index, [loop_id]

    def parse_if(index: int, line_number: int, line: str) -> tuple[int, list[str]]:
        match = re.match(r"^IF\s+(?P<condition>.+)\s*\{$", line, flags=re.I)
        if not match:
            raise ValueError(f"line {line_number}: IF requires a condition block")
        condition = match.group("condition").strip()
        condition_id = add_node(
            "condition",
            f"IF {condition}",
            line_number,
            condition=condition,
        )
        add_block("IF", line_number, condition=condition)
        next_index, true_nodes = parse_block(index + 1)
        get_node(condition_id).metadata["true_nodes"] = true_nodes
        if true_nodes:
            add_edge(condition_id, true_nodes[0], "true", condition)
        all_nodes = [condition_id, *true_nodes]
        if next_index < len(body):
            else_line_number, else_line = body[next_index]
            if re.match(r"^ELSE\s*\{$", else_line, flags=re.I):
                next_index, false_nodes = parse_block(next_index + 1)
                get_node(condition_id).metadata["false_nodes"] = false_nodes
                if false_nodes:
                    add_edge(condition_id, false_nodes[0], "false", condition)
                all_nodes.extend(false_nodes)
        return next_index, [condition_id]

    def parse_orphan_else(index: int, line_number: int, line: str) -> tuple[int, list[str]]:
        if not re.match(r"^ELSE\s*\{$", line, flags=re.I):
            raise ValueError(f"line {line_number}: ELSE requires a block")
        node_id = add_node("else", "ELSE", line_number)
        add_block("ELSE", line_number)
        next_index, child_nodes = parse_block(index + 1)
        return next_index, [node_id, *child_nodes]

    index, workflow_roots = parse_block(0)
    if index != len(body):
        line_number, line = body[index]
        raise ValueError(f"line {line_number}: unexpected statement '{line}'")

    return IRProgram(
        name=match.group("name"),
        data=data,
        capabilities=capabilities,
        memory=memory,
        human_gates=human_gates,
        instructions=instructions,
        roles=roles,
        artifacts=artifacts,
        messages=messages,
        thread_selectors=thread_selectors,
        schemas=schemas,
        workflow_nodes=workflow_nodes,
        workflow_edges=workflow_edges,
        control_blocks=control_blocks,
        workflow_roots=workflow_roots,
    )


def _logical_lines(source: str) -> list[tuple[int, str]]:
    result: list[tuple[int, str]] = []
    for idx, raw_line in enumerate(source.splitlines(), start=1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        if re.match(r"^\}\s+ELSE\b", line, flags=re.I):
            result.append((idx, "}"))
            result.append((idx, re.sub(r"^\}\s*", "", line)))
        else:
            result.append((idx, line))
    return result


def _strip_comment(line: str) -> str:
    in_quote = False
    for idx, char in enumerate(line):
        if char == '"':
            in_quote = not in_quote
        if char == "#" and not in_quote:
            return line[:idx]
    return line


def _split_head(line: str, line_number: int) -> tuple[str, str]:
    parts = line.split(maxsplit=1)
    if not parts:
        raise ValueError(f"line {line_number}: empty statement")
    return parts[0], parts[1] if len(parts) > 1 else ""


def _parse_key_values(text: str, line_number: int) -> dict[str, Any]:
    result: dict[str, Any] = {}
    consumed: list[tuple[int, int]] = []
    for match in KV_RE.finditer(text):
        result[match.group("key")] = _parse_value(match.group("value"))
        consumed.append(match.span())

    leftovers = _remove_spans(text, consumed).strip()
    if leftovers:
        raise ValueError(f"line {line_number}: could not parse '{leftovers}'")
    return result


def _remove_spans(text: str, spans: list[tuple[int, int]]) -> str:
    chars = list(text)
    for start, end in spans:
        for idx in range(start, end):
            chars[idx] = " "
    return "".join(chars)


def _parse_value(value: str) -> Any:
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"') for item in inner.split(",")]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    if re.fullmatch(r"-?\d+\.\d+", value):
        return float(value)
    return value


def _parse_capability(rest: str, line_number: int) -> Capability:
    name, fields = _parse_named_fields(rest, line_number, "capability")
    _require(fields, line_number, ["level", "tools", "network", "write"])
    return Capability(
        name=name,
        level=str(fields["level"]),
        allowed_tools=list(fields["tools"]),
        network_scope=str(fields["network"]),
        write_scope=str(fields["write"]),
        external_effects=str(fields.get("external", "none")),
        max_agents=int(fields.get("max_agents", 1)),
        max_time=str(fields.get("max_time", "10m")),
        max_cost=str(fields.get("max_cost", "low")),
        rollback_required=bool(fields.get("rollback", True)),
    )


def _parse_data(rest: str, line_number: int) -> DataValue:
    name, fields = _parse_named_fields(rest, line_number, "data")
    _require(fields, line_number, ["value"])
    return DataValue(
        name=name,
        value=fields["value"],
        format=str(fields.get("format", "auto")),
    )


def _parse_memory(rest: str, line_number: int) -> MemoryRef:
    name, fields = _parse_named_fields(rest, line_number, "memory")
    _require(
        fields,
        line_number,
        ["space", "key", "freshness", "source", "confidence", "read", "write", "ttl"],
    )
    return MemoryRef(
        name=name,
        space=str(fields["space"]),
        path_or_key=str(fields["key"]),
        freshness=str(fields["freshness"]),
        source=str(fields["source"]),
        confidence=float(fields["confidence"]),
        read_cap=str(fields["read"]),
        write_cap=str(fields["write"]),
        ttl=str(fields["ttl"]),
    )


def _parse_gate(rest: str, line_number: int) -> HumanGate:
    name, fields = _parse_named_fields(rest, line_number, "human gate")
    _require(
        fields,
        line_number,
        ["trigger", "risk", "question", "default", "timeout", "consequence"],
    )
    question = str(fields["question"])
    if len(question) > 180:
        raise ValueError(f"line {line_number}: question must fit a 30-second prompt")
    return HumanGate(
        name=name,
        trigger=str(fields["trigger"]),
        risk_level=str(fields["risk"]),
        question=question,
        recommended_default=str(fields["default"]),
        timeout_action=str(fields["timeout"]),
        consequence_summary=str(fields["consequence"]),
    )


def _parse_role(rest: str, line_number: int) -> RoleDecl:
    name, fields = _parse_named_fields(rest, line_number, "role")
    _require(fields, line_number, ["register", "kind"])
    return RoleDecl(
        name=name,
        register=str(fields["register"]),
        kind=str(fields["kind"]),
        thread_id=str(fields["thread_id"]) if "thread_id" in fields else None,
        selector=str(fields["selector"]) if "selector" in fields else None,
    )


def _parse_artifact(rest: str, line_number: int) -> ArtifactDecl:
    name, fields = _parse_named_fields(rest, line_number, "artifact")
    _require(fields, line_number, ["type", "path", "schema"])
    return ArtifactDecl(
        name=name,
        type=str(fields["type"]),
        path=str(fields["path"]),
        schema=str(fields["schema"]),
    )


def _parse_message(rest: str, line_number: int) -> MessageDecl:
    name, fields = _parse_named_fields(rest, line_number, "message")
    _require(fields, line_number, ["from", "to", "artifact"])
    return MessageDecl(
        name=name,
        from_role=str(fields["from"]),
        to_role=str(fields["to"]),
        artifact=str(fields["artifact"]),
        require_docs=bool(fields.get("require_docs", False)),
    )


def _parse_thread_selector(rest: str, line_number: int) -> ThreadSelectorDecl:
    name, fields = _parse_named_fields(rest, line_number, "thread selector")
    return ThreadSelectorDecl(name=name, fields=fields)


def _parse_schema_field(rest: str, line_number: int) -> SchemaFieldDecl:
    name, fields = _parse_named_fields(rest, line_number, "schema field")
    _require(fields, line_number, ["type"])
    values = fields.get("values", [])
    if not isinstance(values, list):
        values = [str(values)]
    return SchemaFieldDecl(
        name=name,
        type=str(fields["type"]),
        values=[str(value) for value in values],
        required=bool(fields.get("required", False)),
    )


def _parse_named_fields(
    rest: str, line_number: int, label: str
) -> tuple[str, dict[str, Any]]:
    name_parts = rest.split(maxsplit=1)
    if not name_parts or "=" in name_parts[0]:
        raise ValueError(f"line {line_number}: {label} requires a name")
    name = name_parts[0]
    fields = _parse_key_values(name_parts[1] if len(name_parts) > 1 else "", line_number)
    return name, fields


def _parse_instruction(op: str, rest: str, line: int, index: int) -> Instruction:
    parts = rest.split(maxsplit=1)
    if not parts:
        raise ValueError(f"line {line}: instruction requires an agent register")
    agent_ref = parts[0]
    if agent_ref not in REGISTER_AGENTS and not re.fullmatch(
        r"[A-Za-z_][A-Za-z0-9_]*", agent_ref
    ):
        raise ValueError(f"line {line}: unknown agent register '{agent_ref}'")
    fields = _parse_key_values(parts[1] if len(parts) > 1 else "", line)
    _require(fields, line, ["inputs", "output", "cap"])

    schedule_policy: dict[str, Any] = {}
    for key in ("items", "max_workers", "reduce", "shared_write"):
        if key in fields:
            schedule_policy[key] = fields[key]
    runtime_policy = {
        key: value
        for key, value in fields.items()
        if key
        not in {
            "inputs",
            "output",
            "cap",
            "memory",
            "gate",
            "items",
            "max_workers",
            "reduce",
            "shared_write",
        }
    }

    return Instruction(
        id=f"I{index:03d}",
        line=line,
        op=op,
        agent_ref=agent_ref,
        input_refs=list(fields["inputs"]),
        output_schema=str(fields["output"]),
        capability=str(fields["cap"]),
        memory_policy=fields.get("memory"),
        schedule_policy=schedule_policy,
        runtime_policy=runtime_policy,
        human_gate=fields.get("gate"),
        trace_id=f"trace-I{index:03d}",
    )


def _require(fields: dict[str, Any], line_number: int, required: list[str]) -> None:
    missing = [field for field in required if field not in fields]
    if missing:
        raise ValueError(f"line {line_number}: missing required field {missing[0]}")
