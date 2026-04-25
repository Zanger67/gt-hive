# gt-pace

Claude Code plugin for Georgia Tech PACE HPC clusters (Phoenix and ICE). Provides Slurm job scripting, storage navigation, GPU resource selection, troubleshooting, and ready-made templates.

## Skill

- **hpc** - Activated automatically when you ask about PACE, Phoenix, ICE, or Slurm jobs.

## Command

- `/gt-pace:hpc` - Interactive router for common HPC tasks (job scripts, storage, GPUs, troubleshooting).

## Auto-update

A SessionStart hook checks for plugin updates at the beginning of each session. Updated plugins take effect on the next session.

## Full documentation

See the [gt-hive README](https://github.com/glennmatlin/gt-hive) for installation, usage, and maintenance details.
