# Submitted manuscript and reproducibility map

This release accompanies **Auditing Assigned-Intensity Dependence in Social Simulation: A Design-Equalization Framework**, prepared for Social Science Computer Review. The mapping was checked against the submitted main manuscript and supplement supplied on 7 September 2026.

## Analysis samples

- The final simulation archive contains 120,960 runs across 25 designs.
- Initial descriptive analyses use only replications 0–29: 108,000 runs. Their in-sample shares and SS-based retention are distinct from complete-U metrics.
- Complete-U analyses use all available replications: R=60 for E-SD, J-S06-D05 and J-S18-D05, and R=30 for the other 22 designs. Ratios use the R=30 C-D50 benchmark.
- Bootstrap percentile ranges describe resampling stability. They are not calibrated confidence intervals.

## Main tables

All paths in the source column are relative to `analysis_outputs/` unless another directory is specified.

| Manuscript item | Source | Reproduction |
|---|---|---|
| Table 1: related diagnostics | Conceptual definitions in the manuscript | No empirical computation |
| Table 2: design families | `design_registry.csv`, `configuration_replay_registry.csv`, run-level archive | `prepare_simulation_replay.py`; sum archive counts by design family |
| Table 3: reporting metrics | Definitions implemented in `code/run_complete_u_validation.py` | Complete-U estimator and benchmark denominator rules |
| Table 4A: high-signal allocations | `manuscript_table_4a.csv`, `factor_metrics.csv`, `complete_u_point_estimates.csv` | `run_descriptive_analysis.py`, `run_complete_u_validation.py`, `export_manuscript_tables.py` |
| Table 4B: near-zero designs | `manuscript_table_4b.csv`, `complete_u_bootstrap_ranges.csv`, `repeated_split_summary.csv` | Complete-U and split scripts; exported table keeps split diagnostics distinct |
| Table 5: controls | `manuscript_table_5_controls.csv`, `integrity_summary.json` | Complete-U control allocations and exact NC-NoOp comparison |

`manuscript_alignment_checks.json` checks selected displayed values in Tables 4A, 4B and 5 using tolerances corresponding to their printed precision. It is not a claim that every sentence in the manuscript was automatically checked.

## Main and supplementary figures

`figures/submitted/` contains the exact eight PNG images embedded in the supplied DOCX files. These are frozen submission artwork. Scripts regenerate computational figures into `figures/`; they never overwrite the submitted artwork. Figure 1 and Figure 3 have a different final presentation from the computational versions, so byte-identical artwork regeneration is not claimed for those two figures.

| Submitted figure | Exact artwork | Computational file and source |
|---|---|---|
| Main Figure 1 | `submitted/figure1.png` | `figure1_audit_protocol.png`; conceptual diagram in `create_figures.py` |
| Main Figure 2 | `submitted/figure2.png` | `figure2_contrast_and_centered_span.png`; `figure_data/figure2_data.csv`, descriptive bootstrap |
| Main Figure 3 | `submitted/figure3.png` | `figure3_anchor_sensitivity.png`; `figure_data/figure3_data.csv`, R30 in-sample `factor_metrics.csv` |
| Main Figure 4 | `submitted/figure4.png` | `figure6_complete_u_toy_validation.png`; `toy_complete_u_validation.csv` |
| Main Figure 5 | `submitted/figure5.png` | `figure5_positive_control.png`; `figure_data/figure5_contribution_data.csv`, `figure5_outcome_data.csv` |
| Supplement Figure F1 | `submitted/figure_F1.png` | `figure4_main_vs_shapley_high_signal.png`; `factor_metrics.csv`; `create_crossfit_revision_figures.py` |
| Supplement Figure I1 | `submitted/figure_I1.png` | `figure6_equal_dose_trajectories.png`; `figure_data/figure6_data.csv` |
| Supplement Figure J1 | `submitted/figure_J1.png` | `figure5_split_count_sensitivity.png`; `bootstrap_split_count_sensitivity.csv` |

Paths in the artwork and computational-file columns are relative to `figures/`. Analytical source tables are in `analysis_outputs/`. Legacy computational figure numbers are retained for script compatibility; manuscript numbering is given by this map.

## Supplementary tables

| Supplement item | Source or implementation |
|---|---|
| A1 and E1: design matrix | `analysis_outputs/design_registry.csv`, `configs/`, `configuration_replay_registry.csv` |
| B1: network parameters | `code/run_revision.py`: network generation |
| C1: schedule rules | `configs/` and `code/run_revision.py`: direct seeding schedule |
| D1: one-shot strength screening | `analysis_outputs/strength_screening_grid_revision.csv`; `code/reproduce_strength_screening.py` |
| E2: initial integrity | `analysis_outputs/integrity_checks.csv`, `integrity_summary.json` |
| E3: extension integrity | `analysis_outputs/targeted_extension_integrity.csv`; final archive verifier |
| G1: message contrasts | `analysis_outputs/planned_message_contrasts.csv`; R30 descriptive script |
| H: exposure-response table | `analysis_outputs/exposure_spline_metrics.csv`; R30 descriptive script |
| J1: split approximation | `analysis_outputs/bootstrap_split_count_sensitivity.csv` |
| J2 and J3: known-truth validation | `analysis_outputs/toy_complete_u_validation.csv`, `toy_complete_u_truth.csv` |
| J4: extension pairing | `analysis_outputs/extension_ratio_pairing_sensitivity.csv` |
| K1, K2 and K3: anchor and control ranges | `analysis_outputs/complete_u_point_estimates.csv`, `complete_u_bootstrap_ranges.csv` |
| L: archive inventory | This release, its README and `manifest_sha256.csv` |

Historical `lo95`/`hi95` column names are retained for compatibility. Interpret their statistical meaning according to the associated analysis stage, not the column name alone. The full 100-split legacy diagnostics can be regenerated with `code/run_crossfit_method_revision.py`. They are not the primary estimator.
