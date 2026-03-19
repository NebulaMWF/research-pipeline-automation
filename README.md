# Research Pipeline Automation

中文说明: [README.zh-CN.md](./README.zh-CN.md)

`research-pipeline-automation` is a general-purpose skill package for turning a research specification document into a runnable repository workflow.

It is designed for execution-oriented research work rather than passive summarization. The intended use case is: you provide a structured project spec, benchmark plan, or methodology document, and the skill helps an agent build or patch the repository so it can download data, preprocess inputs, run experiments, track settings/results, and draft a paper or report.

This package is domain-agnostic. It can be used for:

- machine learning benchmark repos
- multimodal research projects
- biosignal pipelines such as EMG, EEG, ECG, silent speech, or BCI
- NLP, computer vision, speech, and robotics repos
- paper-oriented experimental pipelines that need automation and reproducibility

EMG is only one example domain. The skill is intentionally written to generalize to other computational research projects.

## What The Skill Does

The skill is meant to help an agent do the following:

1. Read a project specification document and extract:
   - datasets
   - preprocessing contracts
   - model families and baselines
   - split protocols
   - metrics
   - experiment matrix
   - deliverables

2. Normalize the repository around one consistent contract:
   - one processed data format
   - one labeling / tokenization standard
   - one experiment ledger
   - one orchestration path

3. Build or patch the implementation:
   - dataset download logic
   - preprocessing scripts
   - baseline train / eval entrypoints
   - generated config workflow
   - experiment automation
   - watchdog processes
   - self-healing retry logic
   - result summaries
   - manuscript draft generation

4. Make the pipeline practical to run:
   - resumable jobs
   - background execution
   - watchdog recovery
   - automatic repair of common execution failures
   - GPU-aware parameter tuning
   - explicit experiment tracking

5. Produce deliverables:
   - run directories
   - summary tables
   - experiment ledgers
   - manuscript skeletons or paper drafts

## What The Skill Does Not Assume

The skill does not assume:

- a specific task type
- a specific framework
- that the project must be EMG-related
- that the repository already has automation
- that the input spec is perfectly written

The skill does assume that the task is structured enough to be turned into an executable research workflow.

## Repository Contents

```text
research-pipeline-automation/
  SKILL.md
  README.md
  README.zh-CN.md
  INPUT_SPEC_TEMPLATE.md
  agents/
    openai.yaml
  references/
    spec-template.md
    automation-contract.md
    paper-draft-template.md
    platform-install.md
  scripts/
    install_skill.py
    install_codex.sh
    install_claude_code.sh
    install_openclaw.sh
```

## File Roles

### `SKILL.md`

This is the canonical agent-facing workflow. It tells the model when to use the skill and how to approach the task.

### `INPUT_SPEC_TEMPLATE.md`

This is the human-facing template for preparing a project-spec document that can be fed into the skill.

### `references/`

These files are supporting materials:

- `spec-template.md`
  Reference structure for normalizing incomplete specs
- `automation-contract.md`
  What the repository automation should converge toward
- `paper-draft-template.md`
  A manuscript structure grounded in experiment outputs
- `platform-install.md`
  Installation notes and target path conventions

### `scripts/`

These are installation helpers for different tools / environments.

## Typical Workflow

The typical usage pattern is:

1. Create or prepare a project-spec markdown document.
2. Point the agent at the document and ask it to use `$research-pipeline-automation`.
3. Let the agent inspect the repository and patch or scaffold the needed code.
4. Let the automation run:
   - download data
   - preprocess data
   - run experiments
   - write ledgers and summaries
   - generate a manuscript draft

A practical prompt looks like:

```text
Use $research-pipeline-automation with docs/project_spec.md.
Build the end-to-end pipeline, set up dataset download and preprocessing, run the experiment matrix with watchdogs, record all settings and results, and draft a paper from the outputs.
```

## Expected Inputs

The skill works best when the input document includes:

- project goal
- datasets and sources
- processed data format requirements
- methods and baselines
- experiment matrix
- metrics
- CLI expectations
- logging / artifact requirements
- acceptance criteria

If you do not already have such a document, start from:

- [INPUT_SPEC_TEMPLATE.md](./INPUT_SPEC_TEMPLATE.md)

## Expected Outputs

The skill is meant to help create or maintain outputs such as:

- `data/raw/...`
- `data/processed/...`
- `runs/...`
- `results/...`
- `experiment_ledger.json`
- `summary.csv`
- `summary.json` and `summary_test.json`
- manuscript drafts such as markdown or LaTeX skeletons

## Automation Features Expected By The Skill

The skill is designed around the idea that research automation should be robust enough to survive long-running experiments.

Expected automation behaviors include:

- resumable dataset downloads
- deterministic preprocessing
- background orchestration
- watchdog-based recovery
- bounded self-healing retries for common operational failures
- GPU-aware tuning
- skipping completed runs
- explicit handling of failed or infeasible jobs
- machine-readable experiment ledgers

## Common Failure Pattern: Low GPU Utilization While Training Is "Alive"

One common failure mode in research repos is:

- the training process still exists
- GPU utilization stays near zero for a long time
- CPU stays busy
- logs do not reach epoch metrics

This often means the bottleneck is not model compute but the data path.

Typical causes:

- many compressed small files
- variable-length long sequences
- training-time lazy indexing
- fixed sample-count batching for highly variable sequence lengths
- worker settings that exceed available shared-memory capacity

A better solution than simply increasing `batch_size` is usually:

1. build split-level length indices first
2. cache those indices on disk
3. use dynamic batching by frame / token budget
4. restart training only after the index stage is complete

This behavior is now part of the intended automation design for this skill.

## Common Failure Pattern: DataLoader Bus Error / Shared Memory Exhaustion

Another practical failure mode is that training fails because DataLoader workers are too aggressive for the machine:

- logs mention worker bus errors
- logs mention insufficient shared memory
- higher `num_workers` causes instability

In that case, the right fix is usually:

1. lower `num_workers`
2. keep the lower worker count in the generated config
3. retry the same job
4. if process state became inconsistent, perform a clean restart in a new run directory

This is also treated as part of the intended self-healing behavior for the skill.

In practice, this means the automation should not keep retrying forever with the same worker count.  
It should actively step worker count down and, when needed, restart from a fresh output directory.

## Common Failure Pattern: State Mismatch After Failed Restarts

Another common failure mode is that the automation state becomes inconsistent:

- the suite process still exists
- watchdogs are still running
- child training processes remain alive
- the experiment ledger says a job already failed or stopped
- GPU utilization is no longer a reliable signal of progress

When this happens, the right response is not endless in-place retries.

The preferred recovery sequence is:

1. stop the suite
2. stop watchdogs and related monitors
3. stop all child training processes for that run directory
4. delete the inconsistent run directory and stale logs
5. keep durable artifacts such as downloaded data, processed data, and reusable indices
6. restart from a new clean output directory

This clean-restart pattern should be treated as part of the automation strategy, not as an ad hoc manual workaround.

## Common Failure Pattern: Tainted Metrics Or Prediction Files

Another case that should trigger a clean restart is when a run directory already contains mixed history, for example:

- duplicate `epoch 1 / step 1` records from multiple attempts
- later `metrics.jsonl` rows contradict earlier rows in the same run
- prediction files keep old partial outputs from failed attempts

In that situation, continuing in the same output directory makes the artifacts unreliable.

Preferred response:

1. mark the run directory as tainted
2. keep reusable upstream assets only
3. delete the old run directory
4. start from a fresh output directory so result files are clean from epoch 1

## Hardware-Aware Operation

The skill is intended to help the agent reason about the available hardware and tune accordingly.

Typical decisions include:

- lowering `batch_size`
- increasing `grad_accum_steps`
- moving text-only jobs to CPU
- reducing sweep breadth when hardware is limited
- preserving valid runs rather than forcing impossible settings
- auto-repairing OOMs or path-resolution failures when a safe config patch is available
- treating persistent low GPU utilization as a possible data-pipeline problem rather than immediately as a compute-capacity problem

The expectation is that every tuned decision should be reflected in generated configs and experiment ledgers.

## Installation

### Codex

```bash
cd path/to/research-pipeline-automation
./scripts/install_codex.sh --force
```

Default target:

- `~/.codex/skills/research-pipeline-automation`

### Claude Code

```bash
./scripts/install_claude_code.sh --force
```

Default target used by the installer:

- `~/.claude/skills/research-pipeline-automation`

### OpenClaw

```bash
./scripts/install_openclaw.sh --force
```

Default target used by the installer:

- `~/.openclaw/skills/research-pipeline-automation`

### Custom Skill Root

If your environment uses a different root, use:

```bash
./scripts/install_skill.py --platform codex --target-root <skill-root> --force
```

Replace `codex` with `claude-code` or `openclaw` as needed.

### Copy vs Symlink

Default install mode is:

- `symlink`

Alternative:

```bash
./scripts/install_skill.py --platform codex --mode copy --force
```

Use `copy` when symlinks are not desired or not supported by the target setup.

## Validation

A minimal installation check is:

```bash
./scripts/install_skill.py --help
```

Then verify that the installed target contains:

- `SKILL.md`
- `agents/openai.yaml`
- `references/`
- `scripts/`

## Recommended Authoring Pattern For Specs

A good spec should be concrete enough that the agent does not need to invent the experiment plan from scratch.

At minimum, define:

- what to build
- what to compare
- what to measure
- what artifacts to save
- what counts as “done”

The more precise the experiment matrix and logging requirements are, the better the automation can be.
