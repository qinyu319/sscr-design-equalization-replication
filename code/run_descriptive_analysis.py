"""Original R30 analysis, adapted only for portable packaged input/output paths."""
from __future__ import annotations

import ast
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, SplineTransformer


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis_outputs"
FIGURES = ROOT / "figures"
ANALYSIS.mkdir(exist_ok=True)
FIGURES.mkdir(exist_ok=True)

FACTORS = ["topology", "message_condition", "inoculation", "seeding_regime"]
OUTCOMES = ["mean_total_shift", "mean_signed_shift", "conversion_rate"]
KEYS = FACTORS + ["replication"]
SEED_COLS = ["master_seed", "network_seed", "initialization_seed", "seeding_seed", "sharing_seed", "noise_seed", "inoculation_seed"]
BENCHMARK = "C-D50"


def registry() -> pd.DataFrame:
    rows = [
        ("mechanism_dose_1_1_1", "C-D1", "original contrast-set", .05, 0, np.nan, np.nan, "baseline", "archive"),
        ("mechanism_dose_1_2_5", "C-D5", "original contrast-set", np.mean([.05,.10,.25]), .20, np.nan, np.nan, "baseline", "archive"),
        ("mechanism_dose_1_3_10", "C-D10", "original contrast-set", np.mean([.05,.15,.50]), .45, np.nan, np.nan, "baseline", "archive"),
        ("mechanism_dose_1_5_50", "C-D50", "original contrast-set", np.mean([.05,.25,2.50]), 2.45, np.nan, np.nan, "baseline", "archive"),
        ("mechanism_strength_equalized", "E-S", "strength equalization", np.mean([.05,.25,2.50]), 2.45, np.nan, .14, "baseline", "archive"),
        ("mechanism_strength_and_dose_equalized", "E-SD", "joint equalization", .05, 0, .05, .14, "baseline", "archive"),
        ("cs_0", "CS-0", "centered span", .50, 0, np.nan, np.nan, "baseline", "new"),
        ("cs_15", "CS-15", "centered span", .50, .30, np.nan, np.nan, "baseline", "new"),
        ("cs_30", "CS-30", "centered span", .50, .60, np.nan, np.nan, "baseline", "new"),
        ("cs_45", "CS-45", "centered span", .50, .90, np.nan, np.nan, "baseline", "new"),
        ("cs_45_r", "CS-45-R", "centered reversal", .50, .90, np.nan, np.nan, "reversed dose mapping", "new"),
        ("dose_anchor_095_calibrated", "D-A95", "dose equalization", .95, 0, .95, np.nan, "baseline", "new"),
        ("strength_anchor_060", "S-A06", "strength equalization", np.mean([.05,.25,2.50]), 2.45, np.nan, .06, "baseline", "new"),
        ("strength_anchor_180", "S-A18", "strength equalization", np.mean([.05,.25,2.50]), 2.45, np.nan, .18, "baseline", "new"),
        ("joint_s060_d005", "J-S06-D05", "joint equalization", .05, 0, .05, .06, "baseline", "new"),
        ("joint_s060_d050", "J-S06-D50", "joint equalization", .50, 0, .50, .06, "baseline", "new"),
        ("joint_s060_d095", "J-S06-D95", "joint equalization", .95, 0, .95, .06, "baseline", "new"),
        ("joint_s140_d050", "J-S14-D50", "joint equalization", .50, 0, .50, .14, "baseline", "new"),
        ("joint_s140_d095", "J-S14-D95", "joint equalization", .95, 0, .95, .14, "baseline", "new"),
        ("joint_s180_d005", "J-S18-D05", "joint equalization", .05, 0, .05, .18, "baseline", "new"),
        ("joint_s180_d050", "J-S18-D50", "joint equalization", .50, 0, .50, .18, "baseline", "new"),
        ("joint_s180_d095", "J-S18-D95", "joint equalization", .95, 0, .95, .18, "baseline", "new"),
        ("nc_inoculation_noop", "NC-NoOp", "negative control", np.mean([.05,.25,2.50]), 2.45, np.nan, np.nan, "inoculation budget no-op", "new"),
        ("pc_memory_010", "PC-M01", "positive control", .50, 0, .50, np.nan, "opinion reversion mu=.01", "new"),
        ("pc_memory_050", "PC-M05", "positive control", .50, 0, .50, np.nan, "opinion reversion mu=.05", "new"),
    ]
    cols = ["source_id","design","family","dose_center","dose_spread","dose_anchor","strength_anchor","structural_variant","source"]
    return pd.DataFrame(rows, columns=cols)


def load_data(reg: pd.DataFrame) -> pd.DataFrame:
    # Preserve the original descriptive-analysis sample: replications 0-29.
    data = pd.read_csv(ROOT / "data" / "combined_runs_120960.csv.gz")
    data = data[data.replication < 30].copy()
    if len(data) != 108000:
        raise ValueError("Initial archive must contain 108000 rows")
    return data


def integrity_checks(data: pd.DataFrame, reg: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows = []
    expected_cells = 4 * 4 * 3 * 3
    manifest = pd.read_csv(ROOT / "data" / "paired_seed_manifest_initial.csv.gz")
    manifest = manifest[KEYS + SEED_COLS]
    for name, d in data.groupby("design", sort=False):
        duplicate_keys = int(d.duplicated(KEYS).sum())
        unique_cells = int(d[FACTORS].drop_duplicates().shape[0])
        reps_min = int(d.groupby(FACTORS).size().min())
        reps_max = int(d.groupby(FACTORS).size().max())
        m = d.merge(manifest, on=KEYS, how="left", suffixes=("", "_expected"), validate="one_to_one")
        seed_mismatch = 0
        for c in SEED_COLS:
            seed_mismatch += int((m[c].astype("Int64") != m[f"{c}_expected"].astype("Int64")).sum())
        direct_reconcile = int((d["total_direct_exposures"] != d["assigned_direct_seed_events"]).sum())
        arrays_bad = 0
        for c in ["direct_exposures_by_step","secondhand_exposures_by_step","total_exposures_by_step","opinion_shift_by_step","cumulative_total_shift_by_step"]:
            arrays_bad += int(sum(len(ast.literal_eval(v)) != 50 for v in d[c]))
        rows.append({
            "design": name, "rows": len(d), "unique_cells": unique_cells,
            "duplicate_keys": duplicate_keys, "replications_min": reps_min,
            "replications_max": reps_max, "seed_mismatches": seed_mismatch,
            "direct_event_mismatches": direct_reconcile, "time_array_length_errors": arrays_bad,
            "pass": len(d) == expected_cells * 30 and unique_cells == expected_cells and duplicate_keys == 0
                    and reps_min == reps_max == 30 and seed_mismatch == 0 and direct_reconcile == 0 and arrays_bad == 0,
        })
    out = pd.DataFrame(rows)
    old = data[data.design == "C-D50"].sort_values(KEYS).reset_index(drop=True)
    new = data[data.design == "NC-NoOp"].sort_values(KEYS).reset_index(drop=True)
    numeric_common = sorted(set(old.select_dtypes(include=np.number).columns) & set(new.select_dtypes(include=np.number).columns))
    excluded = {"dose_center", "dose_spread", "dose_anchor", "strength_anchor", "opinion_reversion_mu"}
    numeric_common = [c for c in numeric_common if c not in excluded]
    max_abs = max(float(np.nanmax(np.abs(old[c].to_numpy(float) - new[c].to_numpy(float)))) for c in numeric_common)
    array_common = ["direct_exposures_by_step","secondhand_exposures_by_step","total_exposures_by_step","opinion_shift_by_step","cumulative_total_shift_by_step"]
    array_mismatch = sum(int((old[c].astype(str).to_numpy() != new[c].astype(str).to_numpy()).sum()) for c in array_common)
    summary = {
        "designs": int(len(out)), "runs": int(len(data)), "all_design_checks_pass": bool(out["pass"].all()),
        "no_op_numeric_max_abs_difference": max_abs, "no_op_array_mismatches": int(array_mismatch),
    }
    return out, summary


def subset_value(cell: pd.DataFrame, outcome: str, subset: tuple[str, ...], R: int) -> float:
    grand = float(cell[outcome].mean())
    if not subset:
        return 0.0
    means = cell.groupby(list(subset), observed=True)[outcome].transform("mean")
    return float(R * np.square(means - grand).sum())


def decompose_design(d: pd.DataFrame, outcome: str) -> tuple[dict, list[dict]]:
    cell = d.groupby(FACTORS, as_index=False, observed=True)[outcome].mean()
    R = int(d.groupby(FACTORS, observed=True).size().iloc[0])
    grand = float(d[outcome].mean())
    d2 = d.merge(cell, on=FACTORS, suffixes=("", "_cell"), validate="many_to_one")
    ss_sys = float(R * np.square(cell[outcome] - grand).sum())
    ss_mc = float(np.square(d2[outcome] - d2[f"{outcome}_cell"]).sum())
    subsets = [s for k in range(0, len(FACTORS)+1) for s in itertools.combinations(FACTORS, k)]
    values = {s: subset_value(cell, outcome, s, R) for s in subsets}
    pure = {}
    for s in subsets[1:]:
        pure[s] = values[s] - sum(v for t, v in pure.items() if set(t).issubset(s) and t != s)
    detail = []
    for s, ss in pure.items():
        detail.append({"effect": " × ".join(s), "order": len(s), "ss": ss, "share_sys": ss / ss_sys if ss_sys else np.nan})
    shapley = {}
    K = len(FACTORS)
    for f in FACTORS:
        phi = 0.0
        others = [x for x in FACTORS if x != f]
        for k in range(K):
            for s in itertools.combinations(others, k):
                w = math.factorial(k) * math.factorial(K-k-1) / math.factorial(K)
                phi += w * (values[tuple(sorted(s + (f,), key=FACTORS.index))] - values[tuple(sorted(s, key=FACTORS.index))])
        shapley[f] = phi
    summary = {"ss_sys": ss_sys, "ss_mc": ss_mc, "ms_mc": ss_mc / (len(d)-len(cell)), "grand_mean": grand,
               "cell_mean_mc_se_median": float(np.median(d.groupby(FACTORS, observed=True)[outcome].std(ddof=1) / np.sqrt(R)))}
    for f in FACTORS:
        main_ss = pure[(f,)]
        summary[f"main_ss__{f}"] = main_ss
        summary[f"main_share__{f}"] = main_ss / ss_sys if ss_sys else np.nan
        summary[f"shapley_ss__{f}"] = shapley[f]
        summary[f"shapley_share__{f}"] = shapley[f] / ss_sys if ss_sys else np.nan
    return summary, detail


def variance_analysis(data: pd.DataFrame, reg: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summaries, details = [], []
    for design, d in data.groupby("design", sort=False):
        for outcome in OUTCOMES:
            s, det = decompose_design(d, outcome)
            s.update({"design": design, "outcome": outcome})
            summaries.append(s)
            for x in det:
                x.update({"design": design, "outcome": outcome})
                details.append(x)
    wide = pd.DataFrame(summaries)
    detail = pd.DataFrame(details)
    metric_rows = []
    for outcome in OUTCOMES:
        b = wide[(wide.design == BENCHMARK) & (wide.outcome == outcome)].iloc[0]
        for row in wide[wide.outcome == outcome].itertuples(index=False):
            base = {"design": row.design, "outcome": outcome, "tau": row.ss_sys/b.ss_sys, "omega": row.ss_mc/b.ss_mc,
                    "ss_sys": row.ss_sys, "ss_mc": row.ss_mc}
            for f in FACTORS:
                for kind in ["main", "shapley"]:
                    ss = getattr(row, f"{kind}_ss__{f}")
                    bss = b[f"{kind}_ss__{f}"]
                    metric_rows.append(base | {"factor": f, "allocation": kind,
                        "p_sys": ss/row.ss_sys if row.ss_sys else np.nan,
                        "q_sys": ss/b.ss_sys, "rho": ss/bss if bss else np.nan, "factor_ss": ss})
    metrics = pd.DataFrame(metric_rows)
    return wide, detail, metrics


def message_contrasts(data: pd.DataFrame, n_boot: int = 1000, seed: int = 20260805) -> pd.DataFrame:
    eligible = ["E-S", "E-SD", "S-A06", "S-A18", "J-S06-D05", "J-S06-D50", "J-S06-D95", "J-S14-D50", "J-S14-D95", "J-S18-D05", "J-S18-D50", "J-S18-D95"]
    rows = []
    rng = np.random.default_rng(seed)
    unlabeled = ["high_quality_ai", "low_quality_ai", "human_equivalent"]
    for design, d in data[data.design.isin(eligible)].groupby("design", sort=False):
        for outcome in OUTCOMES:
            means = d.groupby("message_condition", observed=True)[outcome].mean()
            repmeans = d.groupby(["replication","message_condition"], observed=True)[outcome].mean().unstack()
            def calc(x):
                return {
                    "labeled vs mean unlabeled": x["labeled_ai"] - x[unlabeled].mean(),
                    "high-quality vs low-quality (unlabeled)": x["high_quality_ai"] - x["low_quality_ai"],
                    "high-quality vs human-equivalent": x["high_quality_ai"] - x["human_equivalent"],
                    "low-quality vs human-equivalent": x["low_quality_ai"] - x["human_equivalent"],
                }
            point = calc(means)
            draws = {k: [] for k in point}
            for _ in range(n_boot):
                sampled = repmeans.iloc[rng.integers(0,len(repmeans),len(repmeans))].mean(axis=0)
                for k,v in calc(sampled).items(): draws[k].append(v)
            for name, estimate in point.items():
                lo, med, hi = np.quantile(draws[name],[.025,.5,.975])
                rows.append({"design": design, "outcome": outcome, "contrast": name, "estimate": float(estimate),
                             "bootstrap_median": med, "lo95": lo, "hi95": hi})
    return pd.DataFrame(rows)


def spline_models(data: pd.DataFrame) -> pd.DataFrame:
    rows = []
    xcol, gcol = "log_exposure", "seeding_regime"
    use = data.copy()
    use[xcol] = np.log1p(use["mean_cumulative_exposure"])
    for design, d in use.groupby("design", sort=False):
        fold = d["replication"].astype(int) % 5
        for outcome in OUTCOMES:
            y = d[outcome].to_numpy(float)
            specs = {
                "M1 regime": (make_pipeline(OneHotEncoder(drop="first", handle_unknown="ignore"), LinearRegression()), [gcol]),
                "M2 spline(exposure)": (make_pipeline(SplineTransformer(n_knots=5, degree=3, include_bias=False), LinearRegression()), [xcol]),
                "M3 spline + regime": (make_pipeline(ColumnTransformer([("spl", SplineTransformer(n_knots=5, degree=3, include_bias=False), [xcol]), ("reg", OneHotEncoder(drop="first", handle_unknown="ignore"), [gcol])]), LinearRegression()), [xcol,gcol]),
                "M4 regime-specific splines": (None, [xcol,gcol]),
            }
            for model_name, (model, cols) in specs.items():
                if model_name.startswith("M4"):
                    tmp = d[[xcol,gcol]].copy()
                    for lev in sorted(tmp[gcol].unique()):
                        tmp[f"x_{lev}"] = tmp[xcol] * (tmp[gcol] == lev).astype(float)
                    num = [c for c in tmp if c.startswith("x_")]
                    model = make_pipeline(ColumnTransformer([("spl", SplineTransformer(n_knots=5, degree=3, include_bias=False), num), ("reg", OneHotEncoder(drop="first", handle_unknown="ignore"), [gcol])]), LinearRegression())
                    X = tmp[num+[gcol]]
                else:
                    X = d[cols]
                model.fit(X, y)
                pred = model.predict(X)
                cv_pred = np.empty_like(y)
                for f in range(5):
                    tr, te = fold != f, fold == f
                    model.fit(X.loc[tr], y[tr])
                    cv_pred[te] = model.predict(X.loc[te])
                rows.append({"design": design, "outcome": outcome, "model": model_name,
                    "r2_in": r2_score(y,pred), "rmse_in": mean_squared_error(y,pred)**.5,
                    "r2_cv": r2_score(y,cv_pred), "rmse_cv": mean_squared_error(y,cv_pred)**.5})
    out = pd.DataFrame(rows)
    pivot = out.pivot_table(index=["design","outcome"], columns="model", values="r2_cv").reset_index()
    pivot["increment_M3_minus_M2"] = pivot["M3 spline + regime"] - pivot["M2 spline(exposure)"]
    pivot["increment_M4_minus_M3"] = pivot["M4 regime-specific splines"] - pivot["M3 spline + regime"]
    return out.merge(pivot[["design","outcome","increment_M3_minus_M2","increment_M4_minus_M3"]], on=["design","outcome"], how="left")


def bootstrap_metrics(data: pd.DataFrame, n_boot: int = 1000, seed: int = 20260805) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    ordered = {}
    base_cells = None
    for design, d in data.groupby("design", sort=False):
        d = d.sort_values(KEYS)
        ordered[design] = {o: d[o].to_numpy(float).reshape(144,30) for o in OUTCOMES}
        if base_cells is None:
            base_cells = d[FACTORS].drop_duplicates().reset_index(drop=True)
    subsets = [s for k in range(0,5) for s in itertools.combinations(FACTORS,k)]
    group_codes = {}
    group_counts = {}
    for s in subsets:
        if not s:
            group_codes[s] = np.zeros(144, dtype=int)
        else:
            group_codes[s] = base_cells.groupby(list(s), sort=True, observed=True).ngroup().to_numpy()
        group_counts[s] = np.bincount(group_codes[s])

    def fast_values(cellmean: np.ndarray, grand: float) -> dict:
        ans = {(): 0.0}
        for s in subsets[1:]:
            codes, counts = group_codes[s], group_counts[s]
            sums = np.bincount(codes, weights=cellmean, minlength=len(counts))
            means = sums / counts
            ans[s] = float(30 * np.sum(counts * np.square(means-grand)))
        return ans

    rows = []
    for b in range(n_boot):
        idx = rng.integers(0,30,size=(144,30))
        results = {}
        for design, od in ordered.items():
            for outcome, arr in od.items():
                sample = np.take_along_axis(arr, idx, axis=1)
                cellmean = sample.mean(axis=1)
                grand = sample.mean()
                ss_sys = float(30*np.square(cellmean-grand).sum())
                ss_mc = float(np.square(sample-cellmean[:,None]).sum())
                vals = fast_values(cellmean, grand)
                shap = {}
                for f in FACTORS:
                    phi=0.; others=[x for x in FACTORS if x!=f]
                    for k in range(4):
                        for s in itertools.combinations(others,k):
                            w=math.factorial(k)*math.factorial(3-k)/math.factorial(4)
                            sf=tuple(sorted(s+(f,),key=FACTORS.index)); ss=tuple(sorted(s,key=FACTORS.index))
                            phi += w*(vals[sf]-vals[ss])
                    shap[f]=phi
                results[(design,outcome)] = (ss_sys,ss_mc,vals,shap)
        for (design,outcome),(ss_sys,ss_mc,vals,shap) in results.items():
            bsys,bmc,bvals,bshap=results[(BENCHMARK,outcome)]
            rows.extend([
                {"bootstrap":b,"design":design,"outcome":outcome,"metric":"tau","value":ss_sys/bsys},
                {"bootstrap":b,"design":design,"outcome":outcome,"metric":"omega","value":ss_mc/bmc},
            ])
            for f in ["seeding_regime","message_condition"]:
                rows.extend([
                    {"bootstrap":b,"design":design,"outcome":outcome,"metric":f"main_share__{f}","value":vals[(f,)]/ss_sys},
                    {"bootstrap":b,"design":design,"outcome":outcome,"metric":f"main_rho__{f}","value":vals[(f,)]/bvals[(f,)] if bvals[(f,)] else np.nan},
                    {"bootstrap":b,"design":design,"outcome":outcome,"metric":f"shapley_share__{f}","value":shap[f]/ss_sys},
                    {"bootstrap":b,"design":design,"outcome":outcome,"metric":f"shapley_rho__{f}","value":shap[f]/bshap[f] if bshap[f] else np.nan},
                ])
    raw = pd.DataFrame(rows)
    return raw.groupby(["design","outcome","metric"])["value"].quantile([.025,.5,.975]).unstack().reset_index().rename(columns={.025:"lo95",.5:"median",.975:"hi95"})


def main():
    print("Reproducing initial R30 descriptive analyses", flush=True)
    reg = registry()
    reg.to_csv(ANALYSIS / "design_registry.csv", index=False)
    data = load_data(reg)
    checks, check_summary = integrity_checks(data, reg)
    checks.to_csv(ANALYSIS / "integrity_checks.csv", index=False)
    (ANALYSIS / "integrity_summary.json").write_text(json.dumps(check_summary,indent=2),encoding="utf-8")
    if not check_summary["all_design_checks_pass"] or check_summary["no_op_numeric_max_abs_difference"] != 0 or check_summary["no_op_array_mismatches"] != 0:
        raise RuntimeError(f"Integrity validation failed: {check_summary}")
    wide, details, metrics = variance_analysis(data, reg)
    wide.to_csv(ANALYSIS / "variance_components.csv", index=False)
    details.to_csv(ANALYSIS / "anova_effects_systematic.csv", index=False)
    metrics.to_csv(ANALYSIS / "factor_metrics.csv", index=False)
    print("Message contrasts", flush=True)
    message_contrasts(data).to_csv(ANALYSIS / "planned_message_contrasts.csv", index=False)
    print("Exposure splines", flush=True)
    spline_models(data).to_csv(ANALYSIS / "exposure_spline_metrics.csv", index=False)
    print("Descriptive bootstrap, 1000 draws", flush=True)
    boot = bootstrap_metrics(data)
    boot.to_csv(ANALYSIS / "bootstrap_key_metrics.csv", index=False)
    core = metrics[(metrics.outcome=="mean_total_shift") & (metrics.factor.isin(["seeding_regime","message_condition"]))]
    summary = {
        **check_summary,
        "centered_seeding_main_shares": core[(core.allocation=="main") & core.design.isin(["CS-0","CS-15","CS-30","CS-45","CS-45-R"])].set_index("design")["p_sys"].to_dict(),
        "dose_anchor_seeding_retention": core[(core.allocation=="main") & core.design.isin(["C-D1","CS-0","D-A95"])].set_index("design")["rho"].to_dict(),
        "positive_control_seeding_shapley_shares": core[(core.allocation=="shapley") & core.design.isin(["CS-0","PC-M01","PC-M05"])].set_index("design")["p_sys"].to_dict(),
    }
    (ANALYSIS / "analysis_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))


if __name__ == "__main__":
    main()
