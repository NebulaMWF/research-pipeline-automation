---
name: research-pipeline-automation
description: Use this skill when the task is to turn a project-spec document for machine learning, multimodal, biosignal, NLP, CV, robotics, or other computational research into a working research pipeline: parse the spec, scaffold repo code, download or organize datasets, preprocess into a unified format, run GPU-aware automated experiments with watchdogs, bounded self-healing error repair, and parameter adjustment, log every setting and result, and produce a paper draft from the final experiment ledger.
---

# Research Pipeline Automation

Use this skill when the input is a research-plan document such as `docs/*.md`, a project spec, a methodology note, or a benchmark plan that describes datasets, baselines, metrics, experiments, and deliverables.

This skill is for execution-oriented research automation. The target output is a working repository that can:

- parse a spec document and extract datasets, systems, metrics, splits, constraints, and experiment matrix
- scaffold or patch code so training, evaluation, logging, and automation match the spec
- download open datasets or organize local datasets into a unified processed format
- auto-run experiments with GPU-aware tuning, watchdogs, resumable orchestration, experiment ledgers, and bounded self-healing retries
- record every experiment setting and result into machine-readable artifacts
- produce a paper draft or manuscript skeleton grounded in the current experiment results

EMG-to-text projects are one concrete example. Do not treat EMG as required. Generalize the workflow to the domain described by the input spec.

## Workflow

1. Read the input spec document first.
   Extract at minimum:
   - datasets and their sources
   - preprocessing contract
   - model families and baselines
   - split protocol
   - evaluation metrics
   - CLI or automation contract
   - experiment matrix and ablations
   - acceptance criteria or definition of done

2. Inspect the repository before writing code.
   Reuse current training, preprocessing, evaluation, and automation code if possible.
   Prefer patching one maintained codepath over creating parallel codepaths.

3. Normalize the implementation around a single contract.
   The repository should converge on:
   - one processed sample format
   - one tokenizer or label encoding standard
   - one results schema
   - one experiment ledger
   - one automation entrypoint

4. Implement or patch the pipeline in this order:
   - dataset acquisition
   - raw-to-processed preprocessing
   - baseline train/eval scripts
   - automation config and orchestrator
   - watchdog/background scripts
   - experiment ledger and summary export
   - manuscript draft generation

5. Make automation resumable.
   Prefer:
   - stable output directories
   - explicit status files
   - detached execution via `screen` or equivalent
   - skipping already completed runs
   - restarting failed orchestrators without repeating finished jobs
   - retrying recoverable jobs after an automatic repair

6. Make training hardware-aware.
   Before launching experiments:
   - inspect visible GPU count and GPU memory
   - choose conservative defaults first
   - reduce per-step batch size before reducing model capacity
   - use gradient accumulation to preserve effective batch
   - move CPU-only stages off the GPU
   - persist tuned values into generated configs and experiment ledgers

7. Record settings and results for every job.
   Every experiment must emit:
   - resolved config path
   - command
   - tags such as dataset, system, stage, fraction, threshold, ablation values
   - status
   - return code
   - summary metrics
   - applied repair actions and retry counts when self-healing is triggered

8. Produce a manuscript draft only after the experiment registry exists.
   The draft may be partial if runs are incomplete, but it must be grounded in actual artifacts rather than guessed results.

## Required Artifacts

Create or maintain these classes of outputs:

- `data/raw/...`
- `data/processed/...`
- `runs/...`
- `results/...`
- `experiment_ledger.json`
- `summary.csv`
- a paper or manuscript draft file

If the repository already has stronger naming conventions, preserve them.

## Tuning Rules

Use these rules in order:

1. Start with the spec defaults.
2. If full-run training OOMs, lower `batch_size`.
3. Add `grad_accum_steps` so the effective batch remains usable.
4. Move text-only or bookkeeping stages to CPU.
5. Reduce sweep breadth before reducing core experiment validity.
6. Persist every tuned value into generated configs and ledger tags.

Do not silently leave impossible experiments in the active queue. Mark them as skipped, reduced, or deferred with a reason.

## Monitoring Rules

Automation should not depend on an interactive shell staying open.

Use detached processes and status files for:
- dataset download monitoring
- preprocess completion
- experiment orchestration
- watchdog recovery

When an orchestrator is already active, watchdogs should monitor rather than spawn duplicates.

## Self-Healing Rules

Automation should attempt bounded self-repair for common operational failures before giving up.

Examples:

- missing processed-data paths caused by incorrect generated config resolution
- CUDA OOM caused by overly aggressive batch size or model memory settings
- long-sequence / high-IO training jobs that appear alive but keep GPU utilization low because indexing or data loading is the bottleneck
- inconsistent orchestration state where ledgers, watchdogs, and child processes disagree about whether a run is still active
- DataLoader worker failures caused by shared-memory pressure, such as bus errors when worker count is too high
- other recoverable launch-time failures where patching the generated config is sufficient

Repair actions should always:

- detect the error signature from logs
- patch the generated config, not the original source spec
- retry the same job
- record the repair action in the experiment ledger

Always use a retry limit.

If the run directory becomes internally inconsistent, do not keep retrying inside the corrupted state. Escalate to a clean restart procedure.

## Long-Sequence Data Rule

For variable-length sequence datasets with large per-sample tensors, do not assume fixed sample-count batching is appropriate.

Prefer this sequence:

1. build explicit length metadata before training
2. use dynamic batching by frame / token / time budget
3. cache split-level length indices on disk
4. if index building is expensive, run it as a separate monitored background stage
5. only launch training after required indices exist

Symptoms of this failure mode:

- training process is alive
- GPU utilization stays near zero for long periods
- CPU or worker processes remain active
- logs do not progress to epochs or metrics

When this happens, treat it as a data-pipeline bottleneck first, not a GPU-capacity problem first.

## Worker / Shared-Memory Rule

For DataLoader-based training, worker count is a stability parameter, not just a speed parameter.

If logs indicate worker crashes, bus errors, or shared-memory exhaustion:

- do not increase worker count further
- reduce `num_workers` in steps
- prefer a stable lower worker count over aggressive parallelism
- consider file-system sharing strategy when supported by the runtime

Typical error signatures:

- `Unexpected bus error encountered in worker`
- `insufficient shared memory (shm)`
- worker killed by signal during data loading

Preferred response order:

1. reduce `num_workers`
2. retry the same job
3. if state became inconsistent, perform a clean restart from a new output directory

When using self-healing automation, this should be treated as a standard repair path:

- detect worker / shm failure from logs
- lower worker count
- regenerate or patch the active config
- retry once in-place if the run directory is still clean
- otherwise clean-restart in a new output directory

## Clean Restart Rule

Use a clean restart when the pipeline state is inconsistent rather than merely slow.

Typical symptoms:

- ledger says a job failed or stopped, but training child processes are still alive
- watchdog is active, but the suite state no longer advances
- old child processes remain after multiple restart attempts
- GPU is idle or erratic while stale workers still exist
- logs contain multiple historical `RUN` headers for the same job and the current state is no longer trustworthy
- metrics or prediction artifacts contain mixed history from multiple restart attempts
- an epoch restarts from `step 1` in the same run directory, causing duplicated or contradictory records

Required clean restart sequence:

1. stop the suite process
2. stop watchdog and auxiliary monitors
3. stop all child training processes tied to the broken run directory
4. delete the inconsistent run directory and its related logs
5. preserve durable artifacts that are still valid:
   - downloaded raw data
   - processed datasets
   - length indices or other reusable caches
6. restart from a fresh output directory so the next run starts from a clean epoch-1 state
7. record that a clean restart was used

Do not delete reusable caches unless they are known to be corrupt.

If result files already contain mixed or contradictory history, treat the whole run directory as tainted and do not append to it further.

## Manuscript Rules

The draft should include:
- title and abstract placeholders grounded in the spec
- datasets section
- preprocessing section
- methods / baselines section
- experiment matrix section
- results tables populated from current summaries when available
- limitations / incomplete runs section when experiments are still running

Use the template in `references/paper-draft-template.md`.

## References

Read these only when needed:

- `references/spec-template.md`
  Use when the input spec is incomplete or when you need to normalize a new project-spec layout.
- `references/automation-contract.md`
  Use when building or patching download, preprocessing, experiment, watchdog, logging, and tuning automation.
- `references/paper-draft-template.md`
  Use when creating the final paper or manuscript draft.
- `references/platform-install.md`
  Use when installing this skill into Codex, Claude Code, or OpenClaw.

## Scripts

Use the bundled scripts instead of rewriting installation steps:

- `scripts/install_skill.py`
  Portable installer with `--platform codex|claude-code|openclaw`.
- `scripts/install_codex.sh`
- `scripts/install_claude_code.sh`
- `scripts/install_openclaw.sh`

These scripts install the skill by symlink by default and can fall back to copy mode.
