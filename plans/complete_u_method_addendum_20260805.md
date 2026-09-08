# Complete-U Method Addendum — 2026-08-05

This addendum records a statistical reanalysis of the frozen 120,960-run archive. No additional ABM simulation was performed.

## Motivation

The earlier repeated balanced-split estimator used independent replication halves to remove own-noise contamination from between-cell quadratic forms. Its point estimate nevertheless depended on the number and realization of sampled splits. The final analysis replaces that approximation with the complete average over every ordered pair of distinct replications.

## Primary estimator

For each factor subset S, let H_S denote the equal-cell projection quadratic form and y_r the vector of cell outcomes at replication index r. The target between-cell quantity is estimated by

B_U(S) = [R(R-1)]^(-1) sum_{r != s} y_r' H_S y_s.

Exact Shapley allocations are computed from the 16 subset values for the four-factor game. Random balanced splits with 20, 50, and 100 repetitions are reported only as incomplete-U convergence diagnostics.

## Bootstrap scope

The distinct-pair block bootstrap resamples replication blocks. When an original block is selected more than once, cross-products between its duplicate copies are excluded. Reported 2.5th–97.5th percentile ranges are descriptive stability summaries. The known-truth toy study compares percentile, BCa, and jackknife-normal procedures and shows that none is uniformly exact across null, small, and non-null components; the manuscript therefore avoids treating the bootstrap ranges as calibrated confidence intervals.

## Extension ratios

For R60/R30 comparisons, benchmark replications 0–29 are resampled once. The matching numerator blocks 0–29 use the same multiplicities, while numerator blocks 30–59 are resampled independently and appended. First-30, all-60, and last-30 numerator definitions are reported as sensitivity analyses.

## Decision rule

The reanalysis is used to assess finite-replication stability of near-zero designs. It does not add a new substantive ABM experiment and does not change the prospective status of the original or revision designs.
