
    const nodes = new Map();
    const nodeModels = new Map();
    const graphNodes = new Map();
    const graphState = { scale: 1, x: 0, y: 0, dragging: false, lastX: 0, lastY: 0 };
    const detailState = { nodeId: null, scale: 1 };
    let source = null;
    let pollTimer = null;
    let activeRunId = null;
    let activeEventCount = 0;

    function byId(id) { return document.getElementById(id); }

    async function loadLatest() {
      if (source) source.close();
      nodes.clear();
      nodeModels.clear();
      graphNodes.clear();
      closeAgentDetail();
      byId("node-grid").innerHTML = "";
      byId("flow-graph").innerHTML = "";
      byId("timeline").textContent = "";
      byId("event-log").textContent = "";
      byId("summary").textContent = "loading latest";
      byId("status-text").textContent = "loading";
      byId("status-dot").className = "status-dot live";
      const response = await fetch("/latest-events", { cache: "no-store" });
      const payload = await response.json();
      for (const event of payload.events || []) applyEvent(event);
    }

    function startRun() {
      if (source) source.close();
      nodes.clear();
      nodeModels.clear();
      graphNodes.clear();
      closeAgentDetail();
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
      source.onmessage = event => applyEvent(JSON.parse(event.data));
      source.onerror = () => {
        byId("status-text").textContent = "disconnected";
        byId("status-dot").className = "status-dot";
      };
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
        markNode(event.node_id, event.status === "passed" ? "done" : "failed", event);
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
      card.classList.remove("running", "done", "failed");
      card.classList.add(state);
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
      row.classList.remove("running", "done", "failed");
      row.classList.add(state);
      row.querySelector(".graph-status").textContent = status || state;
    }

    function appendNodeOutput(event) {
      const card = nodes.get(event.node_id);
      if (!card) return;
      card.querySelector(".node-output").textContent += `${event.chunk}

`;
      card.querySelector(".node-output").scrollTop = card.querySelector(".node-output").scrollHeight;
      card.querySelector(".bar").style.width = `${Math.round(event.progress * 100)}%`;
      const model = nodeModels.get(event.node_id);
      if (model) {
        model.output += `${event.chunk}

`;
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
        .join("
") || "none";
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
      byId("timeline").textContent += `${event.type} ${label}
`;
    }

    function appendLog(line) {
      const log = byId("event-log");
      log.textContent += `${line}
`;
      log.scrollTop = log.scrollHeight;
    }

    async function pollActiveEvents() {
      if (source) return;
      const response = await fetch("/active-events", { cache: "no-store" });
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
        byId("node-grid").innerHTML = "";
        byId("flow-graph").innerHTML = "";
        byId("timeline").textContent = "";
        byId("event-log").textContent = "";
      }
      for (const event of events.slice(activeEventCount)) applyEvent(event);
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
  
