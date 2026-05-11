from __future__ import annotations

from colang.models import Diagnostic, IRProgram


def validate_program(program: IRProgram) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    verified_outputs: set[str] = set()
    produced_outputs: set[str] = set()

    diagnostics.extend(_validate_workflow_declarations(program))

    for instruction in program.instructions:
        capability = program.capabilities.get(instruction.capability)
        if capability is None:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_CAPABILITY",
                    message=f"Instruction uses unknown capability '{instruction.capability}'.",
                    line=instruction.line,
                    instruction_id=instruction.id,
                )
            )
            continue

        if capability.level == "L4":
            diagnostics.append(
                Diagnostic(
                    code="FORBIDDEN_CAPABILITY",
                    message="L4 capabilities are forbidden until the plan is rewritten to reduce risk.",
                    line=instruction.line,
                    instruction_id=instruction.id,
                )
            )

        if _level_number(capability.level) >= 3 and not instruction.human_gate:
            diagnostics.append(
                Diagnostic(
                    code="HUMAN_GATE_REQUIRED",
                    message="L3 instructions require a HumanGate with a 30-second decision prompt.",
                    line=instruction.line,
                    instruction_id=instruction.id,
                )
            )

        if instruction.human_gate and instruction.human_gate not in program.human_gates:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_HUMAN_GATE",
                    message=f"Instruction references unknown human gate '{instruction.human_gate}'.",
                    line=instruction.line,
                    instruction_id=instruction.id,
                )
            )

        for ref_name in instruction.input_refs:
            memory_ref = program.memory.get(ref_name)
            if not memory_ref:
                continue
            required_read = program.capabilities.get(memory_ref.read_cap)
            if required_read and not _capability_allows(capability.level, required_read.level):
                diagnostics.append(
                    Diagnostic(
                        code="MEMORY_READ_CAP_REQUIRED",
                        message=(
                            f"Memory '{ref_name}' requires read capability "
                            f"'{memory_ref.read_cap}'."
                        ),
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )
            if _is_stale(memory_ref.freshness, memory_ref.ttl) and instruction.op not in {
                "FETCH",
                "CACHE",
                "INVALIDATE",
            }:
                diagnostics.append(
                    Diagnostic(
                        code="KNOWLEDGE_REFRESH_REQUIRED",
                        message=(
                            f"Memory '{ref_name}' is stale and must be refreshed "
                            "before normal execution."
                        ),
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )

        if instruction.op == "STORE":
            for ref_name in instruction.input_refs:
                memory_ref = program.memory.get(ref_name)
                if not memory_ref:
                    continue
                required_write = program.capabilities.get(memory_ref.write_cap)
                if required_write and not _capability_allows(
                    capability.level, required_write.level
                ):
                    diagnostics.append(
                        Diagnostic(
                            code="MEMORY_WRITE_CAP_REQUIRED",
                            message=(
                                f"Memory '{ref_name}' requires write capability "
                                f"'{memory_ref.write_cap}'."
                            ),
                            line=instruction.line,
                            instruction_id=instruction.id,
                        )
                    )

        if instruction.op == "MAP":
            if not instruction.schedule_policy.get("reduce"):
                diagnostics.append(
                    Diagnostic(
                        code="MAP_REDUCE_REQUIRED",
                        message="MAP must declare a reduce strategy.",
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )
            if instruction.schedule_policy.get("shared_write") is not False:
                diagnostics.append(
                    Diagnostic(
                        code="MAP_SHARED_WRITE",
                        message="MAP workers cannot directly write shared results.",
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )
            roles = instruction.runtime_policy.get("roles")
            if isinstance(roles, list) and len(set(roles)) > 1:
                diagnostics.append(
                    Diagnostic(
                        code="MAP_HETEROGENEOUS_ROLES",
                        message=(
                            "MAP is for homogeneous batch workers; use "
                            "PARALLEL/BRANCH for heterogeneous role collaboration."
                        ),
                        line=instruction.line,
                        instruction_id=instruction.id,
                        severity="warning",
                    )
                )

        l5_inputs = [
            ref
            for ref in instruction.input_refs
            if ref in program.memory and program.memory[ref].space == "L5"
        ]
        if instruction.op == "STORE" and l5_inputs:
            non_memory_inputs = [
                ref for ref in instruction.input_refs if ref not in program.memory
            ]
            if not any(ref in verified_outputs for ref in non_memory_inputs):
                diagnostics.append(
                    Diagnostic(
                        code="L5_REQUIRES_VERIFY",
                        message="L5 long-term memory writes require a verified input.",
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )
            if not instruction.human_gate:
                diagnostics.append(
                    Diagnostic(
                        code="L5_REQUIRES_HUMAN_GATE",
                        message="L5 long-term memory writes require explicit human acceptance.",
                        line=instruction.line,
                        instruction_id=instruction.id,
                    )
                )

        if instruction.op == "VERIFY":
            verified_outputs.add(instruction.output_schema)
        produced_outputs.add(instruction.output_schema)

    return diagnostics


def _validate_workflow_declarations(program: IRProgram) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = []
    known_roles = set(program.roles) | {"human"}
    known_artifacts = set(program.artifacts)
    known_schemas = set(program.schemas) | {"role_message", "test_report"}
    produced_outputs = {instruction.output_schema for instruction in program.instructions}

    for role in program.roles.values():
        if role.selector and role.selector not in program.thread_selectors:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_THREAD_SELECTOR",
                    message=(
                        f"Role '{role.name}' references unknown thread selector "
                        f"'{role.selector}'."
                    ),
                    severity="error",
                )
            )

    for artifact in program.artifacts.values():
        if artifact.schema not in known_schemas:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_ARTIFACT_SCHEMA",
                    message=(
                        f"Artifact '{artifact.name}' references unknown schema "
                        f"'{artifact.schema}'."
                    ),
                    severity="error",
                )
            )

    for message in program.messages.values():
        if message.from_role not in known_roles or message.to_role not in known_roles:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_MESSAGE_ROLE",
                    message=(
                        f"Message '{message.name}' references an undeclared role."
                    ),
                    severity="error",
                )
            )
        if message.artifact not in known_artifacts:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_MESSAGE_ARTIFACT",
                    message=(
                        f"Message '{message.name}' references unknown artifact "
                        f"'{message.artifact}'."
                    ),
                    severity="error",
                )
            )

    for block in program.control_blocks:
        if block.kind == "ELSE":
            diagnostics.append(
                Diagnostic(
                    code="ORPHAN_ELSE",
                    message="ELSE must immediately follow an IF block.",
                    line=block.line,
                )
            )
        if block.kind == "LOOP" and (
            block.max_rounds is None or block.max_rounds <= 0
        ):
            diagnostics.append(
                Diagnostic(
                    code="LOOP_MAX_ROUNDS_REQUIRED",
                    message="LOOP requires a positive MAX_ROUNDS value.",
                    line=block.line,
                )
            )
        if block.kind == "PARALLEL":
            if len(block.branches) < 2:
                diagnostics.append(
                    Diagnostic(
                        code="PARALLEL_BRANCH_COUNT",
                        message="PARALLEL requires at least two BRANCH blocks.",
                        line=block.line,
                    )
                )
            if len(block.branches) != len(set(block.branches)):
                diagnostics.append(
                    Diagnostic(
                        code="PARALLEL_BRANCH_DUPLICATE",
                        message="BRANCH names must be unique inside a PARALLEL block.",
                        line=block.line,
                    )
                )

    for node in program.workflow_nodes:
        if node.kind not in {"wait", "after"}:
            continue
        artifact = node.artifact
        if artifact and artifact not in known_artifacts and artifact not in produced_outputs:
            diagnostics.append(
                Diagnostic(
                    code="UNKNOWN_WAIT_ARTIFACT",
                    message=f"{node.label} references unknown artifact '{artifact}'.",
                    line=node.line,
                )
            )

    return diagnostics


def _level_number(level: str) -> int:
    if level.startswith("L") and level[1:].isdigit():
        return int(level[1:])
    return 0


def _capability_allows(actual_level: str, required_level: str) -> bool:
    return _level_number(actual_level) >= _level_number(required_level)


def _is_stale(freshness: str, ttl: str) -> bool:
    return freshness not in {"fresh", "verified"} or ttl == "expired"
