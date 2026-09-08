"""Export machine-readable counterparts of manuscript Tables 4A, 4B, and 5."""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AN = ROOT / "analysis_outputs"


def main():
    points = pd.read_csv(AN / "complete_u_point_estimates.csv")
    seed = points[(points.outcome == "mean_total_shift") & (points.factor == "seeding_regime")].set_index("design")
    descriptive = pd.read_csv(AN / "factor_metrics.csv")
    descriptive = descriptive[(descriptive.outcome == "mean_total_shift") & (descriptive.factor == "seeding_regime")]
    shares = descriptive.pivot(index="design", columns="allocation", values="p_sys") * 100
    high = ["C-D50", "CS-0", "CS-15", "CS-30", "CS-45", "E-S"]
    table4a = seed.loc[high, ["replications", "B_factor_U", "q_proportion"]].join(shares[["main", "shapley"]])
    table4a = table4a.rename(columns={"main": "seed_main_percent", "shapley": "seed_shapley_percent"})
    table4a.to_csv(AN / "manuscript_table_4a.csv")
    ranges = pd.read_csv(AN / "complete_u_bootstrap_ranges.csv")
    ranges = ranges[(ranges.outcome == "mean_total_shift") & (ranges.factor == "seeding_regime") & (ranges.metric == "q_proportion")].set_index("design")
    split = pd.read_csv(AN / "repeated_split_summary.csv")
    split = split[(split.outcome == "mean_total_shift") & (split.factor == "seeding_regime")].set_index("design")
    near = ["E-SD", "J-S06-D05", "J-S18-D05"]
    table4b = seed.loc[near, ["replications", "B_total_U", "B_factor_U", "q_proportion"]]
    table4b = table4b.join(ranges[["p02_5", "p97_5"]]).join(split[["positive_frequency"]])
    table4b.to_csv(AN / "manuscript_table_4b.csv")
    table5 = seed.loc[["CS-0", "PC-M01", "PC-M05"], ["replications", "B_factor_U", "q_proportion"]]
    table5.to_csv(AN / "manuscript_table_5_controls.csv")
    # Independently transcribed displayed values from the submitted main manuscript.
    checks = {
        "table_4a_main_percent": np.allclose(table4a.seed_main_percent, [82.54, .45, 21.96, 54.47, 71.81, 98.09], atol=.0051, rtol=0),
        "table_4a_shapley_percent": np.allclose(table4a.seed_shapley_percent, [87.17, .50, 23.27, 57.77, 76.22, 98.65], atol=.0051, rtol=0),
        "table_4a_complete_u": np.allclose(table4a.B_factor_U, [.00293, 8.1e-7, 4.85e-5, .00022, .000528, .00296], rtol=.0025, atol=0),
        "table_4b_complete_u": np.allclose(table4b.B_factor_U, [9.51e-11, -2.47e-11, 2.56e-10], rtol=.003, atol=0),
        "table_4b_positive_splits": np.allclose(table4b.positive_frequency, [.74, .20, .89], atol=.0001, rtol=0),
        "table_5_control_points": np.allclose(table5.B_factor_U, [8.10e-7, 6.95e-6, 2.32e-5], rtol=.003, atol=0),
    }
    result = {"status": "PASS" if all(checks.values()) else "FAIL", "checks": {k: bool(v) for k, v in checks.items()},
              "scope": "Selected numerical columns in submitted Tables 4A, 4B and 5; tolerance follows displayed rounding."}
    (AN / "manuscript_alignment_checks.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
