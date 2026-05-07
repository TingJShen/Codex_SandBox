# Artifact Manifest

Generated for the GitHub archive directory:

```text
260507_Data_Mixing
```

## Files

| File | Size bytes | Notes |
| --- | ---: | --- |
| `.gitattributes` | `115` | Ensures scripts/TSV/Markdown stay LF and `*.tiktoken` remains binary. |
| `README.md` | `2993` | Archive overview. |
| `TESTING_WORKFLOW.md` | `7204` | Full workflow and fixes. |
| `CURRENT_PROGRESS_20260507.md` | `2146` | Last successful live progress snapshot. |
| `RESULTS_SUMMARY.md` | `3948` | Compact result summary. |
| `REMOTE_PATHS_AND_RESUME.md` | `6499` | Remote paths, monitor commands, resume commands. |
| `results/eval_result_log_1_5B.md` | `135889` | Full result log copied from local workspace. |
| `scripts/arena_answers_priority_20260507.sh` | `7281` | Arena answer driver. |
| `scripts/arena_judge_priority_20260507.sh` | `8746` | Arena judge driver. |
| `scripts/arena_token_usage.py` | `4501` | Token usage summarizer. |
| `scripts/arena_tolerant_summary.py` | `4500` | Tolerant Arena score summarizer. |
| `manifests/manifest_qwen3_arena_p1_20260507.tsv` | `1342` | Qwen3 P1 Arena model list. |
| `manifests/manifest_v11_arena_p2_20260507.tsv` | `2081` | V11 P2 Arena model list. |
| `support_cache/o200k_base.tiktoken` | `3613922` | Small tiktoken cache file for offline-safe answer post-processing. |
| `support_cache/README.md` | `886` | Cache usage instructions. |
| `snapshots/LAST_SUCCESSFUL_REMOTE_SNAPSHOT.md` | `4559` | Last verified remote process/count snapshot. |
| `ARTIFACT_MANIFEST.md` | `dynamic` | This manifest. |

## Cache Checksum

`support_cache/o200k_base.tiktoken` SHA256:

```text
446a9538cb6c348e3516120d7c08b09f57c36495e2acfffe59a5bf8b0cfb1a2d
```

## Excluded Large Artifacts

The following are intentionally excluded from GitHub:

```text
model checkpoints
merged model directories
Arena model_answer JSONL files
Arena model_judgment JSONL files
OpenCompass prediction dumps
M3Eval per-run raw output directories
```

Their remote source paths are recorded in the markdown documents.
