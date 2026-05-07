# Survey scope and routing contract

- From: Coordinator
- To: RetrievalDirector-Arxiv; RetrievalDirector-OpenReview
- Subject: Survey scope and routing contract
- Status: passed
- LoopType: FullLoop
- Supersedes: none
- RequiresAction: Retrieval directors should fetch broad public records.
- ArtifactLinks:
- none
- DoneCriteria: Scope, inclusion criteria, and artifact contract are written.

## Scope

- Topic: personalized LLM literature survey.
- Window: 2025-05-07 to 2026-05-07.
- Center papers: LaMP and OPPU as background anchors.
- Sources: arXiv and OpenReview public records.
- Raw scan gate: >= 5000 records.
- Curated gate: >= 200 papers.
- Final language: Chinese, with English titles and stable links.

## Inclusion

Include LLM personalization, user profile/memory, personalized RAG, personalized PEFT, personalized alignment, agents, LLM recommenders, privacy/federated/on-device personalization, and domain applications.

## Artifact Rule

Every role writes a local Markdown artifact and returns/records an absolute path. ASCII routing envelopes are represented by this artifact path; Chinese content stays in UTF-8 Markdown.
