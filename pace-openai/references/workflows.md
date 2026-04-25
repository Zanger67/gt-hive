# PACE Workflows

Use these templates as starting points, then adapt to account and policy context.

Default cluster policy for this skill:

- `Phoenix` by default.
- `ICE` only as backup when needed.

## Generate templates automatically

CPU job template (Phoenix default):

```bash
uv run python scripts/generate_sbatch.py \
  --mode cpu \
  --account gts-<pi_username> \
  --job-name train_cpu \
  --time 04:00:00 \
  --command "python train.py" \
  --out train_cpu.sbatch
```

GPU job template + cost estimate:

```bash
uv run python scripts/generate_sbatch.py \
  --mode gpu \
  --account gts-<pi_username> \
  --gpu-type H100 \
  --gpus 1 \
  --time 04:00:00 \
  --command "python train.py" \
  --estimate-cost \
  --rate-gpu-hour 12.5 \
  --out train_h100.sbatch
```

## Phoenix: submit a basic CPU batch job

1. Log in.

```bash
ssh <gt_username>@<gt-login-host-redacted>
```

2. Check available charge accounts and storage.

```bash
pace-quota
```

3. Create a job script.

```bash
cat > job.sbatch <<'EOF'
#!/bin/bash
#SBATCH -J <job_name>
#SBATCH -A <account_name>
#SBATCH -q inferno
#SBATCH -N 1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=2G
#SBATCH -t 01:00:00
#SBATCH -o Report-%j.out

module purge
module load anaconda3
srun python <script.py>
EOF
```

4. Submit and monitor.

```bash
sbatch job.sbatch
squeue -u <gt_username>
```

## Phoenix: run an interactive session safely

```bash
salloc -A <account_name> -q inferno -N 1 --ntasks-per-node=4 -t 01:00:00
srun hostname
```

Exit to release resources:

```bash
exit
```

## ICE: submit a basic batch job

1. Log in (VPN typically required).

```bash
ssh <gt_username>@<gt-login-host-redacted>
```

2. Create a simple script.

```bash
cat > ice_job.sbatch <<'EOF'
#!/bin/bash
#SBATCH -J <job_name>
#SBATCH -N 1
#SBATCH --ntasks-per-node=4
#SBATCH --mem-per-cpu=2G
#SBATCH -t 01:00:00
#SBATCH -o Report-%j.out

module purge
module load anaconda3
srun python <script.py>
EOF
```

3. Submit and monitor.

```bash
sbatch ice_job.sbatch
squeue -u <gt_username>
```

Note: ICE generally handles partitions and QOS automatically for students/course use.

## GPU request template

Use a conservative template and adjust only needed fields.

```bash
cat > gpu_job.sbatch <<'EOF'
#!/bin/bash
#SBATCH -J <gpu_job>
#SBATCH -A <account_name>
#SBATCH -q inferno
#SBATCH -N 1
#SBATCH --gres=gpu:<GPU_TYPE>:1
#SBATCH --mem-per-gpu=12G
#SBATCH -t 01:00:00
#SBATCH -o Report-%j.out

module purge
module load cuda
srun <gpu_program_or_script>
EOF
```

For Phoenix, common GPU types in docs include `V100`, `RTX_6000`, `A100`, `H100`, `H200`, `L40S`, and `rtx_pro_6000_blackwell`.

## Use local scratch correctly in jobs

- Network scratch path: `~/scratch` (persistent for short-term workflows, cleanup policy applies).
- Job-local scratch path: `${TMPDIR}` (per-job node-local temporary directory).

Template:

```bash
#!/bin/bash
#SBATCH -J <io_job>
#SBATCH -A <account_name>
#SBATCH -q inferno
#SBATCH -N 1
#SBATCH --tmp=200G
#SBATCH -t 02:00:00

cp <input_file> "${TMPDIR}/"
srun <app> "${TMPDIR}/<input_file>" > "${TMPDIR}/result.out"
cp "${TMPDIR}/result.out" ~/scratch/
```

## Transfer data with Globus (preferred for large data)

1. Log into `https://www.globus.org/` using Georgia Tech identity.
2. Choose source and destination collections:
   - `PACE Phoenix`
   - `PACE ICE access`
   - Local personal endpoint (if needed)
3. Start transfer and monitor from Activity.

Use SCP for small transfers or quick command-line operations.

## SCP templates

Local to cluster:

```bash
scp <local_file> <gt_username>@<gt-login-host-redacted>:~/scratch/
```

Cluster to local:

```bash
scp <gt_username>@<gt-login-host-redacted>:~/scratch/<remote_file> <local_destination>/
```

Recursive directory copy:

```bash
scp -r <gt_username>@<gt-login-host-redacted>:~/scratch/<remote_dir> <local_destination>/
```

## Queue troubleshooting checklist

1. Verify current queue state.

```bash
squeue -u <gt_username>
pace-check-queue <partition_or_qos_name>
```

2. Inspect job details.

```bash
sacct -j <job_id> -X
pace-job-summary <job_id>
```

3. On Phoenix, confirm account and available balance.

```bash
pace-quota
```

4. If job is pending, check scheduling reason and resource request realism (walltime, memory, GPU type, QOS).
