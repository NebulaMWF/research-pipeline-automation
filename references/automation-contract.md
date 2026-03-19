# Automation Contract

The repository should converge on these automation components.

## Data Acquisition

- detached execution
- resumable downloads or stable local staging
- completion checks by expected size, checksum, or explicit status marker
- status file with progress

## Preprocess

- explicit `raw -> processed` scripts
- deterministic split generation
- metadata files for every processed dataset
- counts and provenance per split

For variable-length sequence tasks, preprocessing may be insufficient by itself. Add a separate training-index stage when needed:

- split-level length index files
- token-length or frame-length caches
- any lightweight metadata required for dynamic batching

## Experiment Orchestrator

- generated configs per job
- stable run directory per job
- skip completed jobs
- skip jobs with missing prerequisites
- write suite state continuously

If a training stage depends on generated indices or caches, the orchestrator must:

- detect whether those indices exist
- build them before launch when missing
- avoid rebuilding them every run when they are already valid

## Watchdog

- separate process from the orchestrator
- detect if the suite process disappeared
- restart the suite against the same output directory
- stop restarting after `suite_final.json` exists

If there is an intermediate index-building phase, watchdog behavior must respect it:

- either monitor the index-build stage separately
- or wait until the required index files exist before relaunching the suite

## Clean Restart Policy

Not every failure should be resumed in-place.

When the run state is inconsistent, automation should prefer a clean restart over indefinite retries.

Use a clean restart when:

- suite state and experiment ledger disagree with active child processes
- multiple stale child processes from the same run remain alive
- watchdog keeps restoring a run that never reaches stable progress
- logs and status files are no longer a reliable representation of the current state

Clean restart behavior:

1. stop suite
2. stop watchdogs and related monitors
3. stop child training processes for that run directory
4. remove the inconsistent run directory and stale logs
5. preserve valid reusable assets:
   - raw downloads
   - processed data
   - precomputed indices / caches
6. relaunch from a fresh output directory

This policy should be explicit in both code and status artifacts.

## Experiment Ledger

Each job row should include:

- `name`
- `run_dir`
- `config_path`
- `command`
- `tags`
- `status`
- `returncode`
- `summary`

## Hardware-Aware Tuning

For each accelerator-backed stage:

- inspect available memory before launch
- prefer lower per-step batch size and higher gradient accumulation
- move CPU-only jobs off the accelerator
- log tuned values into generated configs and ledger tags

For long sequence tasks, prefer dynamic batching by budget over naive fixed sample-count batching:

- `max_frames_per_batch`
- `max_tokens_per_batch`
- `max_timesteps_per_batch`

This is often more important than changing nominal `batch_size`.

## Common Failure Pattern: Alive Process, Idle GPU

Typical symptoms:

- training process exists
- GPU utilization is near zero for extended periods
- CPU utilization is high
- logs show no epoch progress

Typical causes:

- dataset indexing happening lazily inside the training process
- many compressed small files causing heavy decode / IO overhead
- inappropriate fixed sample-count batching for highly variable sequence lengths
- worker-count settings that exceed available shared-memory capacity

Preferred response:

1. confirm the process is still alive
2. distinguish main process from DataLoader workers
3. move indexing into an explicit pre-training stage
4. cache index outputs on disk
5. switch to dynamic batching by budget
6. only after that, revisit GPU-memory tuning

## Common Failure Pattern: DataLoader Shared-Memory Crash

Typical symptoms:

- training starts, then fails inside data loading
- logs mention worker bus error or insufficient shared memory
- increasing worker count makes the failure more likely

Preferred response:

1. reduce `num_workers`
2. retry the same job with the lower worker count
3. record the repaired worker count in generated configs and experiment ledgers
4. if the run directory is already inconsistent, clean-restart from a fresh output directory

Worker-count repair should be considered a first-class self-healing strategy.

Recommended behavior:

- first failure:
  lower workers and retry
- repeated failure or already-tainted run:
  lower workers and clean-restart from a new run directory

## Common Failure Pattern: State Mismatch

Typical symptoms:

- main suite process exists
- one or more training children exist
- GPU is idle or near idle
- ledger says a previous stage already failed or stopped
- repeated restart attempts append new log headers without restoring healthy progress

Preferred response:

1. detect that the state is inconsistent
2. stop everything associated with the broken run
3. preserve valid caches
4. restart from a fresh run directory

## Common Failure Pattern: Tainted Result Files

Typical symptoms:

- `metrics.jsonl` contains duplicate `step` / `epoch` records from multiple attempts
- later records contradict earlier records inside the same run directory
- prediction files continue appending after a failed or partial restart

Preferred response:

1. treat the run directory as tainted
2. do not reuse it for further training
3. preserve reusable upstream assets only:
   - raw data
   - processed data
   - length indices / metadata caches
4. restart from a brand-new output directory so epoch numbering and result files are clean

## Draft Generation

The paper or manuscript draft must consume the ledger and summary tables, not free-form guesses.
