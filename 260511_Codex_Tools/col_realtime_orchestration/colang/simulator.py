from __future__ import annotations

from colang.models import (
    PIPELINE_STAGES,
    REGISTER_AGENTS,
    Hazard,
    IRProgram,
    RegisterState,
    Trace,
    TraceEvent,
)


def simulate_program(program: IRProgram) -> Trace:
    registers = {
        register: RegisterState(register=register, role=role)
        for register, role in REGISTER_AGENTS.items()
    }
    events: list[TraceEvent] = []
    produced: set[str] = set()
    verified_outputs: set[str] = set()
    fence_open = False
    agent_counter = 0

    for index, instruction in enumerate(program.instructions):
        hazards: list[Hazard] = []
        stage = _stage_for_instruction(instruction.op)
        register = _register_for_instruction(program, instruction.agent_ref)
        if register not in registers:
            registers[register] = RegisterState(register=register, role=instruction.agent_ref)
        state = registers[register]

        missing_inputs = [
            ref
            for ref in instruction.input_refs
            if ref not in produced
            and ref not in program.memory
            and ref not in program.data
            and ref != "seed"
            and not ref.startswith("x")
        ]
        if missing_inputs:
            hazards.append(
                Hazard(
                    code="DATA_DEPENDENCY",
                    message=f"Inputs are not produced yet: {', '.join(missing_inputs)}.",
                )
            )

        if instruction.op == "MAP":
            max_workers = int(instruction.schedule_policy.get("max_workers", 1))
            capability = program.capabilities.get(instruction.capability)
            max_agents = capability.max_agents if capability else 1
            if max_workers > max_agents:
                hazards.append(
                    Hazard(
                        code="FANOUT_EXCEEDED",
                        message=f"MAP requested {max_workers} workers but capability allows {max_agents}.",
                    )
                )

        if fence_open and instruction.op in {"REVIEW", "STORE"}:
            hazards.append(
                Hazard(
                    code="MEMFENCE_REQUIRES_VERIFY",
                    message="MEMFENCE requires VERIFY before review, store, or commit-style reads.",
                )
            )

        if instruction.op == "MEMFENCE":
            fence_open = True

        if instruction.op == "VERIFY":
            verified_outputs.add(instruction.output_schema)
            fence_open = False

        if instruction.op in {"STORE"}:
            l5_inputs = [
                ref
                for ref in instruction.input_refs
                if ref in program.memory and program.memory[ref].space == "L5"
            ]
            if l5_inputs and not any(ref in verified_outputs for ref in instruction.input_refs):
                hazards.append(
                    Hazard(
                        code="L5_REQUIRES_VERIFY",
                        message="L5 store attempted without a verified payload.",
                    )
                )

        if state.agent_id is None:
            agent_counter += 1
            state.agent_id = f"agent-{instruction.agent_ref}-{agent_counter}"
            status = "created"
        elif instruction.op in {"ACQUIRE", "REUSE", "CALL", "FETCH", "MAP"}:
            status = "reused"
        else:
            status = "executed"

        state.lease_count += 1
        state.current_output = instruction.output_schema
        produced.add(instruction.output_schema)

        memory_refs = [
            ref for ref in instruction.input_refs if ref in program.memory
        ]
        if instruction.memory_policy:
            memory_refs.append(instruction.memory_policy)

        events.append(
            TraceEvent(
                instruction_id=instruction.id,
                stage=stage,
                agent=state.agent_id,
                memory_refs=memory_refs,
                hazards=hazards,
                status=status if not hazards else f"{status}:hazard",
                duration=_duration_for(index),
                cost=_cost_for(program, instruction.capability),
            )
        )

    return Trace(events=events, registers=registers)


def _stage_for_instruction(op: str) -> str:
    if op in {"ACQUIRE", "REUSE", "SPILL", "RESTORE", "CAP", "PIPE", "STAGE"}:
        return "Plan"
    if op in {"LOAD", "FETCH", "CACHE", "INVALIDATE"}:
        return "Fetch"
    if op in {"VERIFY", "REVIEW", "ASSERT", "MEMFENCE"}:
        return "Verify"
    if op in {"STORE", "RET", "HALT", "RELEASE"}:
        return "Commit"
    if op in {"FLUSH", "STALL", "FORWARD", "BARRIER"}:
        return "Decode"
    return "Execute" if "Execute" in PIPELINE_STAGES else PIPELINE_STAGES[0]


def _register_for_instruction(program: IRProgram, agent_ref: str) -> str:
    if agent_ref in REGISTER_AGENTS:
        return agent_ref
    role = program.roles.get(agent_ref)
    if role:
        return role.register
    return agent_ref


def _duration_for(index: int) -> str:
    return f"{index + 1}u"


def _cost_for(program: IRProgram, capability_name: str) -> str:
    capability = program.capabilities.get(capability_name)
    return capability.max_cost if capability else "unknown"
