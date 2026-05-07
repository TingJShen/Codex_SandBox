from __future__ import annotations

import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
PROCESSED = ROOT / "cache" / "processed"
REPORTS = ROOT / "cache" / "reports"


NAME_ZH = {
    "Benchmark and Evaluation": "基准与评测",
    "Personalized Alignment and Preference Learning": "个性化对齐与偏好学习",
    "Personalized PEFT and Adaptation": "个性化 PEFT 与适配",
    "LLM-based Recommendation and Ranking": "LLM 推荐与排序",
    "Personalized Agents and Assistants": "个性化 Agent 与助手",
    "Privacy, Federated, and On-device Personalization": "隐私、联邦与端侧个性化",
    "Profile Prompting and Personalized RAG": "画像提示与个性化 RAG",
    "Memory and Dynamic User Modeling": "记忆与动态用户建模",
    "Domain Applications": "领域应用",
}


STAGE_BY_DIRECTION = {
    "Benchmark and Evaluation": "Evaluation",
    "Personalized Alignment and Preference Learning": "Alignment",
    "Personalized PEFT and Adaptation": "PEFT",
    "LLM-based Recommendation and Ranking": "SFT / Recommendation",
    "Personalized Agents and Assistants": "Inference / Agent Memory",
    "Privacy, Federated, and On-device Personalization": "Federated / On-device",
    "Profile Prompting and Personalized RAG": "RAG / Memory",
    "Memory and Dynamic User Modeling": "Continual / Online",
    "Domain Applications": "Application",
}


def display_direction(row: dict, fallback: str) -> str:
    text = f"{row.get('title', '')} {row.get('abstract', '')}".lower()
    if any(term in text for term in ["peft", "parameter-efficient", "fine-tuning", "finetuning", "lora", "adapter", "hypernetwork"]):
        return "Personalized PEFT and Adaptation"
    if any(term in text for term in ["alignment", "reward", "rlhf", "dpo", "preference feedback", "preference learning", "preference optimization"]):
        return "Personalized Alignment and Preference Learning"
    if any(term in text for term in ["recommendation", "recommender", "ranking", "collaborative filtering"]):
        return "LLM-based Recommendation and Ranking"
    if any(term in text for term in ["federated", "on-device", "privacy", "private", "local model"]):
        return "Privacy, Federated, and On-device Personalization"
    if any(term in text for term in ["agent", "assistant", "tool use"]):
        return "Personalized Agents and Assistants"
    if any(term in text for term in ["rag", "retrieval", "profile prompting", "retrieve"]):
        return "Profile Prompting and Personalized RAG"
    if any(term in text for term in ["memory", "long-term", "dynamic user"]):
        return "Memory and Dynamic User Modeling"
    if any(term in text for term in ["benchmark", "evaluation", "dataset", "lamp"]):
        return "Benchmark and Evaluation"
    return fallback


METHOD_ZH_BY_DIRECTION = {
    "Benchmark and Evaluation": "该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。",
    "Personalized Alignment and Preference Learning": "该工作把用户级偏好纳入对齐或奖励建模，关注不同用户对“好回答”的不同标准。",
    "Personalized PEFT and Adaptation": "该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。",
    "LLM-based Recommendation and Ranking": "该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。",
    "Personalized Agents and Assistants": "该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。",
    "Privacy, Federated, and On-device Personalization": "该工作强调隐私保护或本地化个性化，尝试在不集中上传个人数据的情况下获得用户级收益。",
    "Profile Prompting and Personalized RAG": "该工作围绕用户画像、历史检索或个性化上下文注入展开，在生成前选择与当前用户最相关的证据。",
    "Memory and Dynamic User Modeling": "该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。",
    "Domain Applications": "该工作把个性化 LLM 方法落到具体应用场景，重点是用户差异和实际任务收益。",
}


STAGES = [
    {
        "id": "pretraining",
        "zh": {
            "name": "预训练",
            "carrier": "人群与领域先验",
            "summary": "预训练不是真正的个人级个性化，但它决定模型是否见过足够多的人群、文化、领域和行为差异。",
            "methods": "数据覆盖、去重、隐私过滤、领域混合",
            "strength": "提供通用语言、事实和群体差异底座",
            "risk": "群体偏差、隐私记忆化、长尾用户缺失",
        },
        "en": {
            "name": "Pretraining",
            "carrier": "Population and domain priors",
            "summary": "Pretraining is not user-level personalization, but it determines whether the model has broad priors over cultures, domains, and behavioral variation.",
            "methods": "Data coverage, deduplication, privacy filtering, domain mixture",
            "strength": "Supplies the general linguistic and factual foundation",
            "risk": "Population bias, memorization, and missing long-tail users",
        },
    },
    {
        "id": "sft",
        "zh": {
            "name": "监督指令微调",
            "carrier": "画像条件下的示范",
            "summary": "SFT 让模型学会读懂用户画像、历史和约束，把它们转化为任务执行方式。",
            "methods": "Profile-conditioned instruction data, persona tasks, assistant traces",
            "strength": "让显式画像进入指令遵循能力",
            "risk": "把画像当成硬规则，覆盖当前指令",
        },
        "en": {
            "name": "SFT",
            "carrier": "Profile-conditioned demonstrations",
            "summary": "SFT teaches the model how to read user profiles, histories, and constraints as part of task execution.",
            "methods": "Profile-conditioned instruction data, persona tasks, assistant traces",
            "strength": "Connects explicit profiles to instruction following",
            "risk": "Profiles may override current intent",
        },
    },
    {
        "id": "alignment",
        "zh": {
            "name": "偏好优化/对齐",
            "carrier": "用户级偏好奖励",
            "summary": "对齐阶段处理不同用户对“好回答”的不同标准，是个性化和安全边界最容易相互拉扯的位置。",
            "methods": "Personalized reward models, DPO, RLHF, preference feedback",
            "strength": "直接优化个体满意度和偏好一致性",
            "risk": "迎合、校准下降、安全降级",
        },
        "en": {
            "name": "Alignment",
            "carrier": "User-level preference rewards",
            "summary": "Alignment handles different standards of a good answer and is where personalization and safety boundaries interact most strongly.",
            "methods": "Personalized reward models, DPO, RLHF, preference feedback",
            "strength": "Optimizes user satisfaction and preference consistency",
            "risk": "Sycophancy, miscalibration, and safety erosion",
        },
    },
    {
        "id": "peft",
        "zh": {
            "name": "PEFT/微调",
            "carrier": "用户或用户簇参数",
            "summary": "PEFT 把稳定偏好写入 LoRA、adapter 或 hypernetwork 生成的局部参数。",
            "methods": "LoRA, adapters, hypernetworks, user clusters",
            "strength": "偏好稳定、可复用、比提示更深",
            "risk": "冷启动、存储成本、跨用户污染",
        },
        "en": {
            "name": "PEFT / Fine-tuning",
            "carrier": "User or cluster parameters",
            "summary": "PEFT stores stable preferences in local parameters such as LoRA, adapters, or hypernetwork-generated modules.",
            "methods": "LoRA, adapters, hypernetworks, user clusters",
            "strength": "Stable and reusable preference storage",
            "risk": "Cold start, storage cost, cross-user contamination",
        },
    },
    {
        "id": "rag_memory",
        "zh": {
            "name": "RAG/记忆推理",
            "carrier": "历史、画像和长期记忆",
            "summary": "推理期个性化不改参数，而是在生成前检索用户历史、画像、长期记忆或相似用户证据。",
            "methods": "Profile prompting, retrieval, memory stores, reranking",
            "strength": "灵活、可撤销、易审计",
            "risk": "无关记忆污染、上下文预算、隐私暴露",
        },
        "en": {
            "name": "RAG / Memory",
            "carrier": "History, profiles, and long-term memory",
            "summary": "Inference-time personalization retrieves user history, profiles, memories, or similar-user evidence before generation.",
            "methods": "Profile prompting, retrieval, memory stores, reranking",
            "strength": "Flexible, reversible, and auditable",
            "risk": "Irrelevant memory, context budget pressure, privacy leakage",
        },
    },
    {
        "id": "continual",
        "zh": {
            "name": "持续/在线学习",
            "carrier": "随交互更新的用户状态",
            "summary": "长期助手需要处理偏好漂移、遗忘、冲突解决和安全反馈回路。",
            "methods": "Online feedback, test-time adaptation, memory consolidation",
            "strength": "适合长期一致性和动态需求",
            "risk": "旧偏好压制新意图、反馈投毒",
        },
        "en": {
            "name": "Continual / Online",
            "carrier": "Interaction-updated user state",
            "summary": "Long-term assistants must handle preference drift, forgetting, conflict resolution, and safety feedback loops.",
            "methods": "Online feedback, test-time adaptation, memory consolidation",
            "strength": "Supports long-term consistency and dynamic needs",
            "risk": "Stale preferences and feedback poisoning",
        },
    },
    {
        "id": "federated",
        "zh": {
            "name": "联邦/端侧部署",
            "carrier": "本地数据与私有适配器",
            "summary": "隐私约束下，个性化通常被移到端侧小模型、本地 adapter 或联邦偏好优化中。",
            "methods": "Federated learning, on-device adapters, local steering",
            "strength": "降低个人数据集中暴露",
            "risk": "梯度泄露、同步成本、端侧算力限制",
        },
        "en": {
            "name": "Federated / On-device",
            "carrier": "Local data and private adapters",
            "summary": "Under privacy constraints, personalization moves to local models, private adapters, or federated preference optimization.",
            "methods": "Federated learning, on-device adapters, local steering",
            "strength": "Reduces centralized exposure of personal data",
            "risk": "Gradient leakage, synchronization cost, device limits",
        },
    },
]


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def build() -> None:
    summaries = {}
    for path in [PROCESSED / "core_paper_summaries.jsonl", PROCESSED / "extended_paper_summaries.jsonl"]:
        for row in read_jsonl(path):
            summaries[row["title"]] = row

    papers = []
    with (PROCESSED / "curated_papers.csv").open(encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            summary = summaries.get(row["title"], {})
            raw_direction = row.get("direction") or summary.get("direction") or "Domain Applications"
            direction = display_direction(row, raw_direction)
            abstract = re.sub(r"\s+", " ", row.get("abstract", "")).strip()
            first_sentence = re.split(r"(?<=[.!?])\s+", abstract)[0] if abstract else row["title"]
            summary_zh = summary.get("methods_zh") or ""
            if direction != raw_direction or "主要贡献在评测基准" in summary_zh:
                summary_zh = f"{METHOD_ZH_BY_DIRECTION.get(direction, METHOD_ZH_BY_DIRECTION['Domain Applications'])} 摘要中的问题陈述是：{first_sentence}"
            papers.append(
                {
                    "title": row["title"],
                    "url": row.get("url", ""),
                    "date": summary.get("date") or row.get("published", ""),
                    "venue": summary.get("venue_or_status") or row.get("venue", ""),
                    "direction": direction,
                    "stage": STAGE_BY_DIRECTION.get(direction, "Application"),
                    "tier": summary.get("relevance_tier") or row.get("relevance_tier", "extended"),
                    "datasets": summary.get("datasets_zh") or row.get("datasets", ""),
                    "methodZh": summary_zh
                    or "该论文围绕个性化 LLM 的方法、评测或应用展开，具体贡献需结合正文进一步核查。",
                    "methodEn": f"This paper studies {direction.lower()} for personalized LLMs. Public abstract signal: {first_sentence}",
                    "findingsZh": summary.get("main_findings_zh", ""),
                    "score": int(float(row.get("score") or 0)),
                }
            )

    direction_counts = {}
    for paper in papers:
        direction_counts[paper["direction"]] = direction_counts.get(paper["direction"], 0) + 1
    directions = [
        {"name": name, "nameZh": NAME_ZH.get(name, name), "count": count}
        for name, count in sorted(direction_counts.items(), key=lambda item: item[1], reverse=True)
    ]

    events = read_jsonl(REPORTS / "realtime_events.jsonl")
    run_started = next((event for event in events if event.get("type") == "run_started"), {})
    flow = {"nodes": run_started.get("nodes", []), "edges": run_started.get("edges", [])}

    payload = {
        "stats": {"rawRecords": 7199, "curatedPapers": len(papers)},
        "directions": directions,
        "stages": STAGES,
        "papers": papers,
        "flow": flow,
        "events": events,
    }
    (FRONTEND / "data.js").write_text(
        "window.SURVEY_DATA = " + json.dumps(payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {FRONTEND / 'data.js'} with {len(papers)} papers and {len(events)} events")


if __name__ == "__main__":
    build()
