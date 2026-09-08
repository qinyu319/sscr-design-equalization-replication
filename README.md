# Replication package for Auditing Assigned-Intensity Dependence in Social Simulation

This release accompanies **Auditing Assigned-Intensity Dependence in Social Simulation: A Design-Equalization Framework**, prepared for Social Science Computer Review. It contains the frozen simulation archive, executable analysis and model code, verified results, and the submitted figure artwork. See [MANUSCRIPT_MAP.md](MANUSCRIPT_MAP.md) for the exact correspondence to the supplied manuscript and supplement.

The files have been prepared without author identifiers. Repository ownership and Git metadata can still identify an author; an ordinary private repository URL is not an anonymous reviewer-access link. See [PUBLISHING.md](PUBLISHING.md).

## What is included

- A frozen archive of **120,960** unique design × factorial-cell × replication rows.
- **25** simulation designs, with 30 or 60 replications per cell.
- Seven named random-stream seeds in every run-level row.
- The complete distinct-replication-pair U-statistic analysis used for the manuscript.
- Bootstrap stability ranges, split-count diagnostics, sensitivity checks, and known-truth validation.
- Scripts and source tables for the manuscript figures.
- Frozen model code and all archived/revision configuration files.

The frozen input is transported as eight binary files under `data/archive_parts/`. `python code/verify_package.py` automatically concatenates them into `data/combined_runs_120960.csv.gz` and verifies the original SHA-256. This restores the exact 62 MiB compressed input without network access or changes to the data. The assembled file is ignored by Git; `data/archive_parts.json` records its hash and the hash of every part.

## Quick start

Python 3.12 was tested for this release. Use Python 3.11 or newer; the pinned dependencies do not support Python 3.10.

```bash
python -m venv .venv
```

Activate the environment:

```bash
# macOS/Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Install dependencies and run the full result-reproduction workflow:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python code/verify_package.py
python code/run_all.py --include-descriptive
```

`run_all.py --include-descriptive` recomputes the initial R30 decomposition, planned contrasts, exposure splines and descriptive bootstrap, then runs the primary complete-U analysis and regenerates computational figures and manuscript table exports. Omit `--include-descriptive` for the primary analysis using the bundled descriptive tables. It does **not** rerun the computationally expensive agent-based simulations; the frozen simulation archive is the starting point for result reproduction.

To regenerate figures only from the included analysis tables:

```bash
python code/run_all.py --figures-only
```

## Repository map

| Path | Purpose |
|---|---|
| `data/` | Frozen run-level archive used by the primary analysis |
| `DATA_DICTIONARY.md` | Observational unit, keys, variables, and array encoding |
| `code/` | Analysis, validation, figure, and frozen simulation scripts |
| `configs/` | Frozen simulation design configurations |
| `analysis_outputs/` | Published analysis tables and validation summaries |
| `figures/` | Published figures plus source tables where available |
| `notebooks/` | Executed and reviewable notebook companion |
| `plans/` | Dated analysis plans and revision addenda |
| `REPRODUCIBILITY.md` | Estimator, workflow, outputs, and interpretation notes |
| `PUBLISHING.md` | Repository access and anonymous reviewer-link guidance |
| `MANUSCRIPT_MAP.md` | Current main/supplement figure and table mapping |
| `validation/` | This release’s reproduction and seed-replay evidence |
| `figures/submitted/` | Exact eight PNGs embedded in the supplied submission |
| `manifest_sha256.csv` | SHA-256 manifest for the frozen release snapshot |
| `package_validation.json` | Pre-release validation report |

## Primary analysis

For a factor subset \(S\), the finite-replication estimator is the complete order-two U-statistic

```text
B_U(S) = [R(R-1)]^(-1) sum_{r != s} y_r' H_S y_s,
```

where `H_S` is the equal-cell projection quadratic form. Averaging all ordered distinct replication pairs removes the split-count tuning parameter. The split analysis is retained only as a convergence diagnostic.

The primary commands executed by `code/run_all.py` are:

```bash
python code/run_complete_u_validation.py
python code/create_complete_u_figures.py
python code/create_figures.py
python code/export_manuscript_tables.py
```

Bootstrap percentile ranges are descriptive stability summaries, not calibrated confidence intervals.

## Re-running simulations

`code/run_revision.py` is the frozen agent-based-model runner. Run `python code/prepare_simulation_replay.py` first to export archived per-configuration seed manifests and all 28 replay commands to `outputs/replay_inputs/commands.txt`. The configuration registry covers every initial and extension run and records the SHA-256 of each release configuration. Output paths were made portable during packaging, so release configuration hashes should not be confused with hashes of earlier files on the original machine.

To replay one design exactly from its archived seeds:

```bash
python code/prepare_simulation_replay.py
python code/run_revision.py --config configs/cs_0.yaml --seed_manifest outputs/replay_inputs/cs_0_seed_manifest.csv
```

 A single design can be run from the repository root, for example:

```bash
python code/run_revision.py --config configs/cs_0.yaml
```

Configuration files write to paths under `outputs/`, which is ignored by Git. Full simulation regeneration is intentionally separate from the standard result-reproduction workflow because it is computationally intensive. The included frozen archive and named seeds provide the auditable input to the paper analysis.

## Integrity and anonymity

Run `python code/verify_package.py` to check the frozen manifest, required files, archive dimensions, duplicate keys, seed columns, file-size limits, and absence of absolute paths or email-like strings in public text/code files.

After an intentional release change, rebuild the manifest with `python code/build_manifest.py`, then run the verifier again. Do not rebuild the manifest merely to hide an unexplained mismatch.

For a non-anonymous archival release, replace the placeholder author in `CITATION.cff`, add the article DOI/URL, and select an appropriate code/data license consistent with journal and institutional policy.

## Analysis history

- `plans/prospective_revision_analysis_plan_20260805.md` preceded the 19 revision designs.
- `plans/targeted_reanalysis_addendum_20260805.md` preceded the three 30-to-60 extensions.
- `plans/crossfit_method_revision_addendum_20260805.md` documents the earlier split-based stage.
- `plans/complete_u_method_addendum_20260805.md` documents the final complete-U reanalysis.
- None of these files is represented as preregistration of the original study.

Files containing `crossfit`, `repeated_split`, or `repeated_crossfit` document the preceding analysis stage. They are retained for audit history but are not the manuscript's primary estimator or inferential source.

## Notebook and screening

The included executed notebook has 20 cells, including 11 successfully executed code cells. It can be opened from the repository root or the `notebooks/` directory. Optional notebook execution dependencies are in `requirements-notebook.txt`.

The supplementary one-shot strength grid can be reproduced separately with `python code/reproduce_strength_screening.py` (800 one-step simulations, separate from the 120,960-run main archive).

See [RELEASE_NOTES.md](RELEASE_NOTES.md) for changes, validation scope and limitations. No license is granted by this release; retain author control until a code/data license is selected.
