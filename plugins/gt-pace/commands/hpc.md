---
name: hpc
description: Interactive guide to Georgia Tech PACE HPC clusters
---

# PACE HPC Interactive Router

You are helping a user with Georgia Tech's PACE HPC clusters. Present the routing
options below using `AskUserQuestion`, then load the appropriate reference files
based on their selection.

## Step 1: Ask What They Need

Use `AskUserQuestion` with these options:

| Option | Label | Description |
|--------|-------|-------------|
| 1 | Submit a job | Get Slurm job script templates and submission guidance |
| 2 | Request GPUs | GPU syntax, types, and cluster-specific availability |
| 3 | Storage / file transfer | Storage tiers, quotas, Globus, SCP, OnDemand |
| 4 | Troubleshoot a job | Diagnose pending, failed, or OOM jobs |
| 5 | Connect to a cluster | SSH, VPN, OnDemand portal links |
| 6 | Explore cluster specs | Node types, partitions, QOS limits |

## Step 2: Cluster Routing

For options 1, 2, 3, and 6, ask which cluster the user is working with (Phoenix
or ICE) using `AskUserQuestion` -- unless context already makes it clear.

**Phoenix indicators:** charge account (`gts-*`), inferno/embers QOS, research context,
PI mention, project storage paths.

**ICE indicators:** course-related work, AI Makerspace, instructional context,
`<gt-login-host-redacted>`.

## Step 3: Load References

Based on the user's selections, read the relevant files from the `gt-pace:hpc` skill
directory. All paths below are relative to `skills/hpc/` within this plugin.

### Submit a job
- Read `assets/templates/gpu-training.sbatch`, `assets/templates/cpu-batch.sbatch`,
  `assets/templates/multi-gpu-training.sbatch`, or `assets/templates/array-job.sbatch`
  depending on the task described
- Read the cluster reference (`references/phoenix-cluster.md` or `references/ice-cluster.md`)
  for resource limits
- Adapt the template: for ICE, remove `-A` and `-q` lines

### Request GPUs
- Read the cluster reference for GPU types and syntax
- Read `references/slurm-reference.md` for advanced GPU directive syntax
- Summarize available GPU types, memory variants, and core-per-GPU ratios

### Storage / file transfer
- Read the cluster reference for storage paths and quotas
- Summarize the three tiers (home, scratch, local) and file transfer options
  (Globus, SCP, OnDemand)

### Troubleshoot a job
- Read `references/troubleshooting.md`
- Ask the user for the job ID or error message, then walk through diagnostics

### Connect to a cluster
- Provide connection info directly (no extra files needed):
  - Phoenix SSH: `ssh <user>@<gt-login-host-redacted>`
  - Phoenix OnDemand: `https://ondemand-phoenix.pace.gatech.edu/`
  - ICE SSH: `ssh <user>@<gt-login-host-redacted>`
  - ICE OnDemand: `https://ondemand-ice.pace.gatech.edu/`
  - Remind: Georgia Tech VPN (GlobalProtect) is required before connecting

### Explore cluster specs
- Read the cluster reference (`references/phoenix-cluster.md` or `references/ice-cluster.md`)
- Summarize node types, partitions, QOS policies, and resource limits

## Key Rules

- Never suggest running compute on login nodes.
- Never use `mpirun`/`mpiexec` with Slurm -- use `srun` instead.
- Phoenix requires a charge account (`-A gts-<pi>`). If unknown, instruct the
  user to run `pace-quota` on the cluster.
- ICE does not require a charge account.
- Scratch is not backed up. Remind users to move important results to project storage.
