---
name: hpc
description: >-
  This skill should be used when the user asks about "PACE", "Phoenix cluster",
  "ICE cluster", "Slurm job", "sbatch", "HPC", "GPU training on cluster",
  "cluster storage", "scratch space", "charge account", "inferno", "embers",
  "pace-quota", "squeue", "salloc", "interactive session", "OnDemand",
  "job pending", "job failed", "OOM", or mentions Georgia Tech high-performance
  computing. Provides job scripting, storage navigation, GPU resource selection,
  troubleshooting, and templates for ML training and batch workflows.
---

# Georgia Tech PACE HPC Skill

PACE (Partnership for an Advanced Computing Environment) operates two primary clusters
at Georgia Tech: **Phoenix** (research) and **ICE** (instructional). This skill provides
procedural knowledge for both.

## Cluster Routing

Determine which cluster the user is working with before loading cluster-specific references.

**Phoenix indicators:** charge account (`gts-*`), `-A` flag, inferno/embers QOS, research
context, PI mention, project storage paths (`/storage/home/hcoda1/`).

**ICE indicators:** course-related work, AI Makerspace, no charge account needed,
`<gt-login-host-redacted>`, instructional context.

Once determined, load the appropriate reference:
- **Phoenix:** Read `references/phoenix-cluster.md`
- **ICE:** Read `references/ice-cluster.md`

If the cluster cannot be determined from context, ask the user.

For detailed Slurm syntax beyond the quick reference below, read `references/slurm-reference.md`.
For diagnosing job failures or unexpected behavior, read `references/troubleshooting.md`.

## Charge Account Configuration

Phoenix requires a charge account (`-A gts-<pi>`). To find the user's account:

1. Check if a charge account appears in the conversation or in CLAUDE.md
   (users may add `PACE charge account: gts-xxx` to their project CLAUDE.md)
2. If unknown, instruct the user to run `pace-quota` on the cluster, which lists
   all available charge accounts and their balances

ICE does not require a charge account.

## Core Slurm Quick Reference

| Command | Purpose |
|---------|---------|
| `sbatch script.sbatch` | Submit batch job |
| `salloc -N1 -n4 -t1:00:00` | Interactive session |
| `srun <command>` | Run command within allocation (required for MPI) |
| `squeue -u $USER` | Check job status |
| `scancel <jobid>` | Cancel job |
| `sacct -j <jobid> -X` | Job accounting summary |
| `pace-quota` | Storage usage and charge account balances |
| `pace-check-queue <partition>` | Node availability |
| `pace-why-inqueue <jobid>` | Diagnose pending job |

## Essential SBATCH Directives

```bash
#SBATCH -J <name>                # Job name
#SBATCH -A gts-<pi>             # Charge account (Phoenix only)
#SBATCH -q inferno               # QOS: inferno (paid) or embers (free backfill)
#SBATCH -N 1                     # Nodes
#SBATCH --ntasks-per-node=4      # Tasks (processes) per node
#SBATCH --mem-per-cpu=2G         # Memory per core
#SBATCH -t 0-04:00:00            # Walltime (D-HH:MM:SS)
#SBATCH -o Report-%j.out         # Output (%j = job ID)
#SBATCH --gres=gpu:H100:1        # GPU request
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --mail-user=user@gatech.edu
```

## Module System

```bash
module avail                     # List available software
module avail <name>              # Search for software
module load anaconda3            # Load module
module load cuda                 # Required for GPU/CUDA work
module purge                     # Unload all modules
```

System Python on RHEL9 is 3.9. Load `anaconda3` for conda environments.

## Storage Overview

Both clusters provide three tiers:

| Tier | Purpose | Backed up? | Auto-purge |
|------|---------|-----------|------------|
| Home (`~`) | Config, small files | Yes | No (but quota-limited) |
| Scratch (`~/scratch`) | Active computation data | No | Yes (cluster-specific) |
| Local (`$TMPDIR`) | Per-job fast I/O | No | Deleted at job end |

Phoenix also has **project storage** (`~/p-<pi>-0` or `~/r-<pi>-0`) for long-term data.

Specific paths, quotas, and purge policies differ by cluster. Consult the relevant
cluster reference file.

## File Transfer

- **Globus** (recommended for large transfers): Auto-resumes, fast. Endpoints: `PACE Phoenix`, `PACE ICE access`.
- **SCP** (small transfers): `scp file user@<gt-login-host-redacted>:~/scratch/`
- **OnDemand file manager**: Browser-based upload/download for small files.

## GPU Requests

General syntax: `--gres=gpu:<TYPE>:<COUNT>` or `-G <COUNT> -C <CONSTRAINT>`

Common GPU types across clusters: V100, A100, H100, H200, L40S, RTX6000, RTX Pro Blackwell.

Specific GPU names, memory variants, and default core-per-GPU ratios differ by cluster.
Consult the cluster reference file for exact syntax.

## Job Script Templates

Ready-made templates are available in `assets/templates/`:

- **`gpu-training.sbatch`** - Single-GPU ML training (PyTorch/TensorFlow)
- **`multi-gpu-training.sbatch`** - Multi-GPU distributed training (DDP)
- **`cpu-batch.sbatch`** - CPU-only batch processing
- **`array-job.sbatch`** - Parameter sweep / hyperparameter search

Read and adapt the appropriate template for the user's task. Templates use Phoenix
defaults (charge account, inferno QOS). For ICE, remove the `-A` and `-q` lines and
adjust resource limits per the ICE reference.

## Key Rules

- **Never run compute on login nodes.** PACE kills offending processes.
- **Never use `mpirun`/`mpiexec` with Slurm.** Use `srun` instead.
- **Always use `srun` for compute commands inside job scripts** — except when using a
  launcher (`torchrun`, `deepspeed`) that manages process spawning internally.
- **Array job logs must use `%A_%a`**, not just `%A` (causes all tasks to write one file).
- Scratch is never backed up. Move important results to project storage promptly.
- `$TMPDIR` is per-job local scratch. Use `trap 'cp ${TMPDIR}/* ~/scratch/' TERM EXIT`
  to recover data from preempted or failed jobs.

## Connection

| Cluster | SSH | OnDemand |
|---------|-----|----------|
| Phoenix | `ssh user@<gt-login-host-redacted>` | `https://ondemand-phoenix.pace.gatech.edu/` |
| ICE | `ssh user@<gt-login-host-redacted>` | `https://ondemand-ice.pace.gatech.edu/` |

Georgia Tech VPN (GlobalProtect) is required before connecting.

## Additional Resources

### Reference Files

Load these as needed based on the user's task:

- **`references/phoenix-cluster.md`** - Phoenix node specs, partitions, QOS limits, storage paths, GPU syntax
- **`references/ice-cluster.md`** - ICE node specs, partitions, job limits, storage, course QOS
- **`references/slurm-reference.md`** - Complete Slurm directive reference, GPU syntax, array jobs, MPI
- **`references/troubleshooting.md`** - Diagnosing pending/failed jobs, common errors, gotchas

### Raw Documentation

Full original PACE documentation is available via `../../docs` (a symlink to
`docs/PACE Documentation/` at the repo root) for detailed lookups when reference
files do not cover a specific topic.
