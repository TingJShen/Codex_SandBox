from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


REGISTER_AGENTS = {
    "R0": "orchestrator",
    "R1": "planner",
    "R2": "memory",
    "R3": "researcher",
    "R4": "worker",
    "R5": "reviewer",
    "R6": "verifier",
    "R7": "summarizer",
}

PIPELINE_STAGES = ["Decode", "Plan", "Fetch", "Execute", "Verify", "Commit"]

AGENT_OPS = {"ACQUIRE", "REUSE", "SPILL", "RESTORE", "RELEASE"}
EXECUTION_OPS = {"CALL", "HANDOFF", "RET", "TRAP", "HALT", "QUESTION"}
PIPELINE_OPS = {"PIPE", "STAGE", "FORWARD", "STALL", "FLUSH", "BARRIER"}
BATCH_OPS = {"MAP", "JOIN", "REDUCE"}
MEMORY_OPS = {"LOAD", "FETCH", "STORE", "CACHE", "INVALIDATE", "MEMFENCE"}
PERMISSION_OPS = {"CAP", "ELEVATE", "ASSERT", "VERIFY", "REVIEW", "ESCALATE"}
INSTRUCTION_OPS = (
    AGENT_OPS | EXECUTION_OPS | PIPELINE_OPS | BATCH_OPS | MEMORY_OPS | PERMISSION_OPS
)


@dataclass
class DataValue:
    name: str
    value: Any
    format: str = "auto"

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Capability:
    name: str
    level: str
    allowed_tools: list[str]
    network_scope: str
    write_scope: str
    external_effects: str = "none"
    max_agents: int = 1
    max_time: str = "10m"
    max_cost: str = "low"
    rollback_required: bool = True

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MemoryRef:
    name: str
    space: str
    path_or_key: str
    freshness: str
    source: str
    confidence: float
    read_cap: str
    write_cap: str
    ttl: str

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class HumanGate:
    name: str
    trigger: str
    risk_level: str
    question: str
    recommended_default: str
    timeout_action: str
    consequence_summary: str

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoleDecl:
    name: str
    register: str
    kind: str
    thread_id: str | None = None
    selector: str | None = None

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ArtifactDecl:
    name: str
    type: str
    path: str
    schema: str

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class MessageDecl:
    name: str
    from_role: str
    to_role: str
    artifact: str
    require_docs: bool = False

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ThreadSelectorDecl:
    name: str
    fields: dict[str, Any]

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaFieldDecl:
    name: str
    type: str
    values: list[str] = field(default_factory=list)
    required: bool = False

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SchemaDecl:
    name: str
    fields: dict[str, SchemaFieldDecl]

    def to_ir(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "fields": {
                name: field_decl.to_ir()
                for name, field_decl in sorted(self.fields.items())
            },
        }


@dataclass
class Instruction:
    id: str
    line: int
    op: str
    agent_ref: str
    input_refs: list[str]
    output_schema: str
    capability: str
    memory_policy: str | None = None
    schedule_policy: dict[str, Any] = field(default_factory=dict)
    runtime_policy: dict[str, Any] = field(default_factory=dict)
    human_gate: str | None = None
    trace_id: str | None = None

    def to_ir(self) -> dict[str, Any]:
        data = asdict(self)
        data["trace_id"] = self.trace_id or f"trace-{self.id}"
        return data


@dataclass
class Diagnostic:
    code: str
    message: str
    line: int | None = None
    instruction_id: str | None = None
    severity: str = "error"

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Hazard:
    code: str
    message: str
    severity: str = "warning"

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceEvent:
    instruction_id: str
    stage: str
    agent: str
    memory_refs: list[str]
    hazards: list[Hazard]
    status: str
    duration: str
    cost: str

    def to_ir(self) -> dict[str, Any]:
        data = asdict(self)
        data["hazards"] = [hazard.to_ir() for hazard in self.hazards]
        return data


@dataclass
class RegisterState:
    register: str
    role: str
    agent_id: str | None = None
    current_output: str | None = None
    lease_count: int = 0

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowNode:
    id: str
    kind: str
    label: str
    line: int | None = None
    role: str | None = None
    artifact: str | None = None
    condition: str | None = None
    instruction_id: str | None = None
    branch: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class WorkflowEdge:
    id: str
    from_node: str
    to_node: str
    kind: str
    label: str | None = None

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ControlBlock:
    id: str
    kind: str
    line: int
    condition: str | None = None
    max_rounds: int | None = None
    branches: list[str] = field(default_factory=list)
    artifact: str | None = None

    def to_ir(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Trace:
    events: list[TraceEvent]
    registers: dict[str, RegisterState]

    def to_ir(self) -> dict[str, Any]:
        return {
            "events": [event.to_ir() for event in self.events],
            "registers": {
                register: state.to_ir() for register, state in self.registers.items()
            },
        }


@dataclass
class IRProgram:
    name: str
    data: dict[str, DataValue]
    capabilities: dict[str, Capability]
    memory: dict[str, MemoryRef]
    human_gates: dict[str, HumanGate]
    instructions: list[Instruction]
    roles: dict[str, RoleDecl] = field(default_factory=dict)
    artifacts: dict[str, ArtifactDecl] = field(default_factory=dict)
    messages: dict[str, MessageDecl] = field(default_factory=dict)
    thread_selectors: dict[str, ThreadSelectorDecl] = field(default_factory=dict)
    schemas: dict[str, SchemaDecl] = field(default_factory=dict)
    workflow_nodes: list[WorkflowNode] = field(default_factory=list)
    workflow_edges: list[WorkflowEdge] = field(default_factory=list)
    control_blocks: list[ControlBlock] = field(default_factory=list)
    workflow_roots: list[str] = field(default_factory=list)

    def to_ir(self) -> dict[str, Any]:
        return {
            "version": "0.3",
            "name": self.name,
            "register_file": REGISTER_AGENTS,
            "memory_hierarchy": {
                "L0": "register context",
                "L1": "current thread",
                "L2": "task scratch",
                "L3": "local knowledge/index",
                "L4": "web/external",
                "L5": "long-term memory",
            },
            "pipeline": PIPELINE_STAGES,
            "data": {
                name: data_value.to_ir()
                for name, data_value in sorted(self.data.items())
            },
            "capabilities": {
                name: capability.to_ir()
                for name, capability in sorted(self.capabilities.items())
            },
            "memory": {
                name: memory_ref.to_ir() for name, memory_ref in sorted(self.memory.items())
            },
            "human_gates": {
                name: gate.to_ir() for name, gate in sorted(self.human_gates.items())
            },
            "roles": {
                name: role.to_ir() for name, role in sorted(self.roles.items())
            },
            "artifacts": {
                name: artifact.to_ir()
                for name, artifact in sorted(self.artifacts.items())
            },
            "messages": {
                name: message.to_ir()
                for name, message in sorted(self.messages.items())
            },
            "thread_selectors": {
                name: selector.to_ir()
                for name, selector in sorted(self.thread_selectors.items())
            },
            "schemas": {
                name: schema.to_ir() for name, schema in sorted(self.schemas.items())
            },
            "instructions": [instruction.to_ir() for instruction in self.instructions],
            "workflow": {
                "nodes": [node.to_ir() for node in self.workflow_nodes],
                "edges": [edge.to_ir() for edge in self.workflow_edges],
                "control_blocks": [
                    block.to_ir() for block in self.control_blocks
                ],
                "roots": list(self.workflow_roots),
            },
        }
