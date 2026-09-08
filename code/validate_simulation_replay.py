from pathlib import Path
import sys, json
import numpy as np
import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "code"))
import run_revision as runner

data = pd.read_csv(ROOT / "data/combined_runs_120960.csv.gz")
registry = pd.read_csv(ROOT / "analysis_outputs/configuration_replay_registry.csv")
results = []
numeric = ["mean_total_shift", "mean_signed_shift", "conversion_rate", "mean_cumulative_exposure",
           "total_direct_exposures", "total_secondhand_exposures", "total_exposures"]
arrays = ["direct_exposures_by_step", "secondhand_exposures_by_step", "total_exposures_by_step",
          "opinion_shift_by_step", "cumulative_total_shift_by_step"]
for i, entry in enumerate(registry.itertuples(index=False)):
    cfg = yaml.safe_load((ROOT / entry.config).read_text(encoding="utf-8"))
    subset = data[(data.design == entry.design) & data.replication.between(entry.replication_start, entry.replication_start + entry.replications - 1)]
    row = subset.iloc[(i * 137) % len(subset)]
    manifests = runner.load_seed_manifest(str(ROOT / entry.seed_manifest))
    key = tuple(row[k] for k in ["topology", "message_condition", "inoculation", "seeding_regime", "replication"])
    result = runner.run_single(row.topology, row.message_condition, cfg["design"]["message_conditions"][row.message_condition],
                               row.inoculation, row.seeding_regime, cfg["simulation"], int(row.replication),
                               seed_override=manifests[key])
    checks = {c: bool(np.isclose(result[c], row[c], rtol=1e-10, atol=1e-12)) for c in numeric}
    for c in arrays:
        value = json.loads(result[c]) if isinstance(result[c], str) else result[c]
        checks[c] = bool(np.allclose(value, json.loads(row[c]), rtol=1e-10, atol=1e-12))
    results.append({"config": entry.config, "design": entry.design,
                    "key": [str(k) for k in key], "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks})
out = ROOT / "validation"
out.mkdir(exist_ok=True)
summary = {"status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL",
           "scope": "One archived run per configuration (28 runs); not a rerun of the complete ABM matrix.",
           "rtol": 1e-10, "atol": 1e-12, "results": results}
(out / "simulation_replay_checks.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(summary["status"], len(results), "archived simulations replayed")
if summary["status"] != "PASS":
    print(json.dumps([r for r in results if r["status"] != "PASS"], indent=2))
    raise SystemExit(1)
