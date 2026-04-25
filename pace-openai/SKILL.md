---
name: pace-openai
description: Public-safe Georgia Tech PACE HPC workflow guidance using filtered local documentation. Use for Phoenix-first research workflows, cost-aware Slurm planning, storage and transfer guidance, and safe command templates that avoid GT-login-only material.
---

# GT PACE Research Navigator

Use this generated public bundle when Codex is installed in `public` mode.

## Operating Defaults

- Assume `Phoenix` when cluster is unspecified.
- Treat `ICE` as backup only unless explicitly requested.
- Prefer research workflows over workshop/training pages.

## Start With Context

1. Assume `Phoenix` if cluster is not given.
2. Identify task type (`job submission`, `storage`, `data transfer`, `OnDemand`, `resource selection`, `cost`, or `troubleshooting`).
3. Identify workload profile (`CPU`, `GPU`, `MPI`, `array`, `interactive debugging`, or `I/O-heavy`).
4. State assumptions explicitly and continue unless account charging or data handling is unclear.

## Route To The Right Source

Start with [references/public/doc-index.md](references/public/doc-index.md), then open only the needed source docs.

Refresh public artifacts before major work (or after docs change):

```bash
uv run python scripts/pace_doc_pipeline.py rebuild --profile public
```

Use the local search helper first:

```bash
uv run python scripts/pace_doc_search.py --profile public list
uv run python scripts/pace_doc_search.py --profile public find "pace-quota qos account" --cluster phoenix
uv run python scripts/pace_doc_search.py --profile public headings --doc "Using Slurm on ICE"
```

Use direct grep when needed:

```bash
rg -n "pace-quota|salloc|sbatch|qos|TMPDIR|scratch" "PACE Documentation"
```

## Generate Job Templates

Generate sbatch templates with the helper script:

```bash
uv run python scripts/generate_sbatch.py \
  --mode cpu \
  --account gts-<pi_username> \
  --command "python train.py" \
  --out train_cpu.sbatch
```

Estimate cost for Phoenix inferno jobs using configurable rates:

```bash
uv run python scripts/generate_sbatch.py \
  --mode gpu \
  --account gts-<pi_username> \
  --gpus 1 \
  --gpu-type H100 \
  --time 04:00:00 \
  --command "python train.py" \
  --estimate-cost \
  --rate-gpu-hour 12.5 \
  --out train_h100.sbatch
```

Use [references/cost-model.md](references/cost-model.md) for model assumptions.

## Build Responses In This Order

1. Give the recommended workflow with minimal steps to execute safely.
2. Provide command or script templates with placeholders (`<gt_username>`, `<account>`, `<pi_username>`).
3. Include cost and queue tradeoffs (`inferno` vs `embers`, partition and resource implications).
4. Add caveats that affect data safety or public-profile limits.
5. Cite the specific local docs used.

Prefer short, testable command sequences over long prose.

## Safety And Quality Rules

- Do not propose heavy compute on login nodes; route users to `salloc` or `sbatch`.
- For Phoenix jobs, include account and QOS handling (`pace-quota`, `-A`, `-q`).
- Treat `inferno` as paid production path and `embers` as preemptible backfill.
- Distinguish network scratch (`~/scratch`) from job-local scratch (`$TMPDIR` and `/scratch/<jobid>`).
- Treat workshop and training pages as low-priority supplemental references.
- Flag stale-sensitive details (node inventory, policy limits, dates) and encourage re-check against authoritative current docs when policy risk is high.

## Reusable References

- [references/public/doc-index.md](references/public/doc-index.md): generated public-safe index.
- [references/workflows.md](references/workflows.md): public-safe tested command patterns and defaults.
- [references/cost-model.md](references/cost-model.md): cost model assumptions and formulas.
- [scripts/pace_doc_search.py](scripts/pace_doc_search.py): local search helper over the public doc view.
- [scripts/generate_sbatch.py](scripts/generate_sbatch.py): generate sbatch templates plus optional cost estimate.
- [scripts/pace_doc_pipeline.py](scripts/pace_doc_pipeline.py): cleanup and indexing pipeline.
