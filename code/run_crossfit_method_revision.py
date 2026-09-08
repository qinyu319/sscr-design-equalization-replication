"""Repeated-cross-fit and toy-validation revision analysis.

Uses the frozen 120,960-run archive.  It does not run the ABM.
"""

from __future__ import annotations

import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis_outputs"
FIGURES = ROOT / "figures"
DATA = ROOT / "data" / "combined_runs_120960.csv.gz"

FACTORS = ["topology", "message_condition", "inoculation", "seeding_regime"]
OUTCOMES = ["mean_total_shift", "mean_signed_shift", "conversion_rate"]
BENCHMARK = "C-D50"
EXTENDED = {"E-SD", "J-S06-D05", "J-S18-D05"}
FOCUS = ["CS-0", "E-SD", "J-S06-D05", "J-S18-D05"]
SEED = 20260805
N_SPLITS = 100
N_BOOT = 1000
BOOT_SPLITS = 20


def subset_objects(cells: pd.DataFrame, factors=FACTORS):
    subsets = [s for k in range(len(factors) + 1) for s in itertools.combinations(factors, k)]
    indicators, counts = {}, {}
    for subset in subsets:
        if subset:
            code = cells.groupby(list(subset), sort=True, observed=True).ngroup().to_numpy()
        else:
            code = np.zeros(len(cells), dtype=int)
        count = np.bincount(code)
        ind = np.zeros((len(cells), len(count)))
        ind[np.arange(len(cells)), code] = 1.0
        indicators[subset] = ind
        counts[subset] = count.astype(float)
    return subsets, indicators, counts


def shapley_transform(subsets, factors=FACTORS):
    lookup = {s: i for i, s in enumerate(subsets)}
    transform = np.zeros((len(factors), len(subsets)))
    k_total = len(factors)
    for fi, factor in enumerate(factors):
        others = [f for f in factors if f != factor]
        for size in range(k_total):
            weight = math.factorial(size) * math.factorial(k_total - size - 1) / math.factorial(k_total)
            for subset in itertools.combinations(others, size):
                base = tuple(sorted(subset, key=factors.index))
                added = tuple(sorted(subset + (factor,), key=factors.index))
                transform[fi, lookup[added]] += weight
                transform[fi, lookup[base]] -= weight
    return transform


def values_b(mean_a, mean_b, subsets, indicators, counts):
    """Replication-invariant cross-product values; rows are independent estimates."""
    a = np.asarray(mean_a, float)
    b = np.asarray(mean_b, float)
    one = a.ndim == 1
    if one:
        a, b = a[None, :], b[None, :]
    ga, gb = a.mean(1), b.mean(1)
    out = np.zeros((len(a), len(subsets)))
    c = a.shape[1]
    for si, subset in enumerate(subsets[1:], start=1):
        ind, n = indicators[subset], counts[subset]
        ma = (a @ ind) / n
        mb = (b @ ind) / n
        out[:, si] = (((ma - ga[:, None]) * (mb - gb[:, None])) * n).sum(1) / c
    return out[0] if one else out


def values_in_sample_b(cellmean, subsets, indicators, counts):
    return values_b(cellmean, cellmean, subsets, indicators, counts)


def load_arrays():
    data = pd.read_csv(DATA)
    keys = FACTORS + ["replication"]
    arrays, base_cells, reps = {}, None, {}
    for design, frame in data.groupby("design", sort=True):
        frame = frame.sort_values(keys).reset_index(drop=True)
        n_rep = int(frame.groupby(FACTORS, observed=True).size().iloc[0])
        cells = frame[FACTORS].drop_duplicates().reset_index(drop=True)
        if base_cells is None:
            base_cells = cells
        elif not cells.equals(base_cells):
            raise ValueError(f"Cell order differs for {design}")
        arrays[design] = {o: frame[o].to_numpy(float).reshape(144, n_rep) for o in OUTCOMES}
        reps[design] = n_rep
    if len(data) != 120960 or data.duplicated(["design"] + keys).any():
        raise ValueError("Frozen archive integrity failure")
    return data, arrays, base_cells, reps


def balanced_splits(r, n_splits, rng):
    n_a = r // 2
    result = []
    for _ in range(n_splits):
        p = rng.permutation(r)
        result.append((p[:n_a], p[n_a:]))
    return result


def repeated_split_analysis(arrays, reps, subsets, indicators, counts, transform):
    rng = np.random.default_rng(SEED + 101)
    splits = {r: balanced_splits(r, N_SPLITS, rng) for r in sorted(set(reps.values()))}
    records = []
    cache = {}
    for design in sorted(arrays):
        r = reps[design]
        for outcome, arr in arrays[design].items():
            vals = []
            for a_idx, b_idx in splits[r]:
                vals.append(values_b(arr[:, a_idx].mean(1), arr[:, b_idx].mean(1), subsets, indicators, counts))
            vals = np.asarray(vals)
            phi = vals @ transform.T
            cache[(design, outcome)] = (vals, phi)

    for outcome in OUTCOMES:
        b_vals, b_phi = cache[(BENCHMARK, outcome)]
        for design in sorted(arrays):
            vals, phi = cache[(design, outcome)]
            mean_rank = tuple(np.argsort(-phi.mean(0)))
            rank_agree = np.mean([tuple(np.argsort(-row)) == mean_rank for row in phi])
            for fi, factor in enumerate(FACTORS):
                x = phi[:, fi]
                mean_sign = np.sign(x.mean())
                records.append({
                    "design": design, "outcome": outcome, "factor": factor,
                    "replications": reps[design], "splits": N_SPLITS,
                    "mean_B_total": float(vals[:, -1].mean()),
                    "mean_B_factor": float(x.mean()),
                    "split_sd_B_factor": float(x.std(ddof=1)),
                    "split_q025_B_factor": float(np.quantile(x, .025)),
                    "split_q975_B_factor": float(np.quantile(x, .975)),
                    "positive_frequency": float(np.mean(x > 0)),
                    "sign_stability": float(np.mean(np.sign(x) == mean_sign)),
                    "factor_ranking_agreement": float(rank_agree),
                    "q_point": float(x.mean() / b_vals[:, -1].mean()),
                    "rho_point": float(x.mean() / b_phi[:, fi].mean()) if b_phi[:, fi].mean() else np.nan,
                    "tau_point": float(vals[:, -1].mean() / b_vals[:, -1].mean()),
                })
    summary = pd.DataFrame(records)
    summary.to_csv(ANALYSIS / "repeated_split_summary.csv", index=False)

    draw_rows = []
    selected = [BENCHMARK, "CS-0", "E-SD", "J-S06-D05", "J-S18-D05", "PC-M01", "PC-M05"]
    for outcome in OUTCOMES:
        b_vals, _ = cache[(BENCHMARK, outcome)]
        for design in selected:
            vals, phi = cache[(design, outcome)]
            for split_id in range(N_SPLITS):
                for fi, factor in enumerate(FACTORS):
                    draw_rows.append({
                        "design": design, "outcome": outcome, "split": split_id,
                        "factor": factor, "B_total": vals[split_id, -1],
                        "B_factor": phi[split_id, fi],
                        "q": phi[split_id, fi] / b_vals[split_id, -1],
                    })
    pd.DataFrame(draw_rows).to_csv(ANALYSIS / "repeated_split_draws.csv.gz", index=False, compression="gzip")
    return summary, cache


def bootstrap_repeated(arrays, reps, subsets, indicators, counts, transform):
    rng = np.random.default_rng(SEED + 202)
    unique_r = sorted(set(reps.values()))
    # Partition original replication blocks before resampling. Pooling first can
    # put the same original block in A and B and recreate positive noise bias.
    boot_pairs = {}
    for r in unique_r:
        pairs = []
        for pos_a, pos_b in balanced_splits(r, BOOT_SPLITS, rng):
            ia = pos_a[rng.integers(0, len(pos_a), size=(N_BOOT, len(pos_a)))]
            ib = pos_b[rng.integers(0, len(pos_b), size=(N_BOOT, len(pos_b)))]
            pairs.append((ia, ib))
        boot_pairs[r] = pairs
    cache = {}
    for design in sorted(arrays):
        r = reps[design]
        for outcome, arr in arrays[design].items():
            val_sum = np.zeros((N_BOOT, len(subsets)))
            for ia, ib in boot_pairs[r]:
                ma = arr[:, ia].mean(2).T
                mb = arr[:, ib].mean(2).T
                val_sum += values_b(ma, mb, subsets, indicators, counts)
            vals = val_sum / BOOT_SPLITS
            cache[(design, outcome)] = (vals, vals @ transform.T)

    point = pd.read_csv(ANALYSIS / "repeated_split_summary.csv")
    rows = []
    for outcome in OUTCOMES:
        base_vals, base_phi = cache[(BENCHMARK, outcome)]
        for design in sorted(arrays):
            vals, phi = cache[(design, outcome)]
            for fi, factor in enumerate(FACTORS):
                p = point[(point.design == design) & (point.outcome == outcome) & (point.factor == factor)].iloc[0]
                metrics = {
                    "B_total": (p.mean_B_total, vals[:, -1]),
                    "B_factor": (p.mean_B_factor, phi[:, fi]),
                    "q": (p.q_point, phi[:, fi] / base_vals[:, -1]),
                    "rho": (p.rho_point, phi[:, fi] / base_phi[:, fi]),
                    "tau": (p.tau_point, vals[:, -1] / base_vals[:, -1]),
                }
                for metric, (estimate, draws) in metrics.items():
                    lo, med, hi = np.nanquantile(draws, [.025, .5, .975])
                    rows.append({
                        "design": design, "outcome": outcome, "factor": factor,
                        "metric": metric, "point": estimate, "lo95": lo,
                        "median": med, "hi95": hi,
                        "replications_design": reps[design],
                        "replications_benchmark": reps[BENCHMARK],
                        "point_splits": N_SPLITS, "bootstrap_draws": N_BOOT,
                        "splits_per_bootstrap": BOOT_SPLITS,
                        "denominator": "C-D50 repeated-cross-fit B at native R=30",
                    })
    result = pd.DataFrame(rows)
    result.to_csv(ANALYSIS / "repeated_crossfit_intervals.csv", index=False)
    return result


def convergence_existing(arrays, subsets, indicators, counts, transform):
    rng = np.random.default_rng(SEED + 404)
    rows = []
    for n in [10, 15, 20, 25, 30]:
        splits = balanced_splits(n, N_SPLITS, rng)
        vals_by_design = {}
        for design in [BENCHMARK] + FOCUS:
            arr = arrays[design]["mean_total_shift"][:, :n]
            phi_rows, total_rows = [], []
            for ia, ib in splits:
                v = values_b(arr[:, ia].mean(1), arr[:, ib].mean(1), subsets, indicators, counts)
                phi_rows.append(v @ transform.T)
                total_rows.append(v[-1])
            vals_by_design[design] = (np.asarray(total_rows), np.asarray(phi_rows))
        base_total = vals_by_design[BENCHMARK][0]
        for design in FOCUS:
            q = vals_by_design[design][1][:, FACTORS.index("seeding_regime")] / base_total
            rows.append({
                "design": design, "replications": n, "point": q.mean(),
                "split_sd": q.std(ddof=1), "lo_split": np.quantile(q, .025),
                "hi_split": np.quantile(q, .975), "splits": N_SPLITS,
            })
    frame = pd.DataFrame(rows)
    frame.to_csv(ANALYSIS / "repeated_split_replication_convergence.csv", index=False)
    make_convergence_figure(frame)
    return frame


def make_convergence_figure(frame):
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8), gridspec_kw={"width_ratios": [1, 1.35]})
    cs = frame[frame.design == "CS-0"].sort_values("replications")
    axes[0].plot(cs.replications, cs.point, marker="o", color="#d55e00")
    axes[0].fill_between(cs.replications, cs.lo_split, cs.hi_split, color="#d55e00", alpha=.18)
    axes[0].set_title("A. CS-0 reference")
    for design, d in frame[frame.design != "CS-0"].groupby("design", sort=False):
        d = d.sort_values("replications")
        axes[1].plot(d.replications, d.point, marker="o", label=design)
        axes[1].fill_between(d.replications, d.lo_split, d.hi_split, alpha=.12)
    axes[1].axhline(0, color="black", lw=.8)
    axes[1].set_title("B. Near-zero designs (local scale)")
    axes[1].legend(frameon=False, fontsize=8)
    for ax in axes:
        ax.set_xlabel("Replications per cell")
        ax.grid(axis="y", alpha=.2)
    axes[0].set_ylabel("Repeated-cross-fit seeding q")
    fig.suptitle("Replication-prefix convergence under 100 balanced splits", y=1.02, fontsize=11, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure9_repeated_split_convergence_two_panel.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def extension_widths(arrays, subsets, indicators, counts, transform):
    rng = np.random.default_rng(SEED + 505)
    rows = []
    bench = arrays[BENCHMARK]["mean_total_shift"]
    for n in [30, 40, 50, 60]:
        b = 500
        def make_pairs(r):
            pairs = []
            for pa, pb in balanced_splits(r, 20, rng):
                ia = pa[rng.integers(0, len(pa), size=(b, len(pa)))]
                ib = pb[rng.integers(0, len(pb), size=(b, len(pb)))]
                pairs.append((ia, ib))
            return pairs
        pairs_d = make_pairs(n)
        pairs_b = make_pairs(30)

        def boot_vals(arr, pairs):
            acc = np.zeros((b, len(subsets)))
            for ia, ib in pairs:
                ma = arr[:, ia].mean(2).T
                mb = arr[:, ib].mean(2).T
                acc += values_b(ma, mb, subsets, indicators, counts)
            v = acc / len(pairs)
            return v, v @ transform.T

        bv, _ = boot_vals(bench, pairs_b)
        for design in sorted(EXTENDED):
            arr = arrays[design]["mean_total_shift"][:, :n]
            dv, dp = boot_vals(arr, pairs_d)
            q = dp[:, FACTORS.index("seeding_regime")] / bv[:, -1]
            lo, med, hi = np.quantile(q, [.025, .5, .975])
            rows.append({
                "design": design, "replications": n, "lo95": lo, "median": med,
                "hi95": hi, "interval_width": hi - lo, "bootstrap_draws": b,
                "splits_per_draw": 20, "denominator": "C-D50 B at native R=30",
            })
    frame = pd.DataFrame(rows)
    frame.to_csv(ANALYSIS / "extension_interval_widths.csv", index=False)
    return frame


def toy_cells():
    rows = list(itertools.product([-1., 1.], repeat=4))
    return pd.DataFrame(rows, columns=["A", "B", "C", "D"])


def toy_validation():
    rng = np.random.default_rng(SEED + 303)
    factors = ["A", "B", "C", "D"]
    cells = toy_cells()
    subsets, indicators, counts = subset_objects(cells, factors)
    transform = shapley_transform(subsets, factors)
    a, b, c, d = [cells[x].to_numpy() for x in factors]
    mu = .80 * a + .50 * b + .60 * a * b + .30 * c
    true_values = values_in_sample_b(mu, subsets, indicators, counts)
    true_phi = true_values @ transform.T
    settings = []
    outer, n_boot = 500, 199
    for noise in ["homoskedastic", "heteroskedastic"]:
        sigma = np.ones(16) if noise == "homoskedastic" else .60 + .60 * (a == 1) + .40 * (b == 1)
        for r in [10, 15, 30, 60]:
            estimates_is = np.empty((outer, 4))
            estimates_cf = np.empty((outer, 4))
            cover_is = np.zeros((outer, 4), bool)
            cover_cf = np.zeros((outer, 4), bool)
            for m in range(outer):
                y = mu[:, None] + sigma[:, None] * rng.normal(size=(16, r))
                vi = values_in_sample_b(y.mean(1), subsets, indicators, counts)
                estimates_is[m] = vi @ transform.T
                cf_acc = np.zeros(len(subsets))
                for ia, ib in balanced_splits(r, 20, rng):
                    cf_acc += values_b(y[:, ia].mean(1), y[:, ib].mean(1), subsets, indicators, counts)
                estimates_cf[m] = (cf_acc / 20) @ transform.T

                idx = rng.integers(0, r, size=(n_boot, 16, r))
                sample = np.take_along_axis(y[None, :, :], idx, axis=2)
                cm = sample.mean(2)
                phi_i = values_in_sample_b(cm, subsets, indicators, counts) @ transform.T
                # Partition original replications before independent within-half
                # resampling so the halves do not share an original noise block.
                na = r // 2
                ma = np.empty((n_boot, 16)); mb = np.empty((n_boot, 16))
                for z in range(n_boot):
                    p = rng.permutation(r)
                    pa, pb = p[:na], p[na:]
                    ia = pa[rng.integers(0, len(pa), size=(16, len(pa)))]
                    ib = pb[rng.integers(0, len(pb), size=(16, len(pb)))]
                    ma[z] = np.take_along_axis(y, ia, axis=1).mean(1)
                    mb[z] = np.take_along_axis(y, ib, axis=1).mean(1)
                phi_c = values_b(ma, mb, subsets, indicators, counts) @ transform.T
                lo_i, hi_i = np.quantile(phi_i, [.025, .975], axis=0)
                lo_c, hi_c = np.quantile(phi_c, [.025, .975], axis=0)
                cover_is[m] = (lo_i <= true_phi) & (true_phi <= hi_i)
                cover_cf[m] = (lo_c <= true_phi) & (true_phi <= hi_c)

            for fi, factor in enumerate(factors):
                for estimator, est, coverage in [
                    ("in-sample", estimates_is[:, fi], cover_is[:, fi]),
                    ("repeated-cross-fit", estimates_cf[:, fi], cover_cf[:, fi]),
                ]:
                    settings.append({
                        "noise": noise, "R": r, "factor": factor, "estimator": estimator,
                        "true_B_allocation": true_phi[fi], "mean_estimate": est.mean(),
                        "bias": est.mean() - true_phi[fi], "rmse": np.sqrt(np.mean((est - true_phi[fi]) ** 2)),
                        "coverage_95": coverage.mean(), "negative_probability": np.mean(est < 0),
                        "outer_datasets": outer, "bootstrap_draws": n_boot,
                    })
    frame = pd.DataFrame(settings)
    frame.to_csv(ANALYSIS / "toy_crossfit_validation.csv", index=False)
    truth = pd.DataFrame({"factor": factors, "true_B_allocation": true_phi})
    truth.to_csv(ANALYSIS / "toy_true_shapley.csv", index=False)
    return frame, truth


def audit_interval_consistency(intervals):
    use = intervals[(intervals.outcome == "mean_total_shift") &
                    (intervals.design.isin(sorted(EXTENDED))) &
                    (intervals.factor == "seeding_regime") &
                    (intervals.metric.isin(["B_factor", "q", "tau"]))].copy()
    use["point_inside_interval"] = (use.point >= use.lo95) & (use.point <= use.hi95)
    use["interval_width"] = use.hi95 - use.lo95
    use.to_csv(ANALYSIS / "interval_source_audit.csv", index=False)
    return use


def main():
    data, arrays, cells, reps = load_arrays()
    subsets, indicators, counts = subset_objects(cells)
    transform = shapley_transform(subsets)
    repeated, _ = repeated_split_analysis(arrays, reps, subsets, indicators, counts, transform)
    intervals = bootstrap_repeated(arrays, reps, subsets, indicators, counts, transform)
    convergence_existing(arrays, subsets, indicators, counts, transform)
    widths = extension_widths(arrays, subsets, indicators, counts, transform)
    toy, truth = toy_validation()
    audit = audit_interval_consistency(intervals)
    summary = {
        "archive_rows": int(len(data)), "abm_runs_added": 0,
        "repeated_splits": N_SPLITS, "bootstrap_draws": N_BOOT,
        "splits_per_bootstrap": BOOT_SPLITS,
        "toy_outer_datasets_per_setting": 500,
        "toy_bootstrap_draws": 199,
        "all_primary_points_inside_own_intervals": bool(audit.point_inside_interval.all()),
        "outputs": [
            "repeated_split_summary.csv", "repeated_crossfit_intervals.csv",
            "repeated_split_replication_convergence.csv", "extension_interval_widths.csv",
            "toy_crossfit_validation.csv", "interval_source_audit.csv",
        ],
    }
    (ANALYSIS / "crossfit_method_revision_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
