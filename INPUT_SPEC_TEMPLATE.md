# Project Spec Template

> Purpose: feed this document to `research-pipeline-automation` so it can build a runnable research pipeline, automate experiments, track settings/results, and draft a paper.

---

## 1) Project Goal

- Project name:
- Task type:
  - Example: EMG to text / EEG classification / multimodal retrieval / vision-language QA
- Main objective:
- Primary contribution target:
  - Example: stronger baseline / data-efficient method / transfer robustness / safer decoding
- Final deliverables:
  - Code
  - Automated experiments
  - Result tables
  - Paper draft

---

## 2) Datasets

For each dataset, fill one block:

### Dataset A

- Name:
- Role:
  - Example: main dataset / transfer dataset / robustness dataset
- Source:
  - URL / DOI / repo
- Raw format:
  - Example: HDF5 / CSV / NPZ / WAV + JSON / image folders
- Intended split protocol:
  - Example: cross-subject / cross-session / official split / random split
- Notes:

### Dataset B

- Name:
- Role:
- Source:
- Raw format:
- Intended split protocol:
- Notes:

---

## 3) Unified Processed Data Contract

Define the format that all models must consume.

- Processed root layout:

```text
data/
  raw/
    dataset_a/
    dataset_b/
  processed/
    dataset_a/
      train/
      val/
      test/
      meta.json
    dataset_b/
      train/
      val/
      test/
      meta.json
```

- One processed sample format:
  - File type:
  - Main input tensor name:
  - Main input shape:
  - Target field name:
  - Metadata fields:
  - Optional fields:

Recommended example:

```text
.npz
  x: float32 [T, C]
  y: int32 [L]
  uid: str/int
  sid: str/int
  gt_text: str
  extra: dict
```

---

## 4) Label / Tokenization Standard

- Task output type:
  - Character / subword / word / class index / sequence label
- Vocabulary definition:
- Special tokens:
  - Example: `<blank>`, `<pad>`, `<bos>`, `<eos>`
- Primary metric alignment:
  - Example: CER primary, WER secondary

---

## 5) Split and Evaluation Protocol

- Primary split:
- Secondary split:
- Random seed policy:
- What must be stored in `meta.json`:

Metrics:

- Primary metrics:
- Secondary metrics:
- Safety metrics:
  - Example: over-correction rate
- Efficiency metrics:
  - Example: latency, memory

---

## 6) Systems to Implement

List every required system.

### M1 / Baseline

- Name:
- Architecture:
- Training objective:
- Decoder:
- Expected outputs:

### M2 / Improved System

- Name:
- Architecture or post-processing logic:
- Additional constraints:
- Expected outputs:

### M3 / Advanced System

- Name:
- Architecture:
- Additional training or inference requirements:
- Expected outputs:

Add more systems as needed.

---

## 7) Baselines and Comparisons

- Minimum baselines to reproduce:
- Strong non-neural or classical baselines:
- Strong external-paper baselines:
- Optional comparisons:

For each baseline, specify:

- Name:
- Why included:
- Feasibility:

---

## 8) Experiment Matrix

### Core Table

- E1:
- E2:
- E3:
- E4:

### Scaling

- Training fractions:
  - Example: `1% / 5% / 10%`
- Which systems to compare:

### Robustness

- Drift / domain shift / session shift / subject shift:

### Transfer

- Which source dataset:
- Which target dataset:

### Ablations

- Ablation 1:
- Ablation 2:
- Ablation 3:

---

## 9) Training and Hardware Constraints

- Available GPU(s):
  - Example: `1 x RTX 4090 48GB`
- Whether GPU is shared:
- Whether watchdog / background execution is required:
- Preferred safe defaults:
  - Example: lower batch size first, then gradient accumulation
- Maximum acceptable runtime:

---

## 10) CLI Contract

List the required scripts and arguments.

Example:

```bash
python scripts/train_baseline.py --config configs/baseline.yaml --seed 0 --output_dir runs/m1 --device cuda
python scripts/eval_baseline.py --config configs/baseline.yaml --ckpt runs/m1/best.pt --split test
python scripts/train_advanced.py --config configs/advanced.yaml --seed 0 --output_dir runs/m3 --device cuda
python scripts/eval_all.py --runs runs/ --out results/summary.csv
```

---

## 11) Logging and Artifact Contract

Required files per run:

- `metrics.jsonl`
- `predictions_{split}.jsonl`
- `summary.json` or `summary_test.json`
- `resolved_config.json`

Global required files:

- `experiment_ledger.json`
- `summary.csv`
- watchdog status files
- pipeline status files

For every experiment, record:

- name
- command
- config path
- tags
- status
- return code
- result summary

---

## 12) Automation Requirements

Specify what the automation must do.

- Download datasets automatically:
  - Yes / No
- Preprocess automatically after download:
  - Yes / No
- Launch experiments automatically after preprocess:
  - Yes / No
- Resume incomplete runs automatically:
  - Yes / No
- Use watchdog:
  - Yes / No
- Auto-tune settings from GPU memory:
  - Yes / No
- Generate paper draft automatically:
  - Yes / No

---

## 13) Paper Draft Requirements

- Output file format:
  - Markdown / LaTeX / DOCX
- Required sections:
  - Abstract
  - Introduction
  - Datasets
  - Methods
  - Experiment setup
  - Results
  - Limitations
  - Conclusion
- Whether partial results are acceptable:
  - Yes / No

---

## 14) Definition of Done

Write concrete acceptance criteria.

Examples:

- Baseline runs end-to-end on the main dataset
- Core metrics are produced on test split
- Experiment ledger contains all jobs
- Watchdog can resume interrupted experiments
- Result summary table is exported
- Paper draft is generated from actual experiment outputs

---

## 15) Optional References

- Related papers:
- Official repos:
- External baselines:
- Notes for implementation:

---

## 16) Example Fill-In Stub

```text
Project name: LLM for EMG
Task type: sEMG to text
Main dataset: emg2qwerty
Transfer dataset: Silent Speech EMG
Baseline: CTC
Advanced methods: reranking + frozen LLM adaptor
Primary metric: CER
Scaling points: 1% / 5% / 10%
Hardware: 1 x RTX 4090 48GB
Automation: download -> preprocess -> experiment -> watchdog -> paper draft
```
