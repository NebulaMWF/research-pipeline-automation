# Manuscript Draft Template

Use this template after experiments have produced at least partial results.

## Title

`[Project title from spec]`

## Abstract

- problem
- datasets
- methods compared
- main result summary from current `summary.csv`
- note incomplete runs if the suite is still running

## 1. Introduction

- task motivation
- why the benchmark matters
- reproducibility scope

## 2. Datasets

- dataset descriptions
- split protocol
- preprocessing contract

## 3. Methods

- baseline methods
- proposed methods
- decoding / reranking / adaptation details

## 4. Experimental Setup

- encoding / tokenizer or label mapping
- metrics
- hardware
- automation and monitoring
- hyperparameter tuning policy

## 5. Results

- core table
- scaling table
- transfer table
- ablation table

Populate tables from:
- `experiment_ledger.json`
- `summary.csv`
- per-run `summary.json` / `summary_test.json`

## 6. Limitations

- failed runs
- skipped runs
- known bottlenecks
- pending experiments

## 7. Conclusion

- short factual conclusion

## Appendix

- commands
- config references
- dataset and run counts
