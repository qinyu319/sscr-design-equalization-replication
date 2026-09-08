# Reproducibility Guide

## Scope

This package supports two distinct tasks:

1. **Result reproduction (default):** recompute the manuscript's primary statistics and figures from the frozen run-level archive.
2. **Simulation regeneration (optional):** rerun one or more agent-based-model designs from their YAML configurations.

The default workflow addresses result reproduction. Full simulation regeneration is much more computationally expensive and is not invoked by `run_all.py`.

## Frozen analysis input

`data/combined_runs_120960.csv.gz` contains 120,960 rows. It is restored from the eight tracked binary parts automatically by the initial verification command, using the SHA-256 recorded in `data/archive_parts.json`. The analysis expects:

- 25 designs;
- 144 factorial cells per design;
- 30 replications per cell for 22 designs;
- 60 replications per cell for the three extensions;
- seven named seed columns;
- no duplicate `design × topology × message_condition × inoculation × seeding_regime × replication` keys.

`code/verify_package.py` checks these invariants before analysis.

## Primary workflow

From the repository root:

```bash
python code/verify_package.py
python code/run_all.py --include-descriptive
```

Expected stages:

1. `run_descriptive_analysis.py` first reproduces the original 108,000-run R30 descriptive stage when `--include-descriptive` is supplied. `run_complete_u_validation.py` loads the frozen archive and recomputes the primary complete-U estimates, bootstrap ranges, split diagnostics, extension sensitivity, and toy known-truth validation.
2. `create_complete_u_figures.py` regenerates complete-U-specific figures.
3. `create_figures.py` regenerates the remaining manuscript figures and figure-source tables.

All paths are resolved relative to the repository, so the workflow does not depend on the directory name or operating system.

## Primary outputs

| Output | Interpretation |
|---|---|
| `analysis_outputs/complete_u_point_estimates.csv` | Complete distinct-replication-pair estimates and exact Shapley allocations |
| `analysis_outputs/complete_u_bootstrap_ranges.csv` | 1,000-draw distinct-pair block-bootstrap percentile ranges |
| `analysis_outputs/bootstrap_split_count_sensitivity.csv` | 20-, 50-, and 100-split approximation diagnostics |
| `analysis_outputs/extension_ratio_pairing_sensitivity.csv` | Explicit R60/R30 numerator-denominator resampling sensitivity |
| `analysis_outputs/toy_complete_u_truth.csv` | Analytic factor-allocation truths for the toy validation |
| `analysis_outputs/toy_complete_u_validation.csv` | Bias, RMSE, negative-allocation frequency, and interval-method coverage |
| `analysis_outputs/complete_u_validation_summary.json` | Settings, run counts, output list, and high-level checks |

The scripts overwrite generated files with the same names. Runtime metadata in JSON and binary image metadata may differ between machines even when substantive results are identical.

## Estimator and bootstrap

For factor subset `S`, the primary estimator averages the cross-products over every ordered pair of distinct replications. This is the complete order-two U-statistic and is the exact limit of the earlier random-split approximation.

In bootstrap draws, cross-products between repeated copies of the same original replication block are excluded. The statistic is normalized by the number of remaining distinct-original pairs. Reported percentile ranges describe computational/statistical stability; they are not presented as calibrated confidence intervals.

## Optional simulation regeneration

Run one configuration from the repository root:

```bash
python code/run_revision.py --config configs/cs_0.yaml
```

The configuration controls design parameters, replications, seeds, and output location. Generated `outputs/` are intentionally ignored by Git. To reconstruct the complete archive, first run `python code/prepare_simulation_replay.py`, then execute the 28 commands in `outputs/replay_inputs/commands.txt`. Use `analysis_outputs/configuration_replay_registry.csv` to map each output directory to the published design and replication range. Combine raw outputs with those design identifiers and the schema of the frozen archive. Archive assembly is manual; no byte-identical gzip reconstruction is claimed. Because this can require substantial CPU time and storage, it is not part of the default workflow.

## Validation evidence

`package_validation.json` records the release audit. Detailed table comparisons and representative archived-seed simulation checks are under `validation/`. `manifest_sha256.csv` records hashes for the frozen snapshot. The verification utility reports any missing or changed listed file.

## Environment notes

- Python 3.12 was tested; Python 3.11 is the minimum supported by the pinned dependencies.
- Exact direct dependency versions are pinned in `requirements.txt`.
- `environment.yml` provides an equivalent Conda setup.
- Matplotlib font substitution and raster metadata can cause non-substantive image-byte differences across platforms.
- Numerical tables should agree up to ordinary floating-point precision when the pinned environment is used.
