# Arxiv retrieval report

- From: RetrievalDirector-Arxiv
- To: Coordinator
- Subject: Arxiv retrieval report
- Status: passed
- LoopType: FullLoop
- Supersedes: none
- RequiresAction: DedupScoringDirector should consume arxiv_candidates.csv.
- ArtifactLinks:
- D:\Codex_Sandbox\260527_Personalized\cache\raw\arxiv_raw_records.jsonl
- D:\Codex_Sandbox\260527_Personalized\cache\processed\arxiv_candidates.csv
- DoneCriteria: Saved 6900 raw arXiv records.

## Query Stats

- `cat:cs.CL AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=3600, api_total=25262
- `cat:cs.AI AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=900, api_total=50913
- `cat:cs.IR AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=700, api_total=4579
- `cat:cs.LG AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=900, api_total=48757
- `all:personalized AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=400, api_total=6293
- `all:personalization AND submittedDate:[202505070000 TO 202605072359]`: passed, fetched=400, api_total=6304
