# Prospective Revision Analysis Plan

Timestamp: 2026-08-05 (Asia/Shanghai)  
Status: frozen before generation of any new revision-design outcomes  
Purpose: prospective revision analysis plan; this is not a preregistration of the original study.

## 1. Revised contribution and terminology

The revision treats design equalization as an audit and reporting protocol, not a new variance estimator. The primary concept is **assigned-intensity dependence**: the allocation attributed to a nominal factor depends on researcher-assigned intensities carried by its levels, although the factor label may invite a structural interpretation. “Intensity-bundled factor” and “design-induced intensity dependence” are acceptable secondary terms. “Artifact” will be avoided except when discussing prior wording.

The AI-persuasion ABM is a worked methodological example and assumption-auditing demonstration. No result will be framed as an estimate of real-world platform persuasion, disclosure effectiveness, inoculation effectiveness, or the general importance of network topology.

## 2. Research questions

- RQ1: Do factor allocations change when assigned-dose spread varies while mean assigned dose is fixed?
- RQ2: Does diagnosed assigned-intensity dependence persist across alternative dose and message-strength equalization anchors?
- RQ3: Can the audit preserve a timing effect in a model variant where temporal placement affects final outcomes?

## 3. Frozen factors, outcomes, and randomization

All confirmatory revision designs cross four topologies (BA, ER, WS, SBM), four message conditions (high-quality AI, low-quality AI, labeled AI, human-equivalent), three inoculation strategies (none, random, hub), three seeding-regime labels (single-shot, burst, continuous), and 30 replications: 144 cells and 4,320 runs per design.

Primary outcomes are mean total shift, mean signed shift, and conversion rate. These are the three primary outcomes prespecified in the frozen revision pipeline; the word “preregistered” will not be used.

All revision designs use the same factor-cell-by-replication keys and the seven seed streams archived in `paired_seed_manifest.csv`. New designs replay those streams. The existing six-design frozen archive remains immutable and is joined to revision outputs only after row-level reconciliation.

## 4. Design families

### 4.1 Original contrast-set series

The existing calibrated-strength designs C-D1, C-D5, C-D10, and C-D50 are retained and renamed the **original contrast-set series**. They do not identify spread alone because mean, maximum, and distribution change together. The primary statement is that allocations change across assigned-dose contrast sets.

### 4.2 Centered-span identification series

Mean assigned dose is fixed at 0.50N. Timing labels remain single-shot, burst, and continuous.

| Design | Single-shot | Burst | Continuous | Center | Spread parameter |
|---|---:|---:|---:|---:|---:|
| CS-0 | 0.50N | 0.50N | 0.50N | 0.50N | 0.00N |
| CS-15 | 0.35N | 0.50N | 0.65N | 0.50N | 0.15N |
| CS-30 | 0.20N | 0.50N | 0.80N | 0.50N | 0.30N |
| CS-45 | 0.05N | 0.50N | 0.95N | 0.50N | 0.45N |
| CS-45-R | 0.95N | 0.50N | 0.05N | 0.50N | 0.45N, reversed mapping |

The spread-specific claim is supported only if seeding allocation rises monotonically from CS-0 through CS-45. CS-45-R is a falsification test: if outcome ordering follows assigned dose after label reversal, the nominal regime factor is carrying dose; any non-reversing component is evidence of timing structure.

### 4.3 Multi-anchor equalization

Dose anchors are 0.05N, 0.50N, and 0.95N. Message-strength anchors are 0.06, 0.14, and 0.18. The full 3 x 3 joint grid will be analyzed. Existing designs are reused where exactly equivalent: C-D1 is calibrated-strength dose anchor 0.05N; CS-0 is calibrated-strength dose anchor 0.50N; E-S is strength anchor 0.14 with the C-D50 dose mapping; E-SD is joint anchor strength 0.14/dose 0.05N. All other anchors receive new design IDs.

Primary anchor displays report seeding retention, message retention, total systematic-variance retention, and Monte Carlo variance retention. Conclusions will be stated across evaluated anchors; anchor-dependent results will be labeled anchor-dependent.

### 4.4 Negative control

NC-INOC is a no-op budget equalization of the already equal 5% random and hub inoculation budgets under the C-D50 benchmark. The transformed configuration must preserve all operative parameters. With paired streams, the maximum absolute run-level outcome difference and every systematic SS difference must be zero within numerical tolerance (1e-12). Failure blocks interpretation of other equalization results.

### 4.5 Positive control

PC-M01 and PC-M05 add opinion reversion toward each agent’s initial opinion after every simulation step:

`o_i(t+1) = (1 - mu) o_i_update(t+1) + mu o_i(0)`, with `mu` equal to 0.01 or 0.05.

They use the CS-0 equal-dose mapping (0.50N for all regimes) and calibrated message strengths. CS-0 is the mu=0 baseline. A surviving or increasing seeding/timing contribution as mu increases is the positive-control criterion. This variant tests whether the protocol can preserve a structural timing effect; it is not part of the substantive benchmark model.

Legacy recursive-cascade outputs will not be used. The manuscript will delete any statement that recursive propagation was tested under the current frozen code unless it is regenerated under the revision version and paired seed manifest.

## 5. Message planned contrasts

Under strength-equalized designs:

1. labeled AI versus the mean of the three unlabeled conditions identifies the explicitly retained disclosure attenuation;
2. contrasts among high-quality AI, low-quality AI, and human-equivalent should be zero within Monte Carlo tolerance because those levels differ only in assigned strength in the implemented model;
3. the calibrated benchmark contrasts 0.06, 0.14, and 0.18 document the removed strength dimension.

The paper will state that equalization preserves only non-intensity distinctions explicitly implemented in the model.

## 6. Variance definitions and primary metrics

For cell c and replication r, `y_cr` is the run-level outcome and `ybar_c` is its replication mean.

- Systematic design SS: `SS_sys = R sum_c (ybar_c - ybar)^2`.
- Monte Carlo SS: `SS_MC = sum_c sum_r (y_cr - ybar_c)^2`.
- Design-internal systematic contribution: `p_k_sys(D) = SS_k(D) / SS_sys(D)`.
- Benchmark-denominator contribution: `q_k_sys(D) = SS_k(D) / SS_sys(D_b)`.
- Factor retention: `rho_k(D) = SS_k(D) / SS_k(D_b)`.
- Total systematic retention: `tau(D) = SS_sys(D) / SS_sys(D_b)`.
- Monte Carlo retention: `omega(D) = SS_MC(D) / SS_MC(D_b)`.

Main effects and all interactions are decomposed only within `SS_sys`; `SS_MC` is reported separately with residual mean square, cell-level within-cell SD, cell-mean Monte Carlo SE, and cross-design retention. Raw SS is compared across designs only because factor cells, replication count, and outcome scales are identical.

## 7. Exact Shapley attribution

Exact Shapley contributions are computed for the four factors over all 16 subsets using 144 equally weighted cell means. For a subset S, the value function is the R-squared of the saturated grouping model on factors in S; thus interactions among included factors enter the value function and interaction variance is allocated across participating factors. Shapley shares sum to 1 over systematic cell-mean variance. Shapley contribution is the primary broad “factor importance” quantity; ANOVA main-effect SS is retained for continuity.

## 8. Uncertainty

The primary uncertainty procedure uses 1,000 within-cell bootstrap draws. Replication indices are shared across paired designs in each draw. The bootstrap recomputes systematic and Monte Carlo SS, main-effect contributions, Shapley contributions, retention metrics, centered-span contrasts, anchor contrasts, and control contrasts. Intervals describe Monte Carlo stability under the simulated design, not population uncertainty.

## 9. Exposure-response robustness

For each design and outcome, exposure is `log(1 + realized cumulative exposure)`. Four predictive models are evaluated:

- M1: regime only;
- M2: cubic spline of log exposure;
- M3: spline plus regime;
- M4: regime-specific spline plus regime.

Cubic B-splines are used as the GAM implementation. Report in-sample R-squared, grouped five-fold cross-validated R-squared, grouped RMSE, M3 minus M2, and M4 minus M3. Folds are defined by replication index so the same paired random-stream block never appears in both training and validation. This is a predictive mechanistic audit, not causal mediation analysis.

## 10. Implementation checks and documentation requirements

Before interpretation, the revision pipeline must verify:

- 4,320 unique keys and 144 balanced cells per design;
- exact paired-key and seven-stream seed coverage;
- exact direct-event reconciliation with configured schedules;
- 50-step arrays and temporal-metric identities;
- systematic plus Monte Carlo SS equals run-level total SS;
- main effects and interactions sum to systematic SS;
- Shapley shares sum to 1;
- no-op control differences are within 1e-12;
- source, configuration, output, and analysis hashes are recorded.

The supplement must include Algorithm A1, the complete noise distribution, direct and second-hand noise rules, recipient replacement/repetition rules, within-step accumulation order, network parameters, schedule rounding, the regenerated one-shot calibration grid, and the status of recursive variants.

## 11. Calibration

The one-shot calibration sweep will be regenerated under the revision runner for candidate strengths 0.03, 0.06, 0.09, 0.12, 0.14, 0.18, 0.24, and 0.30 with 100 seeds, sharing disabled, no inoculation, and single-shot 5% exposure. The table reports exposed-agent total shift, signed shift, conversion, intervals, and whether a value is retained in the factorial designs. The supplement will distinguish historical selection rationale from the prospective revision analysis and disclose all candidate values in the regenerated grid.

## 12. Reporting rule

No fixed 0.2/0.8 retention thresholds are prespecified. Interpretation uses curves, exact values, paired intervals, centered-span ordering, mapping reversal, and controls. The strongest permitted conclusion is conditional on the observed new analyses. If centered-span ordering fails, the paper will state contrast-set dependence rather than spread dependence. If anchor results diverge, the diagnosis will be labeled anchor-dependent. If the positive control fails, the protocol will not be claimed to preserve structural timing effects.

