const data = window.SURVEY_DATA;

const state = {
  lang: "zh",
  selectedPaper: 0,
  selectedAgent: data.flow.nodes[0]?.id || "coordinator_scope",
  panel: "paper",
  referenceQuery: "",
  referenceDirection: "all",
  visibleEventIndex: data.events.length,
};

const nodePositions = {
  coordinator_scope: [24, 166],
  arxiv_retriever: [270, 76],
  openreview_retriever: [270, 256],
  dedup_scorer: [520, 166],
  taxonomy_director: [770, 42],
  summary_core: [770, 166],
  summary_extended: [770, 292],
  verifier: [1022, 166],
  final_writer: [1274, 166],
};

const directionZh = new Map(data.directions.map((item) => [item.name, item.nameZh]));

const sectionDefs = {
  zh: [
    ["abstract", "摘要"],
    ["intro", "1 引言"],
    ["definition", "2 个性化能力的定义"],
    ["conflict", "3 个性化与通用能力"],
    ["lifecycle", "4 训练与部署阶段"],
    ["taxonomy", "5 方法谱系与论文地图"],
    ["agents", "6 调研 Agent 过程"],
    ["risks", "7 风险、评测与开放问题"],
    ["references", "R 论文索引"],
  ],
  en: [
    ["abstract", "Abstract"],
    ["intro", "1 Introduction"],
    ["definition", "2 Personalization Capability"],
    ["conflict", "3 Personalization vs General Capability"],
    ["lifecycle", "4 Training and Deployment Stages"],
    ["taxonomy", "5 Method Taxonomy and Paper Map"],
    ["agents", "6 Research Agent Process"],
    ["risks", "7 Risks, Evaluation, and Open Problems"],
    ["references", "R Paper Index"],
  ],
};

const copy = {
  zh: {
    navSubtitle: "完整综述正文、论文详情和 Agent 编排进程在同一页面中联动。",
    title: "个性化大语言模型：能力定义、训练阶段、方法谱系与通用能力张力综述",
    lead:
      "本浏览器版 survey 基于 7,199 条 arXiv/OpenReview 扫描记录和 280 篇精筛论文，围绕 LaMP 与 OPPU 两条中心线，回答个性化能力是什么、它是否会损伤通用能力，以及现有模型在预训练、SFT、对齐、PEFT、RAG/Memory、在线学习和端侧部署阶段如何实现个性化。",
    meta: ["来源：arXiv + OpenReview", "窗口：2025-05-07 至 2026-05-07", "中心：LaMP / OPPU", "交互：hover / click / replay"],
    paperTab: "论文",
    agentTab: "Agent",
    search: "搜索标题、方法、数据集",
    allDirections: "全部方向",
  },
  en: {
    navSubtitle: "A full survey reader linking manuscript text, paper details, and agent orchestration.",
    title: "Personalized Large Language Models: Capabilities, Training Stages, Method Taxonomy, and Generality Tensions",
    lead:
      "This browser survey is built from 7,199 arXiv/OpenReview records and 280 curated papers. Centered on LaMP and OPPU, it explains what personalization capability means, whether it conflicts with general capability, and how current models introduce personalization across pretraining, SFT, alignment, PEFT, RAG/memory, online learning, and on-device deployment.",
    meta: ["Sources: arXiv + OpenReview", "Window: 2025-05-07 to 2026-05-07", "Anchors: LaMP / OPPU", "Interactions: hover / click / replay"],
    paperTab: "Paper",
    agentTab: "Agent",
    search: "Search title, method, dataset",
    allDirections: "All directions",
  },
};

function paperNumber(index) {
  return index + 1;
}

function findPaper(needle, fallback = 0) {
  const lower = needle.toLowerCase();
  const idx = data.papers.findIndex((paper) => paper.title.toLowerCase().includes(lower));
  return idx >= 0 ? idx : fallback;
}

const refs = {
  premium: findPaper("PREMIUM"),
  oppu: findPaper("Democratizing Large Language Models"),
  rpo: findPaper("Reflective Personalization Optimization"),
  pieces: findPaper("Personalized Pieces"),
  mta: findPaper("Merge-then-Adapt"),
  hyper: findPaper("Hypernetwork"),
  hydra: findPaper("HYDRA"),
  survey: findPaper("Survey of Personalized Large Language Models"),
  lamp: findPaper("LaMP: When Large Language Models Meet Personalization"),
  lampqa: findPaper("LaMP-QA"),
  clusterrag: findPaper("ClusterRAG"),
  safety: findPaper("privacy", 20),
};

function cite(index) {
  const paper = data.papers[index];
  if (!paper) return "";
  return `<a class="citation-ref" href="#ref-${index}" data-paper-index="${index}" title="${escapeHtml(paper.title)}">${paperNumber(index)}</a>`;
}

function renderShellText() {
  const c = copy[state.lang];
  document.documentElement.lang = state.lang === "zh" ? "zh-CN" : "en";
  document.querySelector("#nav-subtitle").textContent = c.navSubtitle;
  document.querySelector("#hero-title").textContent = c.title;
  document.querySelector("#hero-lead").textContent = c.lead;
  document.querySelector("#hero-meta").innerHTML = c.meta.map((item) => `<span class="meta-chip">${escapeHtml(item)}</span>`).join("");
  document.querySelector('[data-panel="paper"]').textContent = c.paperTab;
  document.querySelector('[data-panel="agent"]').textContent = c.agentTab;
}

function renderNav() {
  document.querySelector("#section-nav").innerHTML = sectionDefs[state.lang]
    .map(([id, label]) => `<li><a href="#${id}"><span class="meta-chip">${escapeHtml(label.split(" ")[0])}</span> ${escapeHtml(label.replace(/^[^ ]+ /, ""))}</a></li>`)
    .join("");
}

function renderManuscript() {
  const isZh = state.lang === "zh";
  document.querySelector("#manuscript").innerHTML = isZh ? manuscriptZh() : manuscriptEn();
  bindCitationRefs();
  bindReferenceControls();
  renderAgentFlow();
}

function manuscriptZh() {
  return `
    <section class="abstract-block" id="abstract">
      <h2>摘要</h2>
      <p class="lead-paragraph">个性化 LLM 研究正在从“给 prompt 拼上用户画像”的窄问题，扩展为贯穿模型生命周期的能力工程。本综述把个性化能力定义为：模型能够获取、表示、更新并调用用户或用户群体的偏好、目标、知识背景、风格、约束和历史交互，并让这些信息对生成、检索、排序、规划、工具调用或安全判断产生可测影响。</p>
      <p>LaMP ${cite(refs.lamp)} 把用户历史转化为 profile，并建立了可复现的个性化语言模型评测；OPPU ${cite(refs.oppu)} 则把个性化推进到每用户 PEFT/adapter 层面。近一年工作沿着这两条线扩散：一类继续追问如何评测、检索和压缩用户历史，另一类尝试把偏好写入参数、奖励、记忆、agent 状态或端侧私有模块。</p>
      <p>本页面的证据底座来自 7,199 条原始扫描记录、5,902 条去重候选和 280 篇精筛论文。正文采用论文浏览器结构：段落中的编号引用可 hover 或 click，右侧面板会展示该论文的发表时间、方法、数据集、结论和与 LaMP/OPPU 的关系；调研 Agent 的检索、去重、分类、摘要与验证过程也被保留为可重放的流程图。</p>
    </section>

    <section class="content-section" id="intro">
      <h2>1 引言</h2>
      <p>“个性化”在 LLM 语境下容易被误解为推荐系统的同义词，或者被简化成长期记忆功能。实际上，个性化更像一组横跨任务类型的能力调制机制：模型可以用用户历史选择证据，用用户偏好改变回答风格，用用户目标规划 agent 行动，用用户风险边界调整安全策略。推荐只是其中一个应用，记忆只是其中一种实现。</p>
      <p>因此，本综述不把论文机械地按 RAG、PEFT、alignment、agent 分成互不相干的清单，而是从一个共享问题出发：用户信息在模型生命周期的哪个位置进入系统、以什么形式保存、如何更新、何时调用、由谁审计？这个问题能同时解释 LaMP 的检索式 profile 路线、OPPU 的参数化个性化路线，以及后续 PREMIUM ${cite(refs.premium)}、HYDRA ${cite(refs.hydra)}、MTA ${cite(refs.mta)}、Instant Personalized Adaptation ${cite(refs.hyper)} 等工作。</p>
      <div class="callout"><strong>中心论点：</strong>个性化不应该被理解为削弱通用能力的替代模型，而应该被理解为受约束的调制层。通用模型提供事实、推理、语言和安全底座；个性化模块只在相关、可撤销、可校准、可审计的范围内改变检索、风格、解释粒度、偏好排序和行动策略。</div>
    </section>

    <section class="content-section" id="definition">
      <h2>2 个性化能力的定义</h2>
      <p>一个模型具有个性化能力，并不意味着它只是在回答中插入用户名，也不意味着它无条件顺从某个画像。更严格的判据是：用户相关信息对模型行为有可测影响，并且这种影响提升了当前用户的任务质量、偏好一致性、长期连贯性或风险控制。若用户画像与当前显式指令冲突，当前指令和安全边界应优先。</p>
      <div class="two-col">
        <div class="mini-card"><h3>区别于指令遵循</h3><p>指令遵循服从当前显式请求；个性化利用跨会话或跨任务的用户模型补全隐含需求。</p></div>
        <div class="mini-card"><h3>区别于上下文适应</h3><p>上下文适应依赖当前 prompt；个性化绑定用户身份、群体或长期历史，强调可更新和可遗忘。</p></div>
        <div class="mini-card"><h3>区别于推荐</h3><p>推荐主要解决 item/rank/choice；个性化 LLM 覆盖开放生成、问答、写作、工具调用、agent 规划和安全治理。</p></div>
        <div class="mini-card"><h3>区别于记忆</h3><p>记忆是存储和检索机制；个性化是能力目标。有记忆不等于会个性化，没有长期记忆也可通过 RAG、PEFT 或 reward 实现个性化。</p></div>
      </div>
      <p>从实现看，用户信息可以是显式偏好、隐式行为、长期记忆、相似用户群体、当前任务上下文或端侧私有数据；它可以作用在生成、检索、推荐、规划、工具调用、安全判断和评测指标上。LaMP-QA ${cite(refs.lampqa)}、ClusterRAG ${cite(refs.clusterrag)} 等工作说明，个性化能力的关键不只是“有用户历史”，还在于选择与当前任务真正相关的用户证据。</p>
    </section>

    <section class="content-section" id="conflict">
      <h2>3 个性化与通用能力是否冲突？</h2>
      <p>结论是不必然冲突，但冲突很容易在错误的调制方式中出现。若个性化直接改写共享 backbone 参数，模型可能出现参数漂移、负迁移、灾难性遗忘和跨用户污染。更稳健的做法通常是冻结通用底座，把用户差异放在 RAG、记忆、adapter、gating、residual steering 或 test-time rewriting 中。</p>
      <p>个性化也可能反而提升通用任务表现。当任务欠指定、用户历史能补足上下文、领域知识未被预训练充分覆盖，或长期助手需要保持一致性时，个性化提供的额外约束会减少歧义。OPPU ${cite(refs.oppu)}、Personalized Pieces ${cite(refs.pieces)} 和 PREMIUM ${cite(refs.premium)} 的共同思想都是把偏好放在局部、轻量、可控的位置，从而让通用能力保持为底座，而不是被完全覆盖。</p>
      <div class="table-block">
        <div class="table-scroll">
          <table>
            <thead><tr><th>冲突来源</th><th>表现</th><th>缓解方式</th></tr></thead>
            <tbody>
              <tr><td>过拟合用户历史</td><td>旧偏好、偶然风格或噪声行为被当作稳定需求</td><td>相关性检索、时间衰减、显式撤销、置信度校准</td></tr>
              <tr><td>共享参数污染</td><td>某些用户偏好影响所有用户</td><td>冻结 backbone，使用 adapter、LoRA、私有 residual 或端侧模块</td></tr>
              <tr><td>安全边界弱化</td><td>长期记忆让危险请求显得“合理”</td><td>安全策略优先级、intent re-check、多方上下文隔离</td></tr>
              <tr><td>隐私泄露</td><td>profile、记忆或梯度暴露敏感信息</td><td>本地检索、联邦学习、最小化日志、记忆权限控制</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="content-section" id="lifecycle">
      <h2>4 训练与部署阶段</h2>
      <p>个性化不是单一算法，而是在模型生命周期中多次进入系统的用户信息流。预训练阶段提供人群和领域先验；SFT 阶段让模型学会读取用户画像；alignment 阶段处理“不同用户认为好回答不同”；PEFT 阶段把稳定偏好写入局部参数；RAG/Memory 在推理期调用用户历史；在线学习处理偏好漂移；联邦和端侧部署则解决个人数据不能集中上传的问题。</p>
      ${renderStageTable("zh")}
    </section>

    <section class="content-section" id="taxonomy">
      <h2>5 方法谱系与论文地图</h2>
      <p>如果按研究问题聚类，近一年工作主要落在八类：个性化对齐与偏好学习、PEFT 与适配、agent 与助手、推荐与排序、画像提示与 RAG、隐私联邦端侧、基准评测、记忆与动态用户建模。它们不是并列菜单，而是围绕“用户信息如何进入模型”这一主问题的不同答案。</p>
      ${renderDirectionBars()}
      <div class="table-block">
        <div class="table-scroll">
          <table>
            <thead><tr><th>方向</th><th>核心问题</th><th>代表论文</th></tr></thead>
            <tbody>
              <tr><td>基准与评测</td><td>如何定义可复现的个性化收益</td><td>LaMP ${cite(refs.lamp)}、LaMP-QA ${cite(refs.lampqa)}</td></tr>
              <tr><td>PEFT 与适配</td><td>如何把用户偏好存入少量参数</td><td>OPPU ${cite(refs.oppu)}、Personalized Pieces ${cite(refs.pieces)}、Instant Hypernetwork ${cite(refs.hyper)}</td></tr>
              <tr><td>黑盒与后处理</td><td>不能改模型参数时如何个性化</td><td>RPO ${cite(refs.rpo)}、HYDRA ${cite(refs.hydra)}</td></tr>
              <tr><td>RAG/记忆</td><td>如何检索、压缩、更新用户历史</td><td>ClusterRAG ${cite(refs.clusterrag)}</td></tr>
              <tr><td>对齐与安全</td><td>如何处理个人偏好和公共安全边界</td><td>PREMIUM ${cite(refs.premium)}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="content-section" id="agents">
      <h2>6 调研 Agent 过程</h2>
      <p>本 survey 的语料不是手工拼凑的。Controller 先写范围 artifact，然后由 arXiv/OpenReview 检索 agent 拉取记录，DedupScoringDirector 去重打分，TaxonomyDirector 建立方向谱系，SummaryDirector 分批写中文条目，VerificationDirector 检查数量和字段，FinalWriter 生成最终长文。下面的流程图保留了这些步骤的实时事件。</p>
      ${renderAgentSectionShell("zh")}
    </section>

    <section class="content-section" id="risks">
      <h2>7 风险、评测与开放问题</h2>
      <p>个性化能力的难点不在于“让模型更像懂我”，而在于让这种懂法可控。一个好的个性化系统需要同时报告事实置信度、偏好匹配度和安全风险分数；否则，风格贴近可能掩盖事实错误，用户满意度可能奖励迎合，长期记忆可能把不该保留的信息永久化。</p>
      <div class="three-col">
        <div class="mini-card"><h3>评测错位</h3><p>平均 benchmark 可能掩盖个体差异，个性化 benchmark 又可能奖励迎合而非正确。</p></div>
        <div class="mini-card"><h3>记忆治理</h3><p>长期记忆需要写入权限、遗忘机制、冲突解决和多用户场景隔离。</p></div>
        <div class="mini-card"><h3>隐私与部署</h3><p>端侧和联邦方案降低集中暴露，但仍面临梯度泄露、同步成本和设备能力限制。</p></div>
      </div>
      <p>未来更值得关注的不是单点方法谁分数更高，而是组合式系统：通用 backbone + 可撤销 memory + 可审计 retrieval + 局部 adapter + 个体 reward + 安全优先级。这样的架构才能在保留通用能力的同时，让个性化成为可靠的能力调制层。</p>
    </section>

    ${renderReferencesSection("zh")}
  `;
}

function manuscriptEn() {
  return `
    <section class="abstract-block" id="abstract">
      <h2>Abstract</h2>
      <p class="lead-paragraph">Personalized LLM research is moving from profile-augmented prompts to lifecycle-wide capability engineering. We define personalization capability as the ability to acquire, represent, update, and use user preferences, goals, background knowledge, style, constraints, and interaction history in a way that measurably affects generation, retrieval, ranking, planning, tool use, or safety decisions.</p>
      <p>LaMP ${cite(refs.lamp)} established a reproducible benchmark around user history as profiles, while OPPU ${cite(refs.oppu)} pushed personalization into per-user PEFT modules. Recent work extends both lines through profile retrieval, lightweight adaptation, black-box rewriting, user-level rewards, long-term memory, personalized agents, and privacy-preserving deployment.</p>
      <p>The corpus behind this browser contains 7,199 raw records, 5,902 deduplicated candidates, and 280 curated papers. Inline citations are interactive: hovering or clicking a number opens method, dataset, findings, venue, and URL details in the right panel. The research agent workflow is preserved as a replayable process graph.</p>
    </section>

    <section class="content-section" id="intro">
      <h2>1 Introduction</h2>
      <p>Personalization is often conflated with recommendation or long-term memory. In LLM systems it is broader: user information can shape evidence retrieval, response style, explanation granularity, agent planning, tool use, ranking, and safety policy. Recommendation is one application; memory is one mechanism.</p>
      <p>This survey asks one organizing question: where does user information enter the model lifecycle, in what form is it stored, how is it updated, when is it invoked, and how can it be audited? This question connects LaMP-style profile retrieval, OPPU-style parameterized personalization, and recent systems such as PREMIUM ${cite(refs.premium)}, HYDRA ${cite(refs.hydra)}, MTA ${cite(refs.mta)}, and instant hypernetwork adaptation ${cite(refs.hyper)}.</p>
      <div class="callout"><strong>Central claim:</strong> personalization should be treated as a constrained modulation layer. The general model supplies the factual, reasoning, linguistic, and safety foundation; personalization changes retrieval, style, explanation granularity, preference ranking, and action strategy only when relevant, reversible, calibrated, and auditable.</div>
    </section>

    <section class="content-section" id="definition">
      <h2>2 Personalization Capability</h2>
      <p>A model is not personalized simply because it uses a name or follows a profile literally. The stronger test is whether user-related information measurably changes model behavior and improves task quality, preference consistency, long-term coherence, or risk control for the current user. Explicit user instructions and safety boundaries should remain higher priority than inferred profiles.</p>
      <div class="two-col">
        <div class="mini-card"><h3>Not just instruction following</h3><p>Instruction following obeys the current explicit request; personalization uses cross-session or cross-task user models to fill implicit needs.</p></div>
        <div class="mini-card"><h3>Not just context adaptation</h3><p>Context adaptation reacts to the current prompt; personalization binds to a user identity, group, or long-term history and must handle update and forgetting.</p></div>
        <div class="mini-card"><h3>Beyond recommendation</h3><p>Recommendation solves item choice and ranking; personalized LLMs also cover open generation, writing, QA, tool use, agents, and safety governance.</p></div>
        <div class="mini-card"><h3>Memory is a mechanism</h3><p>Memory stores and retrieves information; personalization is the capability goal. Memory alone does not guarantee good personalization.</p></div>
      </div>
    </section>

    <section class="content-section" id="conflict">
      <h2>3 Personalization vs General Capability</h2>
      <p>Personalization does not inherently conflict with general capability, but bad modulation can create conflict. Directly changing shared backbone parameters may cause drift, negative transfer, forgetting, or cross-user contamination. More robust systems freeze the general foundation and put user differences into RAG, memory, adapters, gating, residual steering, or test-time rewriting.</p>
      <p>Personalization can improve general task performance when the task is under-specified, user history resolves ambiguity, domain knowledge is not sufficiently covered by pretraining, or a long-term assistant needs consistency. OPPU ${cite(refs.oppu)}, Personalized Pieces ${cite(refs.pieces)}, and PREMIUM ${cite(refs.premium)} all keep preference adaptation local and lightweight.</p>
      <div class="table-block">
        <div class="table-scroll">
          <table>
            <thead><tr><th>Failure source</th><th>Symptom</th><th>Mitigation</th></tr></thead>
            <tbody>
              <tr><td>User-history overfitting</td><td>Stale or noisy behavior becomes a fixed preference</td><td>Relevance retrieval, time decay, explicit deletion, calibration</td></tr>
              <tr><td>Shared-parameter contamination</td><td>One user's preference leaks into behavior for others</td><td>Frozen backbone, adapters, LoRA, local residual modules</td></tr>
              <tr><td>Safety erosion</td><td>Memory legitimizes risky intent</td><td>Safety priority, intent re-checks, context isolation</td></tr>
              <tr><td>Privacy leakage</td><td>Profiles, memories, or gradients expose sensitive data</td><td>Local retrieval, federated learning, minimal logging</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="content-section" id="lifecycle">
      <h2>4 Training and Deployment Stages</h2>
      <p>Personalization is not a single algorithm. User information enters the system at multiple stages: pretraining supplies population priors; SFT teaches profile-conditioned instruction following; alignment models user-level preferences; PEFT stores stable preferences in local parameters; RAG and memory retrieve history at inference time; online learning handles drift; federated and on-device deployment protect private data.</p>
      ${renderStageTable("en")}
    </section>

    <section class="content-section" id="taxonomy">
      <h2>5 Method Taxonomy and Paper Map</h2>
      <p>The curated corpus clusters into alignment and preference learning, PEFT and adaptation, personalized agents, recommendation and ranking, profile prompting and RAG, privacy/federated/on-device methods, benchmarks, and dynamic memory. These are not isolated menus; they are different answers to the same question of where user information enters the LLM system.</p>
      ${renderDirectionBars()}
      <div class="table-block">
        <div class="table-scroll">
          <table>
            <thead><tr><th>Direction</th><th>Question</th><th>Representative papers</th></tr></thead>
            <tbody>
              <tr><td>Benchmarks</td><td>How do we measure personalized gains reproducibly?</td><td>LaMP ${cite(refs.lamp)}, LaMP-QA ${cite(refs.lampqa)}</td></tr>
              <tr><td>PEFT</td><td>How do we store user preferences in few parameters?</td><td>OPPU ${cite(refs.oppu)}, Personalized Pieces ${cite(refs.pieces)}, Hypernetwork adaptation ${cite(refs.hyper)}</td></tr>
              <tr><td>Black-box methods</td><td>How can we personalize when model parameters are inaccessible?</td><td>RPO ${cite(refs.rpo)}, HYDRA ${cite(refs.hydra)}</td></tr>
              <tr><td>RAG and memory</td><td>How do we retrieve and update user history?</td><td>ClusterRAG ${cite(refs.clusterrag)}</td></tr>
              <tr><td>Alignment and safety</td><td>How do personal preferences meet global safety boundaries?</td><td>PREMIUM ${cite(refs.premium)}</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="content-section" id="agents">
      <h2>6 Research Agent Process</h2>
      <p>The survey was built through an artifact-routed workflow: retrieval agents gathered arXiv and OpenReview records, a scoring agent deduplicated and ranked candidates, taxonomy and summary agents wrote structured notes, a verifier checked counts and fields, and the final writer composed the survey.</p>
      ${renderAgentSectionShell("en")}
    </section>

    <section class="content-section" id="risks">
      <h2>7 Risks, Evaluation, and Open Problems</h2>
      <p>The challenge is not merely making a model feel like it knows the user; it is making that knowledge controllable. A strong personalized system should separate factual confidence, preference match, and safety risk. Otherwise, style matching can hide factual errors, user satisfaction can reward sycophancy, and long-term memory can preserve information that should be forgotten.</p>
      <div class="three-col">
        <div class="mini-card"><h3>Evaluation mismatch</h3><p>Aggregate benchmarks hide individual differences, while personalized benchmarks may reward pleasing rather than correct answers.</p></div>
        <div class="mini-card"><h3>Memory governance</h3><p>Long-term memory needs write permissions, forgetting, conflict resolution, and multi-user isolation.</p></div>
        <div class="mini-card"><h3>Privacy and deployment</h3><p>Federated and on-device methods reduce centralized exposure but add leakage and device constraints.</p></div>
      </div>
    </section>

    ${renderReferencesSection("en")}
  `;
}

function renderStageTable(lang) {
  const labels = lang === "zh"
    ? ["阶段", "个性化载体", "典型方法", "为什么有效", "风险"]
    : ["Stage", "Carrier", "Typical methods", "Why it works", "Risk"];
  return `
    <div class="table-block">
      <div class="table-scroll">
        <table>
          <thead><tr>${labels.map((label) => `<th>${label}</th>`).join("")}</tr></thead>
          <tbody>
            ${data.stages.map((stage) => {
              const item = stage[lang];
              return `<tr><td><strong>${escapeHtml(item.name)}</strong></td><td>${escapeHtml(item.carrier)}</td><td>${escapeHtml(item.methods)}</td><td>${escapeHtml(item.strength)}</td><td>${escapeHtml(item.risk)}</td></tr>`;
            }).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function renderDirectionBars() {
  const max = Math.max(...data.directions.map((item) => item.count));
  return `
    <div class="figure-block">
      ${data.directions.map((item) => {
        const label = state.lang === "zh" ? item.nameZh : item.name;
        return `<div class="bar-row"><strong>${escapeHtml(label)}</strong><div class="bar-track"><span style="width:${(item.count / max) * 100}%"></span></div><span>${item.count}</span></div>`;
      }).join("")}
    </div>
  `;
}

function renderAgentSectionShell(lang) {
  const replay = lang === "zh" ? "重放流程" : "Replay";
  const live = lang === "zh" ? "打开 COL 实时页" : "Open COL live";
  return `
    <div class="agent-block">
      <div class="agent-toolbar">
        <button class="small-button primary" id="replay-flow" type="button">${replay}</button>
        <a class="small-button" href="http://127.0.0.1:8765/" target="_blank">${live}</a>
      </div>
      <div class="agent-flow">
        <div class="agent-canvas">
          <svg class="flow-lines" id="flow-lines" aria-hidden="true"></svg>
          <div id="agent-nodes"></div>
        </div>
      </div>
    </div>
  `;
}

function renderReferencesSection(lang) {
  const title = lang === "zh" ? "R 论文索引" : "R Paper Index";
  const intro = lang === "zh"
    ? "下面列出全部 280 篇精筛论文。点击任意卡片可在右侧查看详细信息；搜索会匹配标题、方向、阶段、方法和数据集。"
    : "All 280 curated papers are listed below. Click a card to inspect details in the right panel; search matches title, direction, stage, method, and datasets.";
  return `
    <section class="references-section" id="references">
      <h2>${title}</h2>
      <p>${intro}</p>
      <div class="reference-toolbar">
        <input id="reference-search" type="search" placeholder="${escapeHtml(copy[lang].search)}" />
        <select id="reference-direction" aria-label="Direction filter">
          <option value="all">${escapeHtml(copy[lang].allDirections)}</option>
          ${data.directions.map((item) => `<option value="${escapeHtml(item.name)}">${escapeHtml(lang === "zh" ? item.nameZh : item.name)}</option>`).join("")}
        </select>
      </div>
      <div class="references-grid" id="references-grid"></div>
    </section>
  `;
}

function renderReferences() {
  const grid = document.querySelector("#references-grid");
  if (!grid) return;
  const query = state.referenceQuery.trim().toLowerCase();
  const direction = state.referenceDirection;
  const filtered = data.papers.filter((paper) => {
    if (direction !== "all" && paper.direction !== direction) return false;
    if (!query) return true;
    return `${paper.title} ${paper.direction} ${paper.stage} ${paper.datasets} ${paper.methodZh} ${paper.methodEn}`.toLowerCase().includes(query);
  });
  grid.innerHTML = filtered.map((paper) => {
    const index = data.papers.indexOf(paper);
    return `
      <article class="reference-card" id="ref-${index}" data-paper-index="${index}">
        <div class="reference-number">[${paperNumber(index)}]</div>
        <div>
          <h3>${escapeHtml(paper.title)}</h3>
          <p class="reference-meta">${escapeHtml(paper.date)} · ${escapeHtml(paper.venue || paper.tier)}</p>
          <p class="reference-topic">${escapeHtml(labelDirection(paper.direction))} · ${escapeHtml(paper.stage)} · ${escapeHtml(paper.datasets)}</p>
        </div>
      </article>
    `;
  }).join("");
  grid.querySelectorAll(".reference-card").forEach((card) => {
    card.addEventListener("click", () => selectPaper(Number(card.dataset.paperIndex)));
  });
}

function bindReferenceControls() {
  const search = document.querySelector("#reference-search");
  const direction = document.querySelector("#reference-direction");
  if (search) {
    search.value = state.referenceQuery;
    search.addEventListener("input", () => {
      state.referenceQuery = search.value;
      renderReferences();
    });
  }
  if (direction) {
    direction.value = state.referenceDirection;
    direction.addEventListener("change", () => {
      state.referenceDirection = direction.value;
      renderReferences();
    });
  }
  renderReferences();
}

function selectPaper(index) {
  state.selectedPaper = index;
  switchPanel("paper");
  renderPaperPanel(index);
}

function renderPaperPanel(index = state.selectedPaper) {
  const paper = data.papers[index];
  if (!paper) return;
  const method = state.lang === "zh" ? paper.methodZh : paper.methodEn;
  const findings = paper.findingsZh || (state.lang === "zh" ? "摘要未明确给出更多结论，需结合正文核查。" : "No additional finding was extracted from the abstract.");
  document.querySelector("#paper-panel").innerHTML = `
    <article class="paper-detail-card">
      <h3>[${paperNumber(index)}] ${escapeHtml(paper.title)}</h3>
      <div class="detail-kv">
        <div><strong>URL</strong><a href="${paper.url}" target="_blank">${escapeHtml(paper.url)}</a></div>
        <div><strong>Date / Venue</strong>${escapeHtml(paper.date)} · ${escapeHtml(paper.venue || paper.tier)}</div>
        <div><strong>Direction</strong>${escapeHtml(labelDirection(paper.direction))}</div>
        <div><strong>Stage</strong>${escapeHtml(paper.stage)}</div>
        <div><strong>Method</strong>${escapeHtml(method)}</div>
        <div><strong>Datasets</strong>${escapeHtml(paper.datasets)}</div>
        <div><strong>Findings</strong>${escapeHtml(findings)}</div>
      </div>
    </article>
  `;
}

function renderTooltip(index) {
  const paper = data.papers[index];
  if (!paper) return "";
  const method = state.lang === "zh" ? paper.methodZh : paper.methodEn;
  return `<h3>[${paperNumber(index)}] ${escapeHtml(paper.title)}</h3><p>${escapeHtml(paper.date)} · ${escapeHtml(labelDirection(paper.direction))}</p><p>${escapeHtml(method)}</p>`;
}

let tooltipHideTimer = null;

function bindCitationRefs() {
  const tooltip = document.querySelector("#citation-tooltip");
  document.querySelectorAll(".citation-ref").forEach((node) => {
    const index = Number(node.dataset.paperIndex);
    node.addEventListener("mouseenter", (event) => {
      clearTimeout(tooltipHideTimer);
      tooltip.innerHTML = renderTooltip(index);
      tooltip.hidden = false;
      tooltip.classList.add("visible");
      positionTooltip(event);
      renderPaperPanel(index);
    });
    node.addEventListener("mousemove", positionTooltip);
    node.addEventListener("mouseleave", () => {
      tooltipHideTimer = setTimeout(() => {
        tooltip.classList.remove("visible");
        tooltip.hidden = true;
      }, 180);
    });
    node.addEventListener("click", (event) => {
      event.preventDefault();
      selectPaper(index);
    });
  });
  tooltip.addEventListener("mouseenter", () => clearTimeout(tooltipHideTimer));
  tooltip.addEventListener("mouseleave", () => {
    tooltip.classList.remove("visible");
    tooltip.hidden = true;
  });
}

function positionTooltip(event) {
  const tooltip = document.querySelector("#citation-tooltip");
  const padding = 18;
  const rect = tooltip.getBoundingClientRect();
  let left = event.clientX + 16;
  let top = event.clientY + 16;
  if (left + rect.width + padding > window.innerWidth) left = event.clientX - rect.width - 16;
  if (top + rect.height + padding > window.innerHeight) top = event.clientY - rect.height - 16;
  tooltip.style.left = `${Math.max(padding, left)}px`;
  tooltip.style.top = `${Math.max(padding, top)}px`;
}

function visibleEvents() {
  return data.events.slice(0, state.visibleEventIndex);
}

function lastEvent(nodeId, type) {
  const events = visibleEvents().filter((event) => event.node_id === nodeId && event.type === type);
  return events.length ? events[events.length - 1] : null;
}

function nodeStatus(nodeId) {
  const completed = lastEvent(nodeId, "node_completed");
  if (completed) return completed.status || "passed";
  return visibleEvents().some((event) => event.node_id === nodeId && event.type === "node_started") ? "running" : "waiting";
}

function renderAgentFlow() {
  const wrap = document.querySelector("#agent-nodes");
  const svg = document.querySelector("#flow-lines");
  if (!wrap || !svg) return;
  wrap.innerHTML = data.flow.nodes.map((node) => {
    const [x, y] = nodePositions[node.id] || [20, 20];
    const status = nodeStatus(node.id);
    const active = node.id === state.selectedAgent ? "active" : "";
    return `<button class="agent-node ${status} ${active}" data-node-id="${node.id}" style="left:${x}px; top:${y}px" type="button"><h3>${escapeHtml(node.label)}</h3><p>${escapeHtml(node.role)} · ${escapeHtml(status)}</p></button>`;
  }).join("");
  wrap.querySelectorAll(".agent-node").forEach((node) => {
    node.addEventListener("click", () => {
      state.selectedAgent = node.dataset.nodeId;
      switchPanel("agent");
      renderAgentFlow();
      renderAgentPanel();
    });
  });
  svg.setAttribute("viewBox", "0 0 1480 420");
  svg.innerHTML = '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#9ba8a1"></path></marker></defs>' +
    data.flow.edges.map((edge) => {
      const from = nodePositions[edge.from];
      const to = nodePositions[edge.to];
      if (!from || !to) return "";
      const x1 = from[0] + 190;
      const y1 = from[1] + 43;
      const x2 = to[0];
      const y2 = to[1] + 43;
      const mid = (x1 + x2) / 2;
      return `<path d="M ${x1} ${y1} C ${mid} ${y1}, ${mid} ${y2}, ${x2} ${y2}" fill="none" stroke="#9ba8a1" stroke-width="2" marker-end="url(#arrow)" />`;
    }).join("");
  const replay = document.querySelector("#replay-flow");
  if (replay && !replay.dataset.bound) {
    replay.dataset.bound = "true";
    replay.addEventListener("click", replayAgents);
  }
}

function replayAgents() {
  state.visibleEventIndex = 1;
  renderAgentFlow();
  renderAgentPanel();
  const timer = setInterval(() => {
    state.visibleEventIndex += 2;
    if (state.visibleEventIndex >= data.events.length) {
      state.visibleEventIndex = data.events.length;
      clearInterval(timer);
    }
    renderAgentFlow();
    renderAgentPanel();
  }, 150);
}

function renderAgentPanel() {
  const node = data.flow.nodes.find((item) => item.id === state.selectedAgent) || data.flow.nodes[0];
  if (!node) return;
  const events = visibleEvents().filter((event) => event.node_id === node.id);
  const lines = events.map((event) => {
    const chunk = event.chunk || event.message || event.path || event.status || event.type;
    return `<div class="event-line">${escapeHtml(event.type)}: ${escapeHtml(chunk)}</div>`;
  }).join("") || '<div class="event-line">waiting</div>';
  document.querySelector("#agent-panel").innerHTML = `
    <article class="agent-detail-card">
      <h3>${escapeHtml(node.label)}</h3>
      <div class="detail-kv">
        <div><strong>Role</strong>${escapeHtml(node.role)}</div>
        <div><strong>Status</strong>${escapeHtml(nodeStatus(node.id))}</div>
        <div><strong>Events</strong>${events.length}</div>
      </div>
      <div class="agent-events">${lines}</div>
    </article>
  `;
}

function switchPanel(panel) {
  state.panel = panel;
  document.querySelectorAll(".panel-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.panel === panel));
  document.querySelectorAll(".panel-body").forEach((body) => body.classList.toggle("active", body.id === `${panel}-panel`));
}

function bindGlobalEvents() {
  document.querySelectorAll("[data-lang]").forEach((button) => {
    button.addEventListener("click", () => {
      state.lang = button.dataset.lang;
      document.querySelectorAll("[data-lang]").forEach((item) => item.classList.toggle("active", item === button));
      render();
    });
  });
  document.querySelectorAll(".panel-tab").forEach((button) => {
    button.addEventListener("click", () => switchPanel(button.dataset.panel));
  });
}

function labelDirection(direction) {
  return state.lang === "zh" ? directionZh.get(direction) || direction : direction;
}

function render() {
  renderShellText();
  renderNav();
  renderManuscript();
  renderPaperPanel();
  renderAgentPanel();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

bindGlobalEvents();
render();
