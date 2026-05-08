# Code Archive

This folder stores lightweight source-code snapshots related to the 2026-05-07 data-mixing work.

## `v13/`

`v13/` is a lightweight V13 code snapshot for review and handoff. It intentionally excludes large or generated artifacts:

```text
data/
output*/
checkpoints/
ckpts/
models/
wandb/
cache/
logs/
__pycache__/
*.pyc
*.pt / *.pth / *.bin / *.safetensors / *.ckpt
*.jsonl / *.parquet / *.npy / *.npz / *.wandb
```

The snapshot was assembled from the local synced V13 copy:

```text
D:\Codex_Sandbox\Huawei_Hard\remote_v12_work\v13
```

Then the newer save-step/training patch copy was overlaid:

```text
D:\Codex_Sandbox\Huawei_Hard\remote_patch_v13_save_steps
```

During this archive update, live SSH pulls from the shared `/zhdd` servers were intermittently reset during key exchange, so this folder records the latest available local synced code plus the later patch overlay. The runtime/checkpoint paths remain documented in `../training/`.
