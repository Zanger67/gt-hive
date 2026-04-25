# GT Hive

Georgia Tech PACE HPC skills for AI coding tools. Navigate Phoenix and ICE clusters, compose Slurm job scripts, estimate costs, and find storage and transfer workflows.

## Install

### Claude Code

```bash
claude plugin marketplace add github:glennmatlin/gt-hive
claude plugin install gt-pace
```

### Codex

Clone this repository and link the skill:

```bash
git clone https://github.com/glennmatlin/gt-hive.git
cd gt-hive
ln -sfn "$(pwd)/pace-openai" "$HOME/.codex/skills/pace-openai"
ln -sfn "$(pwd)/docs" "$HOME/.codex/skills/docs"
```

## What's inside

- **`plugins/gt-pace/`** — Claude Code plugin: Slurm scripting, storage navigation, GPU resource selection, troubleshooting, templates.
- **`pace-openai/`** — Codex skill: public-safe PACE research navigation.
- **`docs/PACE Documentation/`** — PACE documentation references.

## Using the plugin

From Claude Code:

- `/gt-pace:hpc` — interactive router for cluster tasks.

The skill auto-loads when your prompt mentions PACE, Phoenix, ICE, Slurm, sbatch, or HPC.

## Issues and contributions

File issues at https://github.com/glennmatlin/gt-hive/issues.

## License

MIT — see [LICENSE](LICENSE).
