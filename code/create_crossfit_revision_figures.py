"""Create figures and a unified extension table for the cross-fit revision."""

from __future__ import annotations

import argparse

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from run_crossfit_method_revision import (
    ANALYSIS, BENCHMARK, EXTENDED, FACTORS, FIGURES, N_SPLITS, SEED,
    balanced_splits, load_arrays, shapley_transform, subset_objects, values_b,
)


def extension_points():
    _, arrays, cells, _ = load_arrays()
    subsets, indicators, counts = subset_objects(cells)
    transform = shapley_transform(subsets)
    rng = np.random.default_rng(SEED + 606)
    bench = arrays[BENCHMARK]["mean_total_shift"]
    rows = []
    for n in [30, 40, 50, 60]:
        sd = balanced_splits(n, N_SPLITS, rng)
        sb = balanced_splits(30, N_SPLITS, rng)
        btot = []
        for ia, ib in sb:
            btot.append(values_b(bench[:, ia].mean(1), bench[:, ib].mean(1), subsets, indicators, counts)[-1])
        btot = np.asarray(btot)
        for design in sorted(EXTENDED):
            arr = arrays[design]["mean_total_shift"][:, :n]
            seed_phi = []
            for ia, ib in sd:
                val = values_b(arr[:, ia].mean(1), arr[:, ib].mean(1), subsets, indicators, counts)
                seed_phi.append((val @ transform.T)[FACTORS.index("seeding_regime")])
            rows.append({
                "design": design, "replications": n,
                "point": float(np.mean(seed_phi) / np.mean(btot)),
                "point_splits": N_SPLITS,
            })
    point = pd.DataFrame(rows)
    width = pd.read_csv(ANALYSIS / "extension_interval_widths.csv")
    table = point.merge(width, on=["design", "replications"], validate="one_to_one")
    # The terminal row is the primary 100-split/1,000-bootstrap estimator used
    # everywhere else; earlier prefixes remain convergence diagnostics.
    primary = pd.read_csv(ANALYSIS / "repeated_crossfit_intervals.csv")
    primary = primary[(primary.outcome == "mean_total_shift") &
                      (primary.factor == "seeding_regime") &
                      (primary.metric == "q") & primary.design.isin(EXTENDED)]
    for x in primary.itertuples(index=False):
        mask = (table.design == x.design) & (table.replications == 60)
        table.loc[mask, ["point", "lo95", "median", "hi95", "interval_width", "bootstrap_draws"]] = [
            x.point, x.lo95, x.median, x.hi95, x.hi95 - x.lo95, x.bootstrap_draws
        ]
    table.to_csv(ANALYSIS / "extension_precision_table.csv", index=False)
    return table


def plot_extension(table):
    fig, ax = plt.subplots(figsize=(7.5, 4.3))
    colors = {"E-SD": "#0072b2", "J-S06-D05": "#d55e00", "J-S18-D05": "#009e73"}
    for design, d in table.groupby("design", sort=False):
        d = d.sort_values("replications")
        ax.plot(d.replications, d.point, marker="o", lw=1.7, color=colors[design], label=design)
        ax.fill_between(d.replications, d.lo95, d.hi95, color=colors[design], alpha=.14)
    ax.axhline(0, color="black", lw=.8)
    ax.set_xlabel("Replications per factorial cell")
    ax.set_ylabel("Repeated-cross-fit seeding q")
    ax.set_title("Conditional extensions increased precision at benchmark-negligible scale")
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "figure11_extension_repeated_crossfit.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_toy():
    toy = pd.read_csv(ANALYSIS / "toy_crossfit_validation.csv")
    nonnull = toy[toy.factor != "D"].copy()
    nonnull["abs_bias"] = nonnull.bias.abs()
    agg = nonnull.groupby(["noise", "R", "estimator"], as_index=False).agg(mean_abs_bias=("abs_bias", "mean"))
    null = toy[toy.factor == "D"].copy()
    fig, axes = plt.subplots(1, 2, figsize=(8.3, 3.8))
    styles = {"in-sample": ("#d55e00", "--"), "repeated-cross-fit": ("#0072b2", "-")}
    for estimator, d in agg[agg.noise == "homoskedastic"].groupby("estimator"):
        color, ls = styles[estimator]
        axes[0].plot(d.R, d.mean_abs_bias, marker="o", color=color, ls=ls, label=estimator)
    axes[0].set_title("A. Mean absolute bias, non-null factors")
    axes[0].set_ylabel("Absolute bias in B allocation")
    axes[0].legend(frameon=False, fontsize=8)
    for estimator, d in null[null.noise == "homoskedastic"].groupby("estimator"):
        color, ls = styles[estimator]
        axes[1].plot(d.R, d.negative_probability, marker="o", color=color, ls=ls, label=estimator)
    axes[1].axhline(.5, color="gray", lw=.8, ls=":")
    axes[1].set_title("B. Negative-allocation probability, null D")
    axes[1].set_ylabel("Probability")
    for ax in axes:
        ax.set_xlabel("Replications per cell")
        ax.grid(axis="y", alpha=.2)
    fig.suptitle("Toy validation: cross-fitting removes the positive null-factor bias", y=1.02, fontsize=11, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure10_toy_crossfit_validation.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_high_signal_allocations():
    metrics = pd.read_csv(ANALYSIS / "factor_metrics.csv")
    designs = ["C-D50", "CS-45", "E-S", "CS-0"]
    factors = ["topology", "message_condition", "inoculation", "seeding_regime"]
    labels = ["Topology", "Message", "Inoculation", "Seeding"]
    fig, axes = plt.subplots(2, 2, figsize=(8.1, 6.1), sharey=True)
    for ax, design in zip(axes.ravel(), designs):
        q = metrics[(metrics.design == design) & (metrics.outcome == "mean_total_shift")]
        main = [q[(q.factor == f) & (q.allocation == "main")].p_sys.iloc[0] for f in factors]
        shp = [q[(q.factor == f) & (q.allocation == "shapley")].p_sys.iloc[0] for f in factors]
        x = np.arange(4); w = .34
        ax.bar(x-w/2, main, w, label="Main effect", color="#56b4e9")
        ax.bar(x+w/2, shp, w, label="Shapley", color="#0072b2")
        ax.set_xticks(x, labels, rotation=18)
        ax.set_title(design, weight="bold")
        ax.grid(axis="y", alpha=.2)
    axes[0,0].set_ylabel("Share of in-sample systematic SS")
    axes[1,0].set_ylabel("Share of in-sample systematic SS")
    axes[0,0].legend(frameon=False, fontsize=8)
    fig.suptitle("Descriptive main-effect and Shapley allocations in high-signal designs", y=.99, weight="bold")
    fig.tight_layout()
    fig.savefig(FIGURES / "figure4_main_vs_shapley_high_signal.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--submitted-only", action="store_true", help="Generate Supplement Figure F1 without legacy extension figures.")
    args = parser.parse_args()
    if not args.submitted_only:
        t = extension_points()
        plot_extension(t)
        plot_toy()
        print(t.to_string(index=False))
    plot_high_signal_allocations()
