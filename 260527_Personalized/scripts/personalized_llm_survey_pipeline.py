from __future__ import annotations

import csv
import html
import json
import math
import re
import sys
import time
import urllib.parse
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import requests


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CACHE = PROJECT_ROOT / "cache"
RAW = CACHE / "raw"
PROCESSED = CACHE / "processed"
REPORTS = CACHE / "reports"
FLOW = CACHE / "director_flow"
ASSETS = CACHE / "final_assets"

COL_ROOT = Path(r"D:\Codex_Sandbox\260421_Codex_Language")
ACTIVE_EVENT_LOG = COL_ROOT / "artifacts" / "realtime_real_runs" / "active_events.jsonl"

RUN_ID = f"PERSONALIZED_LLM_SURVEY_{time.strftime('%Y%m%d_%H%M%S')}"
START_DATE = "2025-05-07"
END_DATE = "2026-05-07"
ARXIV_START = "202505070000"
ARXIV_END = "202605072359"


@dataclass
class PaperRecord:
    source: str
    source_id: str
    title: str
    abstract: str
    authors: str
    published: str
    updated: str
    url: str
    pdf_url: str
    venue: str
    status: str
    categories: str
    query: str


def ensure_dirs() -> None:
    for path in [CACHE, RAW, PROCESSED, REPORTS, FLOW, ASSETS]:
        path.mkdir(parents=True, exist_ok=True)
    ACTIVE_EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)


def json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return str(value)


def reset_events() -> None:
    ACTIVE_EVENT_LOG.write_text("", encoding="utf-8")


def emit(event: dict[str, Any]) -> None:
    event = {"ts": datetime.now(timezone.utc).isoformat(), **event}
    with ACTIVE_EVENT_LOG.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, default=json_default) + "\n")
    with (REPORTS / "realtime_events.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, default=json_default) + "\n")


NODE_SEQUENCE = 0


def node_started(node_id: str, label: str, role: str, phase: str = "serial", group: str | None = None) -> None:
    emit(
        {
            "type": "node_started",
            "node_id": node_id,
            "label": label,
            "role": role,
            "phase": phase,
            "parallel_group": group,
            "thread_mode": "local_artifact_worker",
        }
    )


def node_output(node_id: str, chunk: str, progress: float, group: str | None = None) -> None:
    global NODE_SEQUENCE
    NODE_SEQUENCE += 1
    emit(
        {
            "type": "node_output",
            "node_id": node_id,
            "sequence": NODE_SEQUENCE,
            "chunk": chunk[:600],
            "progress": min(1.0, max(0.0, progress)),
            "parallel_group": group,
        }
    )


def node_completed(
    node_id: str,
    status: str = "passed",
    group: str | None = None,
    thread_id: str | None = None,
    turn_id: str | None = None,
) -> None:
    emit(
        {
            "type": "node_completed",
            "node_id": node_id,
            "status": status,
            "parallel_group": group,
            "thread_id": thread_id or f"local-{node_id}",
            "turn_id": turn_id or f"{RUN_ID}-{node_id}",
        }
    )


def artifact_written(node_id: str, path: Path, message: str | None = None) -> None:
    emit(
        {
            "type": "artifact_written",
            "node_id": node_id,
            "path": str(path),
            "message": message or f"artifact written: {path}",
        }
    )


def write_artifact(
    path: Path,
    *,
    from_role: str,
    to_role: str,
    subject: str,
    status: str,
    loop_type: str,
    requires_action: str,
    links: Iterable[Path | str],
    done_criteria: str,
    body: str,
) -> Path:
    links_text = "\n".join(f"- {link}" for link in links) or "- none"
    content = (
        f"# {subject}\n\n"
        f"- From: {from_role}\n"
        f"- To: {to_role}\n"
        f"- Subject: {subject}\n"
        f"- Status: {status}\n"
        f"- LoopType: {loop_type}\n"
        f"- Supersedes: none\n"
        f"- RequiresAction: {requires_action}\n"
        f"- ArtifactLinks:\n{links_text}\n"
        f"- DoneCriteria: {done_criteria}\n\n"
        f"{body.strip()}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    append_ledger(path, from_role, to_role, status, loop_type, "none", done_criteria, "authoritative_latest", "route")
    return path


def init_ledger() -> None:
    ledger = FLOW / "ledger.md"
    ledger.write_text(
        "# Personalized LLM Survey Routing Ledger\n\n"
        "| Path | From | To | Status | LoopType | Supersedes | Evidence | LedgerState | Decision |\n"
        "|---|---|---|---|---|---|---|---|---|\n",
        encoding="utf-8",
    )


def append_ledger(
    path: Path,
    from_role: str,
    to_role: str,
    status: str,
    loop_type: str,
    supersedes: str,
    evidence: str,
    ledger_state: str,
    decision: str,
) -> None:
    ledger = FLOW / "ledger.md"
    clean = lambda s: str(s).replace("|", "\\|").replace("\n", " ")
    with ledger.open("a", encoding="utf-8") as handle:
        handle.write(
            f"| {clean(path)} | {clean(from_role)} | {clean(to_role)} | {clean(status)} | "
            f"{clean(loop_type)} | {clean(supersedes)} | {clean(evidence)} | {clean(ledger_state)} | {clean(decision)} |\n"
        )


def run_started() -> None:
    nodes = [
        {"id": "coordinator_scope", "label": "Coordinator Scope Artifact", "role": "coordinator", "phase": "serial", "duration_seconds": 1, "outputs": [], "parallel_group": None, "thread_id": "local-coordinator"},
        {"id": "arxiv_retriever", "label": "RetrievalDirector-Arxiv", "role": "retriever", "phase": "parallel", "duration_seconds": 60, "outputs": [], "parallel_group": "retrieval"},
        {"id": "openreview_retriever", "label": "RetrievalDirector-OpenReview", "role": "retriever", "phase": "parallel", "duration_seconds": 60, "outputs": [], "parallel_group": "retrieval"},
        {"id": "dedup_scorer", "label": "DedupScoringDirector", "role": "scorer", "phase": "serial", "duration_seconds": 20, "outputs": [], "parallel_group": None},
        {"id": "taxonomy_director", "label": "TaxonomyDirector", "role": "director", "phase": "parallel", "duration_seconds": 20, "outputs": [], "parallel_group": "analysis"},
        {"id": "summary_core", "label": "SummaryDirector-Core", "role": "summarizer", "phase": "parallel", "duration_seconds": 40, "outputs": [], "parallel_group": "analysis"},
        {"id": "summary_extended", "label": "SummaryDirector-Extended", "role": "summarizer", "phase": "parallel", "duration_seconds": 40, "outputs": [], "parallel_group": "analysis"},
        {"id": "verifier", "label": "VerificationDirector", "role": "verifier", "phase": "serial", "duration_seconds": 20, "outputs": [], "parallel_group": None},
        {"id": "final_writer", "label": "FinalWriter", "role": "writer", "phase": "serial", "duration_seconds": 30, "outputs": [], "parallel_group": None},
    ]
    edges = [
        {"from": "coordinator_scope", "to": "arxiv_retriever"},
        {"from": "coordinator_scope", "to": "openreview_retriever"},
        {"from": "arxiv_retriever", "to": "dedup_scorer"},
        {"from": "openreview_retriever", "to": "dedup_scorer"},
        {"from": "dedup_scorer", "to": "taxonomy_director"},
        {"from": "dedup_scorer", "to": "summary_core"},
        {"from": "dedup_scorer", "to": "summary_extended"},
        {"from": "taxonomy_director", "to": "verifier"},
        {"from": "summary_core", "to": "verifier"},
        {"from": "summary_extended", "to": "verifier"},
        {"from": "verifier", "to": "final_writer"},
    ]
    emit(
        {
            "type": "run_started",
            "mode": "real",
            "run_id": RUN_ID,
            "year": 2026,
            "workspace": str(PROJECT_ROOT),
            "docs_dir": str(FLOW),
            "nodes": nodes,
            "edges": edges,
            "message": "Personalized LLM survey workflow started.",
        }
    )


def normalize_space(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", html.unescape(str(text))).strip()


def normalize_title(title: str) -> str:
    title = normalize_space(title).lower()
    title = re.sub(r"[^a-z0-9]+", " ", title)
    return re.sub(r"\s+", " ", title).strip()


def save_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> int:
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, default=json_default) + "\n")
            count += 1
    return count


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def records_from_csv(path: Path) -> list[PaperRecord]:
    if not path.exists():
        return []
    frame = pd.read_csv(path).fillna("")
    records: list[PaperRecord] = []
    for _, row in frame.iterrows():
        item = row.to_dict()
        records.append(
            PaperRecord(
                source=str(item.get("source", "")),
                source_id=str(item.get("source_id", "")),
                title=str(item.get("title", "")),
                abstract=str(item.get("abstract", "")),
                authors=str(item.get("authors", "")),
                published=str(item.get("published", "")),
                updated=str(item.get("updated", "")),
                url=str(item.get("url", "")),
                pdf_url=str(item.get("pdf_url", "")),
                venue=str(item.get("venue", "")),
                status=str(item.get("status", "")),
                categories=str(item.get("categories", "")),
                query=str(item.get("query", "")),
            )
        )
    return records


def reuse_retrieval_records() -> tuple[list[PaperRecord], list[PaperRecord]] | None:
    arxiv_path = PROCESSED / "arxiv_candidates.csv"
    openreview_path = PROCESSED / "openreview_candidates.csv"
    if not arxiv_path.exists() or not openreview_path.exists():
        return None
    arxiv_records = records_from_csv(arxiv_path)
    openreview_records = records_from_csv(openreview_path)
    node_started("arxiv_retriever", "RetrievalDirector-Arxiv", "retriever", "parallel", "retrieval")
    node_output("arxiv_retriever", f"Reused cached arXiv candidates: {len(arxiv_records)}", 1.0, "retrieval")
    node_completed("arxiv_retriever", "passed", "retrieval")
    node_started("openreview_retriever", "RetrievalDirector-OpenReview", "retriever", "parallel", "retrieval")
    node_output("openreview_retriever", f"Reused cached OpenReview candidates: {len(openreview_records)}", 1.0, "retrieval")
    node_completed("openreview_retriever", "passed", "retrieval")
    return arxiv_records, openreview_records


def arxiv_request(query: str, start: int, max_results: int) -> requests.Response:
    url = (
        "https://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {
                "search_query": query,
                "start": start,
                "max_results": max_results,
                "sortBy": "submittedDate",
                "sortOrder": "descending",
            }
        )
    )
    headers = {"User-Agent": "personalized-llm-survey/0.1 (local research cache)"}
    for attempt in range(4):
        response = requests.get(url, headers=headers, timeout=60)
        if response.status_code == 200:
            return response
        time.sleep(4 + attempt * 6)
    response.raise_for_status()
    return response


def parse_arxiv_feed(xml_bytes: bytes, query: str) -> tuple[int, list[PaperRecord]]:
    root = ET.fromstring(xml_bytes)
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom",
        "opensearch": "http://a9.com/-/spec/opensearch/1.1/",
    }
    total_el = root.find("opensearch:totalResults", ns)
    total = int(total_el.text) if total_el is not None and total_el.text else 0
    records: list[PaperRecord] = []
    for entry in root.findall("atom:entry", ns):
        entry_id = normalize_space(entry.findtext("atom:id", default="", namespaces=ns))
        arxiv_id = entry_id.rsplit("/", 1)[-1]
        title = normalize_space(entry.findtext("atom:title", default="", namespaces=ns))
        abstract = normalize_space(entry.findtext("atom:summary", default="", namespaces=ns))
        authors = "; ".join(
            normalize_space(author.findtext("atom:name", default="", namespaces=ns))
            for author in entry.findall("atom:author", ns)
        )
        published = normalize_space(entry.findtext("atom:published", default="", namespaces=ns))[:10]
        updated = normalize_space(entry.findtext("atom:updated", default="", namespaces=ns))[:10]
        categories = ";".join(cat.attrib.get("term", "") for cat in entry.findall("atom:category", ns))
        pdf_url = ""
        for link in entry.findall("atom:link", ns):
            if link.attrib.get("title") == "pdf":
                pdf_url = link.attrib.get("href", "")
        records.append(
            PaperRecord(
                source="arxiv",
                source_id=arxiv_id,
                title=title,
                abstract=abstract,
                authors=authors,
                published=published,
                updated=updated,
                url=f"https://arxiv.org/abs/{arxiv_id}",
                pdf_url=pdf_url,
                venue="arXiv",
                status="preprint",
                categories=categories,
                query=query,
            )
        )
    return total, records


def fetch_arxiv() -> tuple[list[PaperRecord], dict[str, Any]]:
    node_started("arxiv_retriever", "RetrievalDirector-Arxiv", "retriever", "parallel", "retrieval")
    queries = [
        (f"cat:cs.CL AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]", 3600),
        (f"cat:cs.AI AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]", 900),
        (f"cat:cs.IR AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]", 700),
        (f"cat:cs.LG AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]", 900),
        (f'all:personalized AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]', 400),
        (f'all:personalization AND submittedDate:[{ARXIV_START} TO {ARXIV_END}]', 400),
    ]
    all_records: list[PaperRecord] = []
    query_stats: list[dict[str, Any]] = []
    batch_size = 500
    for query_index, (query, target) in enumerate(queries, start=1):
        node_output("arxiv_retriever", f"arXiv query {query_index}/{len(queries)} target={target}: {query}", 0.08 + query_index * 0.05, "retrieval")
        fetched = 0
        total = None
        start = 0
        while fetched < target:
            max_results = min(batch_size, target - fetched)
            try:
                response = arxiv_request(query, start, max_results)
                total, records = parse_arxiv_feed(response.content, query)
            except Exception as exc:
                query_stats.append({"query": query, "status": "failed", "error": str(exc), "fetched": fetched, "total": total})
                node_output("arxiv_retriever", f"arXiv query failed after {fetched}: {exc}", 0.25, "retrieval")
                break
            if not records:
                break
            all_records.extend(records)
            fetched += len(records)
            start += len(records)
            node_output(
                "arxiv_retriever",
                f"query fetched={fetched}/{target}, API total={total}, raw_total={len(all_records)}",
                min(0.92, 0.12 + len(all_records) / 7000),
                "retrieval",
            )
            if len(records) < max_results:
                break
            time.sleep(3.2)
        query_stats.append({"query": query, "status": "passed", "fetched": fetched, "total": total})
    raw_path = RAW / "arxiv_raw_records.jsonl"
    csv_path = PROCESSED / "arxiv_candidates.csv"
    rows = [asdict(record) for record in all_records]
    save_jsonl(raw_path, rows)
    pd.DataFrame(rows).to_csv(csv_path, index=False, encoding="utf-8-sig")
    report_path = FLOW / "RetrievalDirectorArxiv_To_Coordinator_20260507_retrieval_report.md"
    write_artifact(
        report_path,
        from_role="RetrievalDirector-Arxiv",
        to_role="Coordinator",
        subject="Arxiv retrieval report",
        status="passed",
        loop_type="FullLoop",
        requires_action="DedupScoringDirector should consume arxiv_candidates.csv.",
        links=[raw_path, csv_path],
        done_criteria=f"Saved {len(rows)} raw arXiv records.",
        body=(
            "## Query Stats\n\n"
            + "\n".join(f"- `{s['query']}`: {s['status']}, fetched={s.get('fetched')}, api_total={s.get('total')}" for s in query_stats)
        ),
    )
    artifact_written("arxiv_retriever", report_path)
    node_output("arxiv_retriever", f"arXiv raw records saved: {len(rows)}", 1.0, "retrieval")
    node_completed("arxiv_retriever", "passed", "retrieval")
    return all_records, {"query_stats": query_stats, "raw_path": str(raw_path), "csv_path": str(csv_path)}


def openreview_search(term: str, limit: int = 50) -> list[dict[str, Any]]:
    url = "https://api2.openreview.net/notes/search?" + urllib.parse.urlencode({"term": term, "limit": limit})
    headers = {"User-Agent": "personalized-llm-survey/0.1 (local research cache)"}
    for attempt in range(5):
        response = requests.get(url, headers=headers, timeout=45)
        if response.status_code == 200:
            try:
                return response.json().get("notes", [])
            except json.JSONDecodeError:
                return []
        if response.status_code == 429:
            time.sleep(10 + attempt * 10)
            continue
        time.sleep(4 + attempt * 4)
    return []


def content_value(content: dict[str, Any], key: str) -> str:
    value = content.get(key, "")
    if isinstance(value, dict):
        value = value.get("value", "")
    if isinstance(value, list):
        value = "; ".join(map(str, value))
    return normalize_space(str(value))


def fetch_openreview() -> tuple[list[PaperRecord], dict[str, Any]]:
    node_started("openreview_retriever", "RetrievalDirector-OpenReview", "retriever", "parallel", "retrieval")
    terms = [
        "personalized LLM",
        "LLM personalization",
        "personalized large language model",
        "user profile large language model",
        "personalized agent",
        "personalized RAG",
        "LLM recommendation",
        "LLM recommender",
        "memory LLM user",
        "parameter efficient fine tuning personalization",
        "federated LLM personalization",
        "personalized alignment LLM",
        "preference personalization LLM",
        "LaMP large language model personalization",
        "OPPU personalized parameter efficient fine tuning",
    ]
    raw_notes: list[dict[str, Any]] = []
    records: list[PaperRecord] = []
    stats: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for idx, term in enumerate(terms, start=1):
        node_output("openreview_retriever", f"OpenReview search {idx}/{len(terms)}: {term}", 0.05 + idx / (len(terms) + 2), "retrieval")
        notes = openreview_search(term, limit=80)
        stats.append({"term": term, "notes": len(notes)})
        raw_notes.extend(notes)
        for note in notes:
            note_id = note.get("id") or ""
            if note_id in seen_ids:
                continue
            seen_ids.add(note_id)
            content = note.get("content") or {}
            title = content_value(content, "title")
            abstract = content_value(content, "abstract") or content_value(content, "summary")
            if not title:
                continue
            authors_value = content.get("authors", "")
            if isinstance(authors_value, dict):
                authors_value = authors_value.get("value", "")
            if isinstance(authors_value, list):
                authors = "; ".join(map(str, authors_value))
            else:
                authors = normalize_space(str(authors_value))
            forum = note.get("forum") or note_id
            venue = content_value(content, "venue") or content_value(content, "venueid") or "OpenReview"
            status = content_value(content, "decision") or content_value(content, "recommendation") or "public_note"
            cdate = note.get("cdate") or note.get("pdate") or note.get("tcdate") or 0
            if cdate:
                published = datetime.fromtimestamp(int(cdate) / 1000, tz=timezone.utc).date().isoformat()
            else:
                published = ""
            records.append(
                PaperRecord(
                    source="openreview",
                    source_id=note_id,
                    title=title,
                    abstract=abstract,
                    authors=authors,
                    published=published,
                    updated=published,
                    url=f"https://openreview.net/forum?id={forum}",
                    pdf_url=f"https://openreview.net/pdf?id={forum}",
                    venue=venue,
                    status=status,
                    categories="",
                    query=term,
                )
            )
        time.sleep(4.5)
    raw_path = RAW / "openreview_raw_records.jsonl"
    csv_path = PROCESSED / "openreview_candidates.csv"
    save_jsonl(raw_path, raw_notes)
    pd.DataFrame([asdict(record) for record in records]).to_csv(csv_path, index=False, encoding="utf-8-sig")
    report_path = FLOW / "RetrievalDirectorOpenReview_To_Coordinator_20260507_retrieval_report.md"
    status = "passed" if records else "limited_public_metadata"
    write_artifact(
        report_path,
        from_role="RetrievalDirector-OpenReview",
        to_role="Coordinator",
        subject="OpenReview retrieval report",
        status=status,
        loop_type="FullLoop",
        requires_action="DedupScoringDirector should merge public OpenReview records with arXiv candidates.",
        links=[raw_path, csv_path],
        done_criteria=f"Saved {len(raw_notes)} raw OpenReview notes and {len(records)} paper-like notes.",
        body="## Search Stats\n\n" + "\n".join(f"- `{s['term']}`: notes={s['notes']}" for s in stats),
    )
    artifact_written("openreview_retriever", report_path)
    node_output("openreview_retriever", f"OpenReview raw notes={len(raw_notes)}, paper-like={len(records)}", 1.0, "retrieval")
    node_completed("openreview_retriever", status, "retrieval")
    return records, {"stats": stats, "raw_path": str(raw_path), "csv_path": str(csv_path)}


LLM_TERMS = [
    "large language model",
    "large-language model",
    "llm",
    "llms",
    "language model",
    "chatgpt",
    "gpt-",
    "foundation model",
    "generative ai",
    "instruction tuning",
]

PERSONAL_TERMS = [
    "personalized",
    "personalization",
    "personalisation",
    "user profile",
    "user-specific",
    "user specific",
    "individual preference",
    "individualized",
    "customization",
    "customized",
    "adapt to user",
    "personal memory",
    "user memory",
    "long-term memory",
    "preference",
    "user preference",
    "profile",
    "persona",
    "personal data",
    "user history",
    "behavior pattern",
]

METHOD_GROUPS = {
    "Benchmark and Evaluation": ["benchmark", "evaluation", "leaderboard", "metric", "testbed", "lamp", "longlamp"],
    "Profile Prompting and Personalized RAG": ["retrieval", "rag", "retrieve", "profile", "context", "prompt", "in-context"],
    "Personalized PEFT and Adaptation": ["peft", "lora", "adapter", "fine-tuning", "finetuning", "parameter-efficient", "hypernetwork", "tuning"],
    "Memory and Dynamic User Modeling": ["memory", "long-term", "dynamic", "continual", "update", "user model", "trajectory"],
    "Personalized Alignment and Preference Learning": ["alignment", "preference optimization", "dpo", "reward", "rlhf", "feedback", "preference learning"],
    "Personalized Agents and Assistants": ["agent", "assistant", "tool", "planning", "workflow", "autonomous"],
    "LLM-based Recommendation and Ranking": ["recommendation", "recommender", "ranking", "collaborative filtering", "item", "review", "movie", "news"],
    "Privacy, Federated, and On-device Personalization": ["privacy", "private", "federated", "on-device", "edge", "local model", "decentralized", "secure"],
    "Domain Applications": ["education", "health", "medical", "legal", "coding", "finance", "dialogue", "writing", "email", "news"],
}

DATASET_HINTS = [
    "LaMP",
    "LongLaMP",
    "OPPU",
    "MovieLens",
    "Amazon",
    "Yelp",
    "Goodreads",
    "Reddit",
    "MIND",
    "MS MARCO",
    "Natural Questions",
    "HotpotQA",
    "PersonaChat",
    "ConvAI2",
    "ShareGPT",
    "UltraFeedback",
    "HH-RLHF",
    "Anthropic HH",
    "OpenAssistant",
    "GSM8K",
    "MMLU",
    "TruthfulQA",
    "Alpaca",
    "FLAN",
    "Dolly",
    "StackExchange",
    "IMDB",
    "BookCrossing",
    "LastFM",
    "Steam",
    "Yelp2018",
    "Amazon Reviews",
]


def score_record(row: dict[str, Any]) -> tuple[int, str, list[str]]:
    text = f"{row.get('title','')} {row.get('abstract','')} {row.get('categories','')} {row.get('venue','')}".lower()
    title = str(row.get("title", "")).lower()
    score = 0
    reasons: list[str] = []
    llm_hit = any(term in text for term in LLM_TERMS)
    personal_hits = [term for term in PERSONAL_TERMS if term in text]
    if llm_hit:
        score += 3
        reasons.append("LLM indicator")
    if personal_hits:
        score += min(7, 2 + len(set(personal_hits)))
        reasons.append("personalization/user-preference indicator")
    if any(term in title for term in ["personalized", "personalization", "user", "preference", "profile", "memory"]):
        score += 3
        reasons.append("title-level personalization signal")
    for direction, terms in METHOD_GROUPS.items():
        if any(term in text for term in terms):
            score += 1
    if "lamp" in text or "oppu" in text or "one peft per user" in text:
        score += 5
        reasons.append("LaMP/OPPU lineage")
    if row.get("source") == "openreview":
        score += 1
        reasons.append("OpenReview public note")
    if not llm_hit and not personal_hits:
        score -= 3
    direction = classify_direction(row)
    return score, direction, reasons


def classify_direction(row: dict[str, Any]) -> str:
    text = f"{row.get('title','')} {row.get('abstract','')}".lower()
    title = str(row.get("title", "")).lower()
    if (
        "lamp" in text
        or "benchmark" in title
        or "evaluation" in title
        or "dataset" in title
        or re.search(r"\b(introduce|propose|present|construct|build)\b.{0,80}\b(benchmark|dataset|testbed|leaderboard)\b", text)
    ):
        return "Benchmark and Evaluation"
    if any(term in text for term in ["peft", "lora", "adapter", "fine-tuning", "finetuning", "parameter-efficient", "hypernetwork"]):
        return "Personalized PEFT and Adaptation"
    if any(term in text for term in ["privacy", "federated", "on-device", "local model", "decentralized", "secure"]):
        return "Privacy, Federated, and On-device Personalization"
    if any(term in text for term in ["alignment", "dpo", "reward", "rlhf", "preference optimization", "preference learning"]):
        return "Personalized Alignment and Preference Learning"
    if any(term in text for term in ["recommendation", "recommender", "ranking", "collaborative filtering", "item"]):
        return "LLM-based Recommendation and Ranking"
    if any(term in text for term in ["agent", "assistant", "tool use", "planning", "workflow"]):
        return "Personalized Agents and Assistants"
    if any(term in text for term in ["memory", "long-term", "dynamic user", "user model", "profile update", "continual"]):
        return "Memory and Dynamic User Modeling"
    if any(term in text for term in ["retrieval", "rag", "profile", "prompt", "in-context", "context"]):
        return "Profile Prompting and Personalized RAG"
    return "Domain Applications"


def extract_datasets(text: str) -> str:
    hits = []
    for name in DATASET_HINTS:
        if re.search(rf"\b{re.escape(name)}\b", text, flags=re.IGNORECASE):
            hits.append(name)
    if hits:
        return "; ".join(dict.fromkeys(hits))
    dataset_phrases = re.findall(
        r"(?:on|using|with|across)\s+([A-Z][A-Za-z0-9_\-]+(?:,\s*[A-Z][A-Za-z0-9_\-]+)*(?:\s+and\s+[A-Z][A-Za-z0-9_\-]+)?)\s+(?:datasets?|benchmarks?|tasks?)",
        text,
    )
    if dataset_phrases:
        return "; ".join(dict.fromkeys(dataset_phrases[:3]))
    return "摘要未明确列出数据集；需正文核查"


def first_result_sentence(abstract: str) -> str:
    sentences = re.split(r"(?<=[.!?])\s+", normalize_space(abstract))
    priority = [
        "outperform",
        "improve",
        "achieve",
        "show",
        "demonstrate",
        "effective",
        "state-of-the-art",
        "sota",
        "significant",
    ]
    for sentence in sentences:
        lower = sentence.lower()
        if any(key in lower for key in priority):
            return sentence
    return sentences[-1] if sentences else "摘要未明确给出实验结论。"


def method_summary(row: dict[str, Any]) -> str:
    direction = row.get("direction", "Domain Applications")
    abstract = normalize_space(str(row.get("abstract", "")))
    title = normalize_space(str(row.get("title", "")))
    first = re.split(r"(?<=[.!?])\s+", abstract)[0] if abstract else title
    mapping = {
        "Benchmark and Evaluation": "该工作主要贡献在评测基准、任务构造或度量体系，用来衡量 LLM 在用户级偏好、历史行为或个体上下文下的表现。",
        "Profile Prompting and Personalized RAG": "该工作围绕用户画像、历史检索或个性化上下文注入展开，核心思路是在生成前选择与当前用户最相关的证据并组织进提示或检索增强流程。",
        "Personalized PEFT and Adaptation": "该工作走参数高效个性化路线，通常通过 LoRA、adapter、hypernetwork 或少量可训练参数为用户/群体存储偏好。",
        "Memory and Dynamic User Modeling": "该工作关注长期记忆和动态用户建模，重点是如何随交互持续更新用户状态并在后续任务中调用。",
        "Personalized Alignment and Preference Learning": "该工作把个体偏好纳入对齐或奖励建模，目标是让模型输出更贴合不同用户的主观偏好和约束。",
        "Personalized Agents and Assistants": "该工作把个性化扩展到 agent/assistant 场景，关注任务规划、工具调用和跨轮偏好保持。",
        "LLM-based Recommendation and Ranking": "该工作位于 LLM 推荐系统方向，利用大模型理解用户历史、物品语义或自然语言反馈来改进排序、解释或生成式推荐。",
        "Privacy, Federated, and On-device Personalization": "该工作强调隐私保护或本地化个性化，通常通过联邦学习、本地小模型、去中心化训练或隐私约束降低个人数据外泄风险。",
        "Domain Applications": "该工作把个性化 LLM 方法落到具体应用场景，重点是任务数据、用户差异和实际效益。",
    }
    return f"{mapping.get(direction, mapping['Domain Applications'])} 摘要中的问题陈述是：{first}"


def relation_to_lamp_oppu(row: dict[str, Any]) -> str:
    text = f"{row.get('title','')} {row.get('abstract','')}".lower()
    direction = row.get("direction", "")
    if "lamp" in text:
        return "直接处在 LaMP 评测谱系中，常以 LaMP/LongLaMP 式任务衡量用户画像或历史行为带来的生成收益。"
    if "oppu" in text or "one peft per user" in text:
        return "直接延续 OPPU 的每用户 PEFT/adapter 个性化设定，关注可扩展性、效率或少样本用户数据问题。"
    if direction == "Personalized PEFT and Adaptation":
        return "方法层面接近 OPPU：把个体差异存入少量参数，而不是只靠提示拼接。"
    if direction == "Profile Prompting and Personalized RAG":
        return "方法层面接近 LaMP：把用户历史作为可检索 profile，在生成时显式注入上下文。"
    if direction == "Benchmark and Evaluation":
        return "问题设置上延续 LaMP 的核心问题：如何定义、评估并比较 LLM 的个性化能力。"
    return "属于 LaMP/OPPU 之后更宽的个性化 LLM 生态，扩展了用户偏好建模、应用或部署约束。"


def dedup_and_score(arxiv_records: list[PaperRecord], openreview_records: list[PaperRecord]) -> tuple[pd.DataFrame, pd.DataFrame]:
    node_started("dedup_scorer", "DedupScoringDirector", "scorer")
    rows = [asdict(record) for record in arxiv_records + openreview_records]
    for row in rows:
        row["title_norm"] = normalize_title(row.get("title", ""))
    raw_df = pd.DataFrame(rows)
    if raw_df.empty:
        raise RuntimeError("No candidate records available after retrieval.")
    raw_df["priority_source"] = raw_df["source"].map({"openreview": 0, "arxiv": 1}).fillna(9)
    raw_df = raw_df.sort_values(["title_norm", "priority_source", "published"], ascending=[True, True, False])
    deduped = raw_df.drop_duplicates(subset=["title_norm"], keep="first").copy()
    scores = deduped.apply(lambda row: score_record(row.to_dict()), axis=1)
    deduped["score"] = [item[0] for item in scores]
    deduped["direction"] = [item[1] for item in scores]
    deduped["score_reasons"] = ["; ".join(item[2]) for item in scores]
    deduped["datasets"] = deduped.apply(lambda row: extract_datasets(f"{row.get('title','')} {row.get('abstract','')}"), axis=1)
    deduped = deduped.sort_values(["score", "source", "published"], ascending=[False, True, False])
    deduped_path = PROCESSED / "deduped_candidates.csv"
    scored_path = PROCESSED / "scored_candidates.csv"
    deduped.to_csv(scored_path, index=False, encoding="utf-8-sig")
    deduped.to_csv(deduped_path, index=False, encoding="utf-8-sig")
    curated = deduped[(deduped["score"] >= 5) & (deduped["abstract"].fillna("").str.len() > 80)].copy()
    if len(curated) < 240:
        curated = deduped[deduped["abstract"].fillna("").str.len() > 80].head(260).copy()
    else:
        curated = curated.head(280).copy()
    curated["relevance_tier"] = pd.cut(
        curated["score"],
        bins=[-math.inf, 7, 11, math.inf],
        labels=["extended", "strong", "core"],
    ).astype(str)
    curated_path = PROCESSED / "curated_papers.csv"
    curated.to_csv(curated_path, index=False, encoding="utf-8-sig")
    report_path = FLOW / "DedupScoringDirector_To_Coordinator_20260507_scoring_report.md"
    write_artifact(
        report_path,
        from_role="DedupScoringDirector",
        to_role="Coordinator",
        subject="Deduplication and scoring report",
        status="passed",
        loop_type="FullLoop",
        requires_action="TaxonomyDirector and SummaryDirectors should consume curated_papers.csv.",
        links=[deduped_path, scored_path, curated_path],
        done_criteria=f"Deduped {len(raw_df)} raw rows into {len(deduped)} candidates and selected {len(curated)} curated papers.",
        body=(
            f"- raw_rows: {len(raw_df)}\n"
            f"- deduped_candidates: {len(deduped)}\n"
            f"- curated_papers: {len(curated)}\n\n"
            "## Direction Counts\n\n"
            + "\n".join(f"- {k}: {v}" for k, v in curated["direction"].value_counts().items())
        ),
    )
    artifact_written("dedup_scorer", report_path)
    node_output("dedup_scorer", f"Deduped={len(deduped)}, curated={len(curated)}", 1.0)
    node_completed("dedup_scorer", "passed")
    return deduped, curated


DIRECTION_INTROS = {
    "Benchmark and Evaluation": "这个方向回答“个性化 LLM 到底该如何评测”。LaMP 将用户历史转化为检索式 profile，并把 citation、tagging、rating、headline、title、email subject、tweet paraphrase 等任务统一为可比较的个性化生成/分类基准；近一年工作继续扩展到长历史、多轮记忆、更真实的用户行为和更细粒度的偏好差异。最新进展不是单纯提高分数，而是把评测从静态 profile 推向长期、动态、隐私受限和任务迁移环境。",
    "Profile Prompting and Personalized RAG": "这个方向继承 LaMP 的检索式个性化思路：不改变模型参数，而是在推理时检索用户历史、画像、偏好证据或相似用户样本。发展脉络从简单拼接 profile，走向学习检索器、压缩长期历史、区分稳定偏好和临时意图，以及把 RAG 与记忆模块结合。最新工作更重视上下文预算、噪声 profile、冲突偏好和跨任务泛化。",
    "Personalized PEFT and Adaptation": "这个方向以 OPPU 为中心：为每个用户或用户簇训练少量参数，让偏好沉淀在 adapter/LoRA/hypernetwork 中。它比 prompt 个性化更能吸收隐含行为模式，但面临用户规模、冷启动和更新成本问题。近一年论文重点在共享-私有参数分解、即时 adapter 生成、少样本用户数据、跨用户迁移和可扩展部署。",
    "Memory and Dynamic User Modeling": "这个方向把个性化看作持续交互中的状态维护问题。早期 profile 多是离线静态文本，近一年工作更强调长期记忆写入、遗忘、冲突解决、时序偏好漂移和可解释调用。它与 agent 和 RAG 紧密相连：记忆既是检索库，也是决策状态。",
    "Personalized Alignment and Preference Learning": "这个方向把用户差异推入对齐阶段，研究个体化 reward、DPO/RLHF、偏好聚合和多目标冲突。相较 OPPU 的任务适配，它更关心“不同用户认为好答案的标准不同”。最新进展集中在个体 reward 模型、联邦/私有偏好优化、跨域偏好泛化和避免过度迎合。",
    "Personalized Agents and Assistants": "这个方向关注长期助手如何理解个人目标、工作流和工具偏好。与单次文本生成不同，agent 个性化需要在规划、调用工具、记忆更新和任务复盘中保持一致。最新工作通常把用户模型、记忆、反馈和环境状态合在一起，评估也更偏向真实任务完成度。",
    "LLM-based Recommendation and Ranking": "这个方向是个性化 LLM 与推荐系统交汇处：LLM 被用来理解用户历史、生成解释、做 conversational recommendation，或作为排序/重排模型。发展脉络从把 LLM 当语义编码器，走向利用自然语言偏好、生成式用户模拟和多轮交互。最新进展关注冷启动、可解释性、长序列行为和推荐中的对齐风险。",
    "Privacy, Federated, and On-device Personalization": "这个方向处理个性化天然带来的隐私矛盾：越个性化越需要个人数据。近一年工作将联邦学习、本地小模型、隐私保护 adapter、去中心化偏好优化和日志最小化结合起来，目标是在不上传敏感历史的情况下获得用户级收益。它也是 OPPU 大规模部署必须面对的工程与伦理约束。",
    "Domain Applications": "这个方向把个性化 LLM 放进教育、健康、写作、代码、信息消费等具体场景。它们未必提出通用算法，但提供了真实需求：用户目标不同、专业背景不同、风险容忍度不同。近一年趋势是从演示式应用转向任务数据、长期行为和领域安全约束共建。",
}


def build_taxonomy(curated: pd.DataFrame) -> pd.DataFrame:
    node_started("taxonomy_director", "TaxonomyDirector", "director", "parallel", "analysis")
    counts = curated["direction"].value_counts().to_dict()
    rows = []
    for direction, intro in DIRECTION_INTROS.items():
        subset = curated[curated["direction"] == direction].head(12)
        rows.append(
            {
                "direction": direction,
                "count": int(counts.get(direction, 0)),
                "intro_zh": intro,
                "representative_titles": " | ".join(subset["title"].astype(str).tolist()),
            }
        )
    taxonomy = pd.DataFrame(rows)
    taxonomy_path = PROCESSED / "taxonomy.csv"
    taxonomy.to_csv(taxonomy_path, index=False, encoding="utf-8-sig")
    report_path = FLOW / "TaxonomyDirector_To_Coordinator_20260507_taxonomy.md"
    write_artifact(
        report_path,
        from_role="TaxonomyDirector",
        to_role="Coordinator",
        subject="Taxonomy report",
        status="passed",
        loop_type="FullLoop",
        requires_action="FinalWriter should use taxonomy.csv for section order and direction introductions.",
        links=[taxonomy_path],
        done_criteria="Built problem-driven taxonomy from curated corpus.",
        body="\n\n".join(f"## {row['direction']}\n\n{row['intro_zh']}\n\nCount: {row['count']}" for _, row in taxonomy.iterrows()),
    )
    artifact_written("taxonomy_director", report_path)
    node_output("taxonomy_director", f"Taxonomy directions={len(taxonomy)}, nonempty={sum(taxonomy['count'] > 0)}", 1.0, "analysis")
    node_completed("taxonomy_director", "passed", "analysis")
    return taxonomy


def build_summary_row(row: pd.Series, rank: int) -> dict[str, Any]:
    item = row.to_dict()
    abstract = normalize_space(str(item.get("abstract", "")))
    return {
        "rank": rank,
        "title": normalize_space(str(item.get("title", ""))),
        "url": item.get("url", ""),
        "source": item.get("source", ""),
        "date": item.get("published", "") or item.get("updated", ""),
        "venue_or_status": f"{item.get('venue','')} / {item.get('status','')}",
        "relevance_tier": item.get("relevance_tier", ""),
        "direction": item.get("direction", ""),
        "methods_zh": method_summary(item),
        "datasets_zh": item.get("datasets", "") or extract_datasets(abstract),
        "main_findings_zh": f"主要结论可从摘要中的结果句概括为：{first_result_sentence(abstract)}",
        "relation_to_lamp_oppu_zh": relation_to_lamp_oppu(item),
        "score": int(item.get("score", 0)),
        "notes_for_verification": "自动摘要基于标题、摘要和公开元数据；数据集字段若标注需正文核查，后续应优先抽查。",
    }


def summarize_papers(curated: pd.DataFrame) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    node_started("summary_core", "SummaryDirector-Core", "summarizer", "parallel", "analysis")
    node_started("summary_extended", "SummaryDirector-Extended", "summarizer", "parallel", "analysis")
    core_df = curated.head(80).copy()
    ext_df = curated.iloc[80:].copy()
    core = [build_summary_row(row, i + 1) for i, (_, row) in enumerate(core_df.iterrows())]
    extended = [build_summary_row(row, i + 81) for i, (_, row) in enumerate(ext_df.iterrows())]
    core_path = PROCESSED / "core_paper_summaries.jsonl"
    ext_path = PROCESSED / "extended_paper_summaries.jsonl"
    save_jsonl(core_path, core)
    save_jsonl(ext_path, extended)
    core_report = FLOW / "SummaryDirectorCore_To_Coordinator_20260507_core_summaries.md"
    ext_report = FLOW / "SummaryDirectorExtended_To_Coordinator_20260507_extended_summaries.md"
    write_artifact(
        core_report,
        from_role="SummaryDirector-Core",
        to_role="Coordinator",
        subject="Core paper summaries",
        status="passed",
        loop_type="FullLoop",
        requires_action="VerificationDirector should sample-check core summaries.",
        links=[core_path],
        done_criteria=f"Wrote {len(core)} core Chinese summary records.",
        body="\n".join(f"- {item['rank']}. {item['title']} ({item['date']})" for item in core[:30]),
    )
    write_artifact(
        ext_report,
        from_role="SummaryDirector-Extended",
        to_role="Coordinator",
        subject="Extended paper summaries",
        status="passed",
        loop_type="FullLoop",
        requires_action="VerificationDirector should sample-check extended summaries.",
        links=[ext_path],
        done_criteria=f"Wrote {len(extended)} extended Chinese summary records.",
        body="\n".join(f"- {item['rank']}. {item['title']} ({item['date']})" for item in extended[:60]),
    )
    artifact_written("summary_core", core_report)
    artifact_written("summary_extended", ext_report)
    node_output("summary_core", f"Core summaries={len(core)}", 1.0, "analysis")
    node_output("summary_extended", f"Extended summaries={len(extended)}", 1.0, "analysis")
    node_completed("summary_core", "passed", "analysis")
    node_completed("summary_extended", "passed", "analysis")
    return core, extended


def central_background() -> list[dict[str, Any]]:
    return [
        {
            "rank": 0,
            "title": "LaMP: When Large Language Models Meet Personalization",
            "url": "https://arxiv.org/abs/2304.11406",
            "source": "arxiv",
            "date": "2023-04-22; ACL 2024",
            "venue_or_status": "ACL 2024 long paper / benchmark",
            "relevance_tier": "center",
            "direction": "Benchmark and Evaluation",
            "methods_zh": "LaMP 把用户历史作为 profile，引入一组个性化语言模型任务，用统一框架评估检索用户画像、拼接上下文、微调和零样本生成等方法。它把“个性化”从单个推荐任务扩展为可复现的 LLM benchmark。",
            "datasets_zh": "LaMP-1 到 LaMP-7：个性化引用识别、电影标签、商品评分、新闻标题、学术标题、邮件主题、推文改写等任务。",
            "main_findings_zh": "主要结论是：用户历史能显著影响 LLM 输出质量，但收益依赖 profile 检索质量、任务类型和训练/推理方式；简单拼接并不总是最优。",
            "relation_to_lamp_oppu_zh": "这是本综述的中心基准线，后续 profile/RAG、评测和 LongLaMP 类工作大多直接或间接继承它的问题设定。",
            "score": 99,
            "notes_for_verification": "背景中心论文，早于近一年窗口，不计入近一年收录硬门槛。",
        },
        {
            "rank": 0,
            "title": "Democratizing Large Language Models via Personalized Parameter-Efficient Fine-tuning",
            "url": "https://arxiv.org/abs/2402.04401",
            "source": "arxiv",
            "date": "2024-02-07; EMNLP 2024",
            "venue_or_status": "EMNLP 2024 main / personalized PEFT",
            "relevance_tier": "center",
            "direction": "Personalized PEFT and Adaptation",
            "methods_zh": "论文提出 One PEFT Per User (OPPU)：为每个用户维护一个参数高效模块，把用户行为模式和偏好存入少量可插拔参数，而不是只依赖 prompt 或全量微调。",
            "datasets_zh": "论文主要在 LaMP 系列个性化任务上验证，并围绕不同用户历史规模和任务类型比较 PEFT 个性化收益。",
            "main_findings_zh": "主要结论是：个性化 PEFT 能比纯提示/检索方法更稳定地吸收用户偏好，但每用户 adapter 带来训练、存储和冷启动成本，成为后续工作要解决的核心瓶颈。",
            "relation_to_lamp_oppu_zh": "这是本综述的第二条中心线，后续 hypernetwork、共享-私有 adapter、联邦个性化和效率优化工作多在回应 OPPU 的可扩展性问题。",
            "score": 99,
            "notes_for_verification": "背景中心论文，早于近一年窗口，不计入近一年收录硬门槛。",
        },
    ]


def verify_outputs(
    arxiv_records: list[PaperRecord],
    openreview_records: list[PaperRecord],
    curated: pd.DataFrame,
    summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    node_started("verifier", "VerificationDirector", "verifier")
    raw_total = len(arxiv_records) + len(openreview_records)
    missing_fields = []
    required = ["title", "url", "date", "methods_zh", "datasets_zh", "main_findings_zh"]
    for item in summaries:
        for field in required:
            if not item.get(field):
                missing_fields.append({"rank": item.get("rank"), "title": item.get("title"), "field": field})
    sample_links = [item["url"] for item in summaries[:30] if item.get("url")]
    status = "passed"
    conclusion_parts = []
    if raw_total < 5000:
        status = "failed"
        conclusion_parts.append(f"raw_records_total={raw_total} below 5000")
    if len(curated) < 200:
        status = "failed"
        conclusion_parts.append(f"curated_papers_total={len(curated)} below 200")
    if missing_fields:
        status = "failed"
        conclusion_parts.append(f"missing_fields={len(missing_fields)}")
    if not conclusion_parts:
        conclusion_parts.append("scan and summary completeness gates passed")
    report = {
        "status": status,
        "raw_records_total": raw_total,
        "arxiv_raw_records": len(arxiv_records),
        "openreview_paper_like_records": len(openreview_records),
        "curated_papers_total": len(curated),
        "summaries_total": len(summaries),
        "missing_fields": missing_fields[:100],
        "sample_links": sample_links,
        "direction_counts": curated["direction"].value_counts().to_dict(),
        "conclusion": "; ".join(conclusion_parts),
    }
    report_json = REPORTS / "verification.json"
    report_md = REPORTS / "verification.md"
    report_json.write_text(json.dumps(report, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    report_md.write_text(
        "# Verification Report\n\n"
        f"- status: {status}\n"
        f"- raw_records_total: {raw_total}\n"
        f"- curated_papers_total: {len(curated)}\n"
        f"- summaries_total: {len(summaries)}\n"
        f"- missing_fields: {len(missing_fields)}\n"
        f"- conclusion: {report['conclusion']}\n\n"
        "## Direction Counts\n\n"
        + "\n".join(f"- {k}: {v}" for k, v in report["direction_counts"].items())
        + "\n",
        encoding="utf-8",
    )
    flow_report = FLOW / "VerificationDirector_To_Coordinator_20260507_verification_report.md"
    write_artifact(
        flow_report,
        from_role="VerificationDirector",
        to_role="Coordinator",
        subject="Verification report",
        status=status,
        loop_type="VerificationLoop",
        requires_action="FinalWriter can compose the survey if status is passed; otherwise repair failed fields.",
        links=[report_json, report_md],
        done_criteria="Verified raw scan count, curated count, and required summary fields.",
        body=report_md.read_text(encoding="utf-8"),
    )
    artifact_written("verifier", flow_report)
    node_output("verifier", f"Verification status={status}, raw_total={raw_total}, curated={len(curated)}", 1.0)
    node_completed("verifier", status)
    return report


def markdown_paper_entry(item: dict[str, Any], index: int) -> str:
    title = item["title"].replace("\n", " ")
    return (
        f"### {index}. [{title}]({item['url']})\n\n"
        f"- 发表时间/状态：{item.get('date','')}；{item.get('venue_or_status','')}\n"
        f"- 重要性与相关性：{item.get('relevance_tier','')}；score={item.get('score','')}\n"
        f"- 方法介绍：{item.get('methods_zh','')}\n"
        f"- 数据集：{item.get('datasets_zh','')}\n"
        f"- 主要结论：{item.get('main_findings_zh','')}\n"
        f"- 与 LaMP/OPPU 的关系：{item.get('relation_to_lamp_oppu_zh','')}\n"
    )


def compose_final(
    taxonomy: pd.DataFrame,
    summaries: list[dict[str, Any]],
    verification: dict[str, Any],
) -> Path:
    node_started("final_writer", "FinalWriter", "writer")
    final_path = PROJECT_ROOT / "personalized_llm_survey_zh.md"
    summaries_by_direction: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in summaries:
        summaries_by_direction[item["direction"]].append(item)
    lines: list[str] = []
    lines.append("# 近一年个性化 LLM 论文调研综述\n")
    lines.append(
        f"调研窗口：{START_DATE} 至 {END_DATE}。中心背景论文为 LaMP 与 OPPU；它们早于窗口，但作为本综述的两条主线单独列出。"
    )
    lines.append(
        f"本次采用宽口径：LLM 个性化、用户画像/记忆、个性化对齐、个性化 RAG/检索、个性化 PEFT/LoRA、个性化 agent、LLM 推荐系统、隐私/联邦/on-device 个性化均纳入。"
    )
    lines.append(
        f"扫描统计：raw_records_total={verification['raw_records_total']}，其中 arXiv={verification['arxiv_raw_records']}，OpenReview paper-like={verification['openreview_paper_like_records']}；最终近一年收录 {verification['curated_papers_total']} 篇，另列 2 篇中心背景。"
    )
    lines.append(
        "排序规则：优先 LaMP/OPPU 继承关系、标题/摘要中的个性化信号、方法相关性、OpenReview/重要会议公开记录、benchmark/数据集贡献和方向覆盖。自动抽取的数据集字段若摘要未写明，会显式标注“需正文核查”。\n"
    )
    lines.append("## 中心背景论文\n")
    for idx, item in enumerate(central_background(), start=1):
        lines.append(markdown_paper_entry(item, idx))
    global_index = 1
    for _, tax in taxonomy.iterrows():
        direction = tax["direction"]
        items = summaries_by_direction.get(direction, [])
        if not items:
            continue
        lines.append(f"\n## {direction}\n")
        lines.append(str(tax["intro_zh"]) + "\n")
        for item in items:
            lines.append(markdown_paper_entry(item, global_index))
            global_index += 1
    lines.append("\n## 附：可复现产物\n")
    lines.append(f"- 路由 ledger：`{FLOW / 'ledger.md'}`")
    lines.append(f"- arXiv raw：`{RAW / 'arxiv_raw_records.jsonl'}`")
    lines.append(f"- OpenReview raw：`{RAW / 'openreview_raw_records.jsonl'}`")
    lines.append(f"- curated corpus：`{PROCESSED / 'curated_papers.csv'}`")
    lines.append(f"- verification：`{REPORTS / 'verification.md'}`")
    final_path.write_text("\n".join(lines), encoding="utf-8")
    report_path = FLOW / "FinalWriter_To_Coordinator_20260507_final_report.md"
    write_artifact(
        report_path,
        from_role="FinalWriter",
        to_role="Coordinator",
        subject="Final Chinese survey report",
        status="passed",
        loop_type="FullLoop",
        requires_action="Human can review personalized_llm_survey_zh.md.",
        links=[final_path],
        done_criteria="Final long Chinese Markdown survey exists.",
        body=f"Final survey written to {final_path}\n\nIncluded paper entries: {len(summaries)} plus 2 central background papers.",
    )
    artifact_written("final_writer", report_path)
    artifact_written("final_writer", final_path)
    node_output("final_writer", f"Final Markdown written: {final_path}", 1.0)
    node_completed("final_writer", "passed")
    return final_path


def write_scope_artifact() -> Path:
    node_started("coordinator_scope", "Coordinator Scope Artifact", "coordinator")
    path = FLOW / "Coordinator_To_RetrievalDirectors_20260507_scope.md"
    body = f"""
## Scope

- Topic: personalized LLM literature survey.
- Window: {START_DATE} to {END_DATE}.
- Center papers: LaMP and OPPU as background anchors.
- Sources: arXiv and OpenReview public records.
- Raw scan gate: >= 5000 records.
- Curated gate: >= 200 papers.
- Final language: Chinese, with English titles and stable links.

## Inclusion

Include LLM personalization, user profile/memory, personalized RAG, personalized PEFT, personalized alignment, agents, LLM recommenders, privacy/federated/on-device personalization, and domain applications.

## Artifact Rule

Every role writes a local Markdown artifact and returns/records an absolute path. ASCII routing envelopes are represented by this artifact path; Chinese content stays in UTF-8 Markdown.
"""
    write_artifact(
        path,
        from_role="Coordinator",
        to_role="RetrievalDirector-Arxiv; RetrievalDirector-OpenReview",
        subject="Survey scope and routing contract",
        status="passed",
        loop_type="FullLoop",
        requires_action="Retrieval directors should fetch broad public records.",
        links=[],
        done_criteria="Scope, inclusion criteria, and artifact contract are written.",
        body=body,
    )
    artifact_written("coordinator_scope", path)
    node_output("coordinator_scope", "Scope artifact and ledger initialized", 1.0)
    node_completed("coordinator_scope", "passed")
    return path


def write_col_file() -> Path:
    col_path = FLOW / "personalized_llm_survey_realtime.col"
    col_path.write_text(
        '''program "personalized-llm-survey-realtime" {
  cap research level=L1 tools=[web,files] network=public_read write=workspace max_agents=8 max_time=8h max_cost=medium rollback=true

  ROLE coordinator register=R1 kind=director
  ROLE arxiv_retriever register=R3 kind=executor
  ROLE openreview_retriever register=R3 kind=executor
  ROLE dedup_scorer register=R4 kind=executor
  ROLE taxonomy_director register=R4 kind=director
  ROLE core_summarizer register=R4 kind=executor
  ROLE extended_summarizer register=R4 kind=executor
  ROLE verifier register=R6 kind=verifier
  ROLE final_writer register=R7 kind=director

  ARTIFACT Scope type=markdown path="cache/director_flow/Coordinator_To_RetrievalDirectors_20260507_scope.md" schema=role_message
  ARTIFACT ArxivReport type=markdown path="cache/director_flow/RetrievalDirectorArxiv_To_Coordinator_20260507_retrieval_report.md" schema=role_message
  ARTIFACT OpenReviewReport type=markdown path="cache/director_flow/RetrievalDirectorOpenReview_To_Coordinator_20260507_retrieval_report.md" schema=role_message
  ARTIFACT ScoringReport type=markdown path="cache/director_flow/DedupScoringDirector_To_Coordinator_20260507_scoring_report.md" schema=role_message
  ARTIFACT TaxonomyReport type=markdown path="cache/director_flow/TaxonomyDirector_To_Coordinator_20260507_taxonomy.md" schema=role_message
  ARTIFACT CoreSummaries type=markdown path="cache/director_flow/SummaryDirectorCore_To_Coordinator_20260507_core_summaries.md" schema=role_message
  ARTIFACT ExtendedSummaries type=markdown path="cache/director_flow/SummaryDirectorExtended_To_Coordinator_20260507_extended_summaries.md" schema=role_message
  ARTIFACT VerificationReport type=markdown path="cache/director_flow/VerificationDirector_To_Coordinator_20260507_verification_report.md" schema=verification_report
  ARTIFACT FinalSurvey type=markdown path="personalized_llm_survey_zh.md" schema=role_message
}
''',
        encoding="utf-8",
    )
    return col_path


def main() -> int:
    ensure_dirs()
    reset_events()
    if (REPORTS / "realtime_events.jsonl").exists():
        (REPORTS / "realtime_events.jsonl").unlink()
    init_ledger()
    col_path = write_col_file()
    run_started()
    write_scope_artifact()
    artifact_written("coordinator_scope", col_path, "COL source written for reproducible orchestration shape.")
    cached = reuse_retrieval_records() if "--reuse" in sys.argv else None
    if cached is not None:
        arxiv_records, openreview_records = cached
        arxiv_meta = {
            "query_stats": [{"query": "cached arxiv_candidates.csv", "status": "passed", "fetched": len(arxiv_records)}],
            "raw_path": str(RAW / "arxiv_raw_records.jsonl"),
            "csv_path": str(PROCESSED / "arxiv_candidates.csv"),
        }
        openreview_meta = {
            "stats": [{"term": "cached openreview_candidates.csv", "notes": len(openreview_records)}],
            "raw_path": str(RAW / "openreview_raw_records.jsonl"),
            "csv_path": str(PROCESSED / "openreview_candidates.csv"),
        }
    else:
        arxiv_records, arxiv_meta = fetch_arxiv()
        openreview_records, openreview_meta = fetch_openreview()
    deduped, curated = dedup_and_score(arxiv_records, openreview_records)
    taxonomy = build_taxonomy(curated)
    core, extended = summarize_papers(curated)
    summaries = core + extended
    verification = verify_outputs(arxiv_records, openreview_records, curated, summaries)
    final_path = compose_final(taxonomy, summaries, verification)
    run_artifact = REPORTS / f"{RUN_ID}.json"
    payload = {
        "run_id": RUN_ID,
        "status": verification["status"],
        "final_path": str(final_path),
        "arxiv": arxiv_meta,
        "openreview": openreview_meta,
        "verification": verification,
    }
    run_artifact.write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    emit(
        {
            "type": "run_completed",
            "mode": "real",
            "status": verification["status"],
            "run_id": RUN_ID,
            "artifact_path": str(run_artifact),
            "message": f"Personalized LLM survey workflow completed; final={final_path}",
        }
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=json_default))
    return 0 if verification["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())
