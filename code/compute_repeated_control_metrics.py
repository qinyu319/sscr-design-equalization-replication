"""Unified repeated-cross-fit intervals for the positive-control table."""

import numpy as np
import pandas as pd

from run_crossfit_method_revision import (
    ANALYSIS, BENCHMARK, BOOT_SPLITS, FACTORS, N_BOOT, SEED, balanced_splits,
    load_arrays, shapley_transform, subset_objects, values_b,
)


_, arrays, cells, _ = load_arrays()
subsets, indicators, counts = subset_objects(cells)
transform = shapley_transform(subsets)
rng = np.random.default_rng(SEED + 202)
pairs = []
for pa, pb in balanced_splits(30, BOOT_SPLITS, rng):
    ia = pa[rng.integers(0, len(pa), size=(N_BOOT, len(pa)))]
    ib = pb[rng.integers(0, len(pb), size=(N_BOOT, len(pb)))]
    pairs.append((ia, ib))

point = pd.read_csv(ANALYSIS / "repeated_split_summary.csv")
all_ci = pd.read_csv(ANALYSIS / "repeated_crossfit_intervals.csv")
rows = []
for outcome in ["mean_total_shift", "mean_signed_shift", "conversion_rate"]:
    phi_boot = {}
    for design in [BENCHMARK, "CS-0", "PC-M01", "PC-M05"]:
        arr = arrays[design][outcome]
        acc = np.zeros((N_BOOT, len(subsets)))
        for ia, ib in pairs:
            ma = arr[:, ia].mean(2).T
            mb = arr[:, ib].mean(2).T
            acc += values_b(ma, mb, subsets, indicators, counts)
        phi_boot[design] = (acc / BOOT_SPLITS) @ transform.T
    fi = FACTORS.index("seeding_regime")
    cs_point = point[(point.design == "CS-0") & (point.outcome == outcome) &
                     (point.factor == "seeding_regime")].mean_B_factor.iloc[0]
    for design in ["CS-0", "PC-M01", "PC-M05"]:
        p = point[(point.design == design) & (point.outcome == outcome) &
                  (point.factor == "seeding_regime")].iloc[0]
        for metric in ["B_factor", "q"]:
            z = all_ci[(all_ci.design == design) & (all_ci.outcome == outcome) &
                       (all_ci.factor == "seeding_regime") & (all_ci.metric == metric)].iloc[0]
            rows.append({"design": design, "outcome": outcome, "metric": metric,
                         "point": z.point, "lo95": z.lo95, "median": z["median"], "hi95": z.hi95})
        draws = phi_boot[design][:, fi] / phi_boot["CS-0"][:, fi]
        lo, med, hi = np.nanquantile(draws, [.025, .5, .975])
        rows.append({"design": design, "outcome": outcome, "metric": "multiple_CS0",
                     "point": p.mean_B_factor / cs_point, "lo95": lo, "median": med, "hi95": hi})

pd.DataFrame(rows).to_csv(ANALYSIS / "repeated_control_metrics.csv", index=False)
