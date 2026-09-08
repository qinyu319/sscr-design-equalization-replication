# Cross-Fitted Shapley Method Revision Addendum

Timestamp: 2026-08-05 (Asia/Shanghai)

Status: Post-review revision specification. This document was written after the 120,960-run archive was complete and before the repeated-split and toy-validation outputs described below were generated. It is not an original-study preregistration and does not authorize additional ABM runs.

## 1. Scope

This revision uses the frozen 120,960-run archive and low-cost synthetic statistical simulations only. No additional ABM design or replication will be generated. The objectives are to formalize the cross-fitted estimator, quantify split sensitivity, validate finite-sample behavior in a known data-generating process, replace replication-count-dependent reporting with a between-cell estimand, and regenerate all overlapping interval tables from one source.

## 2. Replication-invariant estimand

For C equally weighted factorial cells, let `mu` be the vector of true cell means, `P_S` the equal-cell conditional-mean projection for factor subset S, and `M = I - 11'/C` the centering operator. The primary subset value is

`B(S) = C^(-1) mu' M P_S M mu`.

For the balanced factorial design, this equals the mean squared fitted deviation across cells. Standard Shapley allocations of `B(S)` define the target total factor contributions. Raw and 30-reference sums of squares are retained only as study-specific engineering quantities.

For a balanced split into independent replication sets A and B, the estimator is

`B_CF(S) = C^(-1) m_A' M P_S M m_B`,

symmetrically identical to the cross-product of subset-fitted, grand-mean-centered half-sample cell means. Its exact expectation and variance order will be derived in the supplement. If half-sample errors are cross-independent, `E[B_CF(S)] = B(S)` even with heteroskedastic cells and within-half common-random-number covariance. If the two halves have nonzero cross-covariance, the bias term is `C^(-1) tr(M P_S M Cov(e_B,e_A))`. Unequal cell weights require a weighted projection and weighted centering; the present equal-cell formula targets the balanced archive.

Because Shapley allocation is linear, the expected cross-fitted allocation equals the Shapley allocation of `B(S)` under the same independence condition. Finite-sample nonmonotonicity and negative factor allocations are treated as signed estimation error, not negative importance. A factor is not ranked as positively important when its interval crosses zero. Ratio shares are suppressed when the cross-fitted total is not separated from zero.

## 3. Repeated balanced splits

- Generate 100 deterministic random balanced splits using seed 20260805 + 101.
- For 30-replication designs, each split is 15+15; for the three 60-replication extensions, each split is 30+30.
- The same split index is used across designs with the same replication count and across all outcomes, preserving paired comparisons.
- The repeated-split mean is the primary point estimator.
- Report per design, outcome, and factor: mean allocation, split-to-split SD, 2.5th and 97.5th split quantiles, positive-allocation frequency, agreement of the sign with the repeated-split mean, and exact factor-ranking agreement with the ranking of the repeated-split mean.
- Repeated-split dispersion is a sensitivity analysis, not an independent-sample confidence interval.

## 4. Split-aware bootstrap

- Use 1,000 paired replication-block bootstrap draws with seed 20260805 + 202.
- Each draw resamples replication indices globally across cells, preserving the common-random-number block structure.
- Within each bootstrap draw, average 20 deterministic random balanced splits of the resampled replication positions.
- For comparisons involving a 60-replication extension and the 30-replication C-D50 benchmark, resample each archive at its native replication count and compare replication-invariant `B` quantities; no 30-replication SS rescaling is used.
- Percentile intervals are descriptive. They do not include a formal correction for the data-triggered extension decision or sequential selection.
- All manuscript and supplement point estimates and intervals for repeated-cross-fitted `B`, q, rho, and tau will be exported from this single procedure.

## 5. Toy validation

Use a balanced 2^4 factorial with effects-coded factors A, B, C, and D and known cell mean

`mu = 0.80 A + 0.50 B + 0.60 AB + 0.30 C`,

so D is a true null factor. Evaluate homoskedastic noise (`sigma=1`) and heteroskedastic noise (`sigma=0.60 + 0.60 I[A=1] + 0.40 I[B=1]`) at R = 10, 15, 30, and 60. For each setting use 500 independent datasets. Compare in-sample and repeated-cross-fitted Shapley bias against the exact Shapley allocation of `B(S)`, null-factor negative-allocation probability, and 95% percentile-bootstrap coverage. Bootstrap coverage uses 199 resamples per dataset and random balanced splitting within each resample. The simulation seed is 20260805 + 303.

## 6. Conditional-extension interpretation

No retrospective equivalence margin will be introduced. The paper will use the weaker interpretation:

`The extensions increased precision and did not reveal evidence of a benchmark-relevant seeding contribution.`

It will state explicitly that the extension choice was data-triggered, the intervals are descriptive, no formal sequential-selection correction was applied, and zero-compatible intervals do not establish practical equivalence. Tables will report the actual interval widths at 30, 40, 50, and 60 replications.

## 7. Reporting hierarchy

1. Primary inference: repeated-cross-fitted replication-invariant allocation B, benchmark-denominator q, factor retention rho, and total retention tau.
2. Secondary description: in-sample ANOVA main effects and in-sample Shapley shares, shown only for high-signal designs.
3. Near-zero designs: no in-sample share is presented as a core result; a dedicated noise-corrected table reports B, q, intervals, and split stability.

## 8. Fixed editorial changes

- Replace the claim that all 108,000 runs were prospectively specified with: `a 25-design archive comprising six previously archived designs and 19 prospectively specified revision designs, totaling 108,000 runs`.
- Use `an ordered spread effect under the evaluated centered mapping` throughout.
- Replace generic control-validation language with separate implementation-invariance and constructed structural-survival statements.
- Remove the unsupported secondary held-out prediction-score claim.
- Compress the abstract to no more than 200 words.
- Move the 25-design matrix out of the main manuscript and retain only a design-family summary there.
- Give the exact ER bridging rule, SBM probability formula, and uniform direct-recipient sampling rule.
- Prepare a local anonymous-review replication package and manifest; an external anonymous review URL remains an author upload step.

