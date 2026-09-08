"""Export exact archived seed inputs and the 28 configuration-to-design mappings.

This command prepares inputs only; it does not launch the full simulation matrix.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
KEYS = ["topology", "message_condition", "inoculation", "seeding_regime", "replication"]
SEEDS = ["master_seed", "network_seed", "initialization_seed", "seeding_seed",
         "sharing_seed", "noise_seed", "inoculation_seed"]


def main():
    archive = pd.read_csv(ROOT / "data/combined_runs_120960.csv.gz", usecols=["design"] + KEYS + SEEDS)
    registry = pd.read_csv(ROOT / "analysis_outputs/design_registry.csv").set_index("source_id")
    destination = ROOT / "outputs/replay_inputs"
    destination.mkdir(parents=True, exist_ok=True)
    rows = []
    commands = []
    for path in sorted((ROOT / "configs").glob("*.yaml")):
        cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
        design = cfg["design"]
        label = registry.loc[design["name"], "design"]
        first = int(design.get("replication_start", 0))
        count = int(design["replications"])
        subset = archive[(archive.design == label) & archive.replication.between(first, first + count - 1)]
        if len(subset) != 144 * count or subset.duplicated(KEYS).any():
            raise ValueError(f"Incomplete archived replay input: {path.name}")
        seed_path = destination / f"{path.stem}_seed_manifest.csv"
        subset[KEYS + SEEDS].sort_values(KEYS).to_csv(seed_path, index=False)
        config_rel = path.relative_to(ROOT).as_posix()
        seed_rel = seed_path.relative_to(ROOT).as_posix()
        commands.append(f"python code/run_revision.py --config {config_rel} --seed_manifest {seed_rel}")
        rows.append({"config": config_rel, "design": label, "replication_start": first,
                     "replications": count, "rows": len(subset), "seed_manifest": seed_rel,
                     "release_config_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                     "simulation_output": cfg["output"]["dir"]})
    frame = pd.DataFrame(rows)
    if len(frame) != 28 or int(frame.rows.sum()) != 120960:
        raise ValueError("Replay plan does not cover the final archive")
    frame.to_csv(ROOT / "analysis_outputs/configuration_replay_registry.csv", index=False)
    (destination / "commands.txt").write_text("\n".join(commands) + "\n", encoding="utf-8")
    print(json.dumps({"configurations": len(frame), "runs": int(frame.rows.sum()),
                      "commands": "outputs/replay_inputs/commands.txt"}, indent=2))


if __name__ == "__main__":
    main()
