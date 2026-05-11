from __future__ import annotations

from html import escape

from colang.models import IRProgram, Trace


def render_html(program: IRProgram, trace: Trace) -> str:
    business_flow = _business_flow(program)
    artifact_board = _artifact_board(program)
    register_rows = "\n".join(
        f"<tr><td>{escape(name)}</td><td>{escape(state.role)}</td>"
        f"<td>{escape(state.agent_id or '-')}</td>"
        f"<td>{escape(state.current_output or '-')}</td>"
        f"<td>{state.lease_count}</td></tr>"
        for name, state in trace.registers.items()
    )
    timeline = "\n".join(
        f"<div class='event {escape(event.stage.lower())}'>"
        f"<strong>{escape(event.instruction_id)}</strong>"
        f"<span>{escape(event.stage)}</span>"
        f"<small>{escape(event.status)}</small>"
        f"{_hazard_badges(event)}</div>"
        for event in trace.events
    )
    graph_edges = "\n".join(
        f"<li>{escape(instruction.agent_ref)} -> {escape(instruction.output_schema)}"
        f" <code>{escape(instruction.op)}</code></li>"
        for instruction in program.instructions
    )
    memory_rows = "\n".join(
        f"<tr><td>{escape(name)}</td><td>{escape(ref.space)}</td>"
        f"<td>{escape(ref.path_or_key)}</td><td>{escape(ref.read_cap)}</td>"
        f"<td>{escape(ref.write_cap)}</td></tr>"
        for name, ref in program.memory.items()
    )
    batch_cards = "\n".join(
        _batch_card(instruction)
        for instruction in program.instructions
        if instruction.op == "MAP"
    ) or "<p>No MAP instructions in this program.</p>"

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>COL Trace - {escape(program.name)}</title>
  <style>
    body {{ font-family: Segoe UI, Arial, sans-serif; margin: 0; background: #f7f8fb; color: #20242c; }}
    header {{ padding: 24px 32px; background: #17202a; color: white; }}
    main {{ padding: 24px 32px; display: grid; gap: 20px; }}
    section {{ background: white; border: 1px solid #dde2ea; border-radius: 8px; padding: 18px; }}
    h2 {{ margin: 0 0 12px; font-size: 18px; }}
    h3 {{ margin: 16px 0 10px; font-size: 15px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border-bottom: 1px solid #e6e9ef; padding: 8px; text-align: left; font-size: 14px; }}
    .timeline {{ display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; }}
    .event {{ min-width: 130px; border: 1px solid #d7dce5; border-radius: 6px; padding: 10px; background: #fbfcff; }}
    .event span, .event small {{ display: block; margin-top: 5px; }}
    .hazard {{ display: inline-block; margin-top: 8px; padding: 2px 6px; border-radius: 4px; background: #fff2d6; color: #7a4b00; font-size: 12px; }}
    .batch {{ display: inline-grid; grid-template-columns: repeat(4, 32px); gap: 6px; margin-top: 8px; }}
    .cell {{ height: 28px; border-radius: 4px; background: #dfe9ff; display: grid; place-items: center; font-size: 12px; }}
    .flow {{ display: grid; gap: 10px; }}
    .flow-node {{ border-left: 4px solid #4169a8; background: #f8fbff; padding: 9px 10px; border-radius: 6px; }}
    .flow-node.condition {{ border-left-color: #a87900; transform: skew(-4deg); }}
    .flow-node.condition > * {{ transform: skew(4deg); }}
    .flow-node.loop {{ border-left-color: #8a4fb0; }}
    .flow-node.parallel_fork, .flow-node.parallel_join, .flow-node.branch {{ border-left-color: #2d7d68; }}
    .flow-edge {{ color: #526070; font-size: 13px; }}
    .pill {{ display: inline-block; margin-left: 6px; padding: 2px 6px; border-radius: 4px; background: #edf1f7; font-size: 12px; }}
    code {{ background: #eef2f7; padding: 2px 5px; border-radius: 4px; }}
  </style>
</head>
<body>
  <header>
    <h1>Codex Orchestration Language Trace</h1>
    <p>{escape(program.name)}</p>
  </header>
  <main>
    <section>
      <h2>Business Flow</h2>
      {business_flow}
    </section>
    <section>
      <h2>Artifact Board</h2>
      {artifact_board}
    </section>
    <section>
      <h2>Execution View</h2>
      <h3>Register File</h3>
      <table>
        <thead><tr><th>Register</th><th>Role</th><th>Agent</th><th>Output</th><th>Leases</th></tr></thead>
        <tbody>{register_rows}</tbody>
      </table>
      <h3>Pipeline Timeline</h3>
      <div class="timeline">{timeline}</div>
      <h3>Agent Call Graph</h3>
      <ul>{graph_edges}</ul>
      <h3>Memory Access</h3>
      <table>
        <thead><tr><th>Name</th><th>Space</th><th>Key</th><th>Read Cap</th><th>Write Cap</th></tr></thead>
        <tbody>{memory_rows}</tbody>
      </table>
      <h3>Batch Grid</h3>
      {batch_cards}
    </section>
  </main>
</body>
</html>"""


def _business_flow(program: IRProgram) -> str:
    if not program.workflow_nodes:
        return "<p>No workflow nodes in this program.</p>"
    nodes = "\n".join(_workflow_node_card(node) for node in program.workflow_nodes)
    edges = "\n".join(
        f"<div class='flow-edge'>{escape(edge.from_node)} "
        f"<code>{escape(edge.kind)}</code> {escape(edge.to_node)}"
        f"{_optional_label(edge.label)}</div>"
        for edge in program.workflow_edges
    )
    return f"<div class='flow'>{nodes}{edges}</div>"


def _workflow_node_card(node) -> str:
    details = []
    if node.role:
        details.append(f"role={node.role}")
    if node.artifact:
        details.append(f"artifact={node.artifact}")
    if node.condition:
        details.append(f"condition={node.condition}")
    if node.metadata.get("max_rounds") is not None:
        details.append(f"max_rounds={node.metadata['max_rounds']}")
    detail_html = "".join(
        f"<span class='pill'>{escape(detail)}</span>" for detail in details
    )
    return (
        f"<div class='flow-node {escape(node.kind)}'>"
        f"<div><strong>{escape(node.kind.upper())}</strong> "
        f"{escape(node.label)}{detail_html}</div></div>"
    )


def _artifact_board(program: IRProgram) -> str:
    artifact_rows = "\n".join(
        f"<tr><td>{escape(name)}</td><td>{escape(artifact.type)}</td>"
        f"<td>{escape(artifact.path)}</td><td>{escape(artifact.schema)}</td></tr>"
        for name, artifact in program.artifacts.items()
    ) or "<tr><td colspan='4'>No artifacts declared.</td></tr>"
    message_rows = "\n".join(
        f"<tr><td>{escape(name)}</td><td>{escape(message.from_role)}</td>"
        f"<td>{escape(message.to_role)}</td><td>{escape(message.artifact)}</td></tr>"
        for name, message in program.messages.items()
    ) or "<tr><td colspan='4'>No messages declared.</td></tr>"
    schema_rows = "\n".join(
        f"<tr><td>{escape(schema_name)}</td><td>{escape(field_name)}</td>"
        f"<td>{escape(field.type)}</td><td>{escape(','.join(field.values))}</td>"
        f"<td>{str(field.required).lower()}</td></tr>"
        for schema_name, schema in program.schemas.items()
        for field_name, field in schema.fields.items()
    ) or "<tr><td colspan='5'>No schemas declared.</td></tr>"
    selector_rows = "\n".join(
        f"<tr><td>{escape(name)}</td><td>{escape(str(selector.fields))}</td></tr>"
        for name, selector in program.thread_selectors.items()
    ) or "<tr><td colspan='2'>No thread selectors declared.</td></tr>"
    return (
        "<h3>Artifacts</h3><table>"
        "<thead><tr><th>Name</th><th>Type</th><th>Path</th><th>Schema</th></tr></thead>"
        f"<tbody>{artifact_rows}</tbody></table>"
        "<h3>Messages</h3><table>"
        "<thead><tr><th>Name</th><th>From</th><th>To</th><th>Artifact</th></tr></thead>"
        f"<tbody>{message_rows}</tbody></table>"
        "<h3>Schemas</h3><table>"
        "<thead><tr><th>Schema</th><th>Field</th><th>Type</th><th>Values</th><th>Required</th></tr></thead>"
        f"<tbody>{schema_rows}</tbody></table>"
        "<h3>Thread Selectors</h3><table>"
        "<thead><tr><th>Name</th><th>Fields</th></tr></thead>"
        f"<tbody>{selector_rows}</tbody></table>"
    )


def _optional_label(label: str | None) -> str:
    return f" <span class='pill'>{escape(label)}</span>" if label else ""


def _hazard_badges(event) -> str:
    return "".join(
        f"<span class='hazard'>{escape(hazard.code)}</span>" for hazard in event.hazards
    )


def _batch_card(instruction) -> str:
    workers = int(instruction.schedule_policy.get("max_workers", 1))
    cells = "".join(f"<div class='cell'>{idx + 1}</div>" for idx in range(workers))
    return (
        f"<div><strong>{escape(instruction.id)}</strong> "
        f"{escape(instruction.output_schema)}"
        f"<div class='batch'>{cells}</div></div>"
    )
