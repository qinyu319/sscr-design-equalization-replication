from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "code" / "run_revision.py"
spec = importlib.util.spec_from_file_location("run_revision", RUNNER)
run_revision = importlib.util.module_from_spec(spec)
sys.modules["run_revision"] = run_revision
assert spec.loader is not None
spec.loader.exec_module(run_revision)

CANDIDATES = [0.03, 0.06, 0.09, 0.12, 0.14, 0.18, 0.24, 0.30]
N_SEEDS = 100
CFG = {
    "n_agents": 1000,
    "n_steps": 1,
    "seed_fraction": 0.05,
    "inoculation_budget_fraction": 0.05,
    "sharing_probability": 0.0,
    "second_hand_attenuation": 0.70,
    "disclosure_lambda": 0.70,
    "inoculation_kappa": 0.20,
    "noise_scale": 0.30,
    "target_position": 0.60,
    "activation_threshold": 0.01,
}


def one_shot(delta_m: float, seed: int) -> dict[str, float]:
    agents = run_revision.init_agents(CFG["n_agents"], seed)
    initial = agents.opinions.copy()
    graph = run_revision.build_network("BA", CFG["n_agents"], agents.opinions, seed + 1)
    run_revision.persuasion_step(
        graph,
        agents,
        delta_m,
        False,
        0,
        dict(CFG),
        np.random.default_rng(seed + 10_000),
        np.random.default_rng(seed + 20_000),
        np.random.default_rng(seed + 30_000),
        CFG["seed_fraction"],
    )
    exposed = agents.direct_exposure > 0
    delta = agents.opinions[exposed] - initial[exposed]
    direction = np.sign(CFG["target_position"] - initial[exposed])
    opposed = initial[exposed] < 0
    conversion = float(np.mean(agents.opinions[exposed][opposed] > 0)) if opposed.any() else 0.0
    return {
        "total_shift": float(np.mean(np.abs(delta))),
        "signed_shift": float(np.mean(delta * direction)),
        "conversion": conversion,
    }


def status(delta_m: float) -> str:
    return {
        0.06: "retained low-strength anchor",
        0.14: "retained intermediate/human-equivalent anchor",
        0.18: "retained high and labeled pre-attenuation anchor",
    }.get(delta_m, "candidate not retained")


def main() -> None:
    rows = []
    for delta_m in CANDIDATES:
        simulations = [one_shot(delta_m, seed) for seed in range(N_SEEDS)]
        row = {"candidate_delta": delta_m, "n_seeds": N_SEEDS, "selection_status": status(delta_m)}
        for metric in ("total_shift", "signed_shift", "conversion"):
            values = np.asarray([simulation[metric] for simulation in simulations])
            row[f"mean_{metric}"] = float(values.mean())
            row[f"sd_{metric}"] = float(values.std(ddof=1))
            row[f"lo95_{metric}"] = float(np.quantile(values, 0.025))
            row[f"hi95_{metric}"] = float(np.quantile(values, 0.975))
        rows.append(row)
    out = ROOT / "analysis_outputs" / "strength_screening_grid_revision.csv"
    pd.DataFrame(rows).to_csv(out, index=False)
    print(pd.DataFrame(rows).to_string(index=False))
    print(f"Saved {out}")


if __name__ == "__main__":
    main()

