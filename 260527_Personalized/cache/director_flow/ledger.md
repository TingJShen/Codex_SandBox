# Personalized LLM Survey Routing Ledger

| Path | From | To | Status | LoopType | Supersedes | Evidence | LedgerState | Decision |
|---|---|---|---|---|---|---|---|---|
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\Coordinator_To_RetrievalDirectors_20260507_scope.md | Coordinator | RetrievalDirector-Arxiv; RetrievalDirector-OpenReview | passed | FullLoop | none | Scope, inclusion criteria, and artifact contract are written. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\DedupScoringDirector_To_Coordinator_20260507_scoring_report.md | DedupScoringDirector | Coordinator | passed | FullLoop | none | Deduped 7199 raw rows into 5902 candidates and selected 280 curated papers. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\TaxonomyDirector_To_Coordinator_20260507_taxonomy.md | TaxonomyDirector | Coordinator | passed | FullLoop | none | Built problem-driven taxonomy from curated corpus. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\SummaryDirectorCore_To_Coordinator_20260507_core_summaries.md | SummaryDirector-Core | Coordinator | passed | FullLoop | none | Wrote 80 core Chinese summary records. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\SummaryDirectorExtended_To_Coordinator_20260507_extended_summaries.md | SummaryDirector-Extended | Coordinator | passed | FullLoop | none | Wrote 200 extended Chinese summary records. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\VerificationDirector_To_Coordinator_20260507_verification_report.md | VerificationDirector | Coordinator | passed | VerificationLoop | none | Verified raw scan count, curated count, and required summary fields. | authoritative_latest | route |
| D:\Codex_Sandbox\260527_Personalized\cache\director_flow\FinalWriter_To_Coordinator_20260507_final_report.md | FinalWriter | Coordinator | passed | FullLoop | none | Final long Chinese Markdown survey exists. | authoritative_latest | route |
