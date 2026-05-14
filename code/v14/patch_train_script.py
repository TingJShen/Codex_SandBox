#!/usr/bin/env python3
"""Patch dynamic_train_v13_a100_smoke_bsz4_20step.sh to add DOMAIN_BUDGET_SMOOTH."""

path = "/zhdd/home/tjshen/260415_ArcherA100/v14/dynamic_train_v13_a100_smoke_bsz4_20step.sh"

# Restore from backup first to get a clean slate
import shutil
shutil.copy(path + ".bak_20260513", path)

with open(path) as f:
    lines = f.readlines()

# Patch 1: insert DOMAIN_BUDGET_SMOOTH default after LEARN_EMA_DECAY line
for i, line in enumerate(lines):
    if line.strip().startswith("LEARN_EMA_DECAY="):
        lines.insert(i + 1, "DOMAIN_BUDGET_SMOOTH=${DOMAIN_BUDGET_SMOOTH:-0.5}\n")
        print(f"Patch 1: inserted after line {i+1}")
        break

# Patch 2: insert domain_budget_smooth hydra passthrough after learn_ema_decay line
for i, line in enumerate(lines):
    if "trainer.dynamic_sampling.learn_ema_decay" in line:
        new_line = "    +trainer.dynamic_sampling.domain_budget_smooth=${DOMAIN_BUDGET_SMOOTH} \\\n"
        lines.insert(i + 1, new_line)
        print(f"Patch 2: inserted after line {i+1}")
        break

with open(path, "w") as f:
    f.writelines(lines)
print("OK - file saved")
