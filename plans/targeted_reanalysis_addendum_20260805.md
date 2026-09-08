# Targeted statistical reanalysis addendum

Status: frozen before inspecting the cross-fitted or convergence results.

This addendum supplements the prospective revision analysis plan. It addresses finite-replication contamination of between-cell sums of squares and does not introduce new experimental factors.

## Data scope

- Use the existing 25 balanced designs and 108,000 run-level outcomes.
- Primary outcomes remain mean total shift, mean signed shift, and conversion rate.
- Primary near-zero designs are E-SD, J-S06-D05, J-S18-D05, and CS-0.
- C-D50 remains the benchmark denominator.

## Noise-corrected cross-fitting

For each design, outcome, and factorial cell, sort runs by the frozen replication index. Split the 30 replications into A={0,…,14} and B={15,…,29}. For every factor subset S, estimate equally weighted conditional cell means separately in A and B.

Define the cross-product value

V_CF(S)=30 Σ_c [m_A,S(c)−g_A][m_B,S(c)−g_B],

where m_h,S(c) is the half-sample conditional mean for the subset group containing cell c and g_h is the corresponding half-sample grand mean. Independent half-sample noise has zero expected cross-product, so V_CF targets the full-30-replication systematic sum-of-squares scale without allocating finite-replication cell-mean noise. V_CF may be negative near the noise floor.

Enumerate all 16 subsets and compute exact Shapley values from V_CF. Report raw cross-fitted Shapley SS, common-denominator contribution, retention, and—only when cross-fitted total systematic SS is positive and separated from zero—the internal Shapley share.

As a secondary predictive check, train subset conditional means in one half, score them in the other half against the held-out grand-mean baseline, swap halves, and average. This deliberately conservative out-of-sample value is not used as the main variance estimator.

## Cross-fitted bootstrap

- Use 1,000 paired draws.
- Resample replication indices independently within A and B, using the same cell-by-replication index arrays for every design.
- Recalculate all subset values, Shapley SS, total cross-fitted systematic SS, benchmark-denominator contributions, and retentions.
- Percentile intervals may cross zero; they will not be truncated.

## Replication-count convergence

Using the first n={10,15,20,25,30} replications, calculate:

- in-sample systematic and Monte Carlo SS;
- split-half cross-fitted systematic SS;
- seeding and message raw Shapley SS;
- common-denominator Shapley contribution;
- factor retention;
- internal shares only when the cross-fitted total is positive.

For each n, split the selected replications into the earliest floor(n/2) and remaining replications. The primary convergence plots cover E-SD, J-S06-D05, J-S18-D05, CS-0, and C-D50.

## Missing intervals from the existing bootstrap

Report 95% intervals for:

- seeding retention at the three calibrated-strength dose anchors;
- message retention at the three strength anchors;
- total systematic retention for all nine joint anchors;
- seeding contribution in PC-M01 and PC-M05;
- E-SD systematic SS, Monte Carlo SS, and Monte Carlo retention.

Positive-control reporting will include Shapley raw SS, the ratio to CS-0, common-denominator contribution relative to C-D50, and paired-bootstrap intervals.

## Conditional additional simulations

Do not add runs before completing the analyses above. Add replications only for near-zero designs that meet at least one of these diagnostics:

1. cross-fitted total systematic SS is not separated from zero;
2. a key raw Shapley SS changes sign across splits or its interval crosses zero;
3. the n=20,25,30 convergence sequence does not settle relative to its uncertainty;
4. the in-sample and cross-fitted common-denominator conclusions differ materially;
5. noise-corrected systematic SS is negative or indistinguishable from zero.

If triggered, extend only the affected designs from 30 to 60 replications first, preserve factor-cell keys and paired random-stream construction, then repeat the same diagnostics. Increase to 100 only if 60 remains inadequate.

## Language constraint

The centered result will be described as “a monotonic spread effect under the evaluated centered mapping,” not as a universal result over every possible dose–schedule mapping.
