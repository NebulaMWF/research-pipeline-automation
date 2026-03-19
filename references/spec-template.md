# Spec Template

Use this as the normalization target when the input spec is incomplete.

Minimum sections:

1. Goal
2. Datasets
3. Methods / baselines
4. Processed data contract
5. Labeling or tokenization
6. Split protocol
7. Metrics
8. CLI or automation contract
9. Logging and artifacts
10. Experiment matrix
11. Definition of done

Minimum decisions to extract:

- dataset names and acquisition sources
- train / val / test policy
- system families and baselines
- output metrics
- mandatory result files
- scaling points and ablations
- final manuscript deliverables

Default assumptions when the spec does not define them:

- one canonical processed format
- one experiment ledger
- one summary table
- one automation entrypoint
