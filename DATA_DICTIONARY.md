# Data Dictionary

The compressed input is shipped as eight lossless parts. Run `python code/verify_package.py` once after download to reconstruct `data/combined_runs_120960.csv.gz` and verify its original hash.

## File and observational unit

`data/combined_runs_120960.csv.gz` is a gzip-compressed CSV. Each row is one `design × topology × message condition × inoculation strategy × seeding regime × replication` simulation run.

The composite key is:

```text
design, topology, message_condition, inoculation, seeding_regime, replication
```

The archive contains 25 designs, 144 factorial cells per design, and either 30 or 60 replications per cell. Replication indices are zero-based (`0`–`29` or `0`–`59`).

## Identification and design fields

| Variable | Type | Description |
|---|---|---|
| `design` | string | Frozen short identifier for the simulation design |
| `family` | string | Higher-level design family used to group related audits |
| `topology` | category | Network topology: `BA`, `ER`, `WS`, or `SBM` |
| `message_condition` | category | Message condition: `high_quality_ai`, `low_quality_ai`, `labeled_ai`, or `human_equivalent` |
| `inoculation` | category | Inoculation strategy: `none`, `random`, or `hub` |
| `seeding_regime` | category | Direct-message schedule: `single_shot`, `burst`, or `continuous` |
| `replication` | integer | Zero-based replication index within a factorial cell |

Network abbreviations denote Barabási–Albert (`BA`), Erdős–Rényi (`ER`), Watts–Strogatz (`WS`), and stochastic block model (`SBM`) topologies. Design-level labels and analysis groupings are also listed in `analysis_outputs/design_registry.csv`.

## Random-stream seeds

All seed fields are integers. Separate named streams allow the paired design comparisons to preserve intended common random numbers while keeping stochastic mechanisms auditable.

| Variable | Description |
|---|---|
| `master_seed` | Master run seed from which stream assignments are organized |
| `network_seed` | Network-generation random stream |
| `initialization_seed` | Agent-state initialization stream |
| `seeding_seed` | Direct-message recipient/schedule stream |
| `sharing_seed` | Secondhand-sharing stream |
| `noise_seed` | Opinion-update noise stream |
| `inoculation_seed` | Inoculation assignment stream |

Seed values repeat deliberately across paired designs and conditions. They are identifiers for deterministic pseudo-random streams, not independent measured variables.

## Assigned-treatment fields

| Variable | Type | Description |
|---|---|---|
| `message_strength` | float | Configured message-effect magnitude for the message condition |
| `delta_m` | float | Frozen runner name for the same configured message-effect magnitude |
| `assigned_direct_seed_events` | integer | Number of direct seed-message events assigned by the design |
| `opinion_reversion_mu` | float | Per-step opinion-reversion parameter |

`message_strength` and `delta_m` are retained together for provenance and compatibility with different analysis stages.

## Realized exposure fields

| Variable | Type | Description |
|---|---|---|
| `mean_cumulative_exposure` | float | Mean number of total exposure events per agent |
| `total_direct_exposures` | integer | Total realized direct exposure events in the run |
| `total_secondhand_exposures` | integer | Total realized secondhand exposure events in the run |
| `total_exposures` | integer | Sum of direct and secondhand exposure events |

## Primary outcomes

| Variable | Type | Description |
|---|---|---|
| `mean_total_shift` | float | Mean absolute change between final and initial agent opinion |
| `mean_signed_shift` | float | Mean opinion change signed toward the target position (0.6) |
| `conversion_rate` | float | Among agents initially below 0, fraction whose final opinion is above 0 |

The exact outcome implementation is in `compute_outcomes()` in `code/run_revision.py`.

## Step-level diagnostic arrays

The following fields are JSON-formatted arrays stored inside CSV cells. Every array has 50 elements, one per simulation step.

| Variable | Element type | Description |
|---|---|---|
| `direct_exposures_by_step` | integer | Direct exposure-event count at each step |
| `secondhand_exposures_by_step` | integer | Secondhand exposure-event count at each step |
| `total_exposures_by_step` | integer | Direct plus secondhand exposure-event count at each step |
| `opinion_shift_by_step` | float | Mean absolute opinion movement generated at each step |
| `cumulative_total_shift_by_step` | float | Cumulative mean absolute opinion shift through each step |

Example loading code:

```python
import json
import pandas as pd

data = pd.read_csv("data/combined_runs_120960.csv.gz")
data["total_exposures_by_step"] = data["total_exposures_by_step"].map(json.loads)
```

## Missingness and integrity

The release verifier checks required columns, row count, design count, replication counts, duplicate composite keys, and blank seed values. Run:

```bash
python code/verify_package.py
```
