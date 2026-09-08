"""Run the paper result-reproduction workflow from any working directory."""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(script: str, *arguments: str) -> None:
    path = ROOT / "code" / script
    print(f"\n==> {script}", flush=True)
    subprocess.run([sys.executable, str(path), *arguments], cwd=ROOT, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recompute the primary analyses and/or manuscript figures."
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--figures-only",
        action="store_true",
        help="Regenerate figures from the included analysis outputs.",
    )
    mode.add_argument(
        "--analysis-only",
        action="store_true",
        help="Recompute primary analysis tables without regenerating figures.",
    )
    parser.add_argument(
        "--include-descriptive",
        action="store_true",
        help="Also reproduce the original R30 decomposition, contrasts, splines, and descriptive bootstrap.",
    )
    parser.add_argument(
        "--skip-verification",
        action="store_true",
        help="Skip the pre-run package integrity and schema checks.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    started = time.perf_counter()

    if not args.skip_verification:
        run("verify_package.py")

    if args.include_descriptive and not args.figures_only:
        run("run_descriptive_analysis.py")

    if not args.figures_only:
        run("run_complete_u_validation.py")

    if not args.analysis_only:
        run("create_complete_u_figures.py")
        run("create_figures.py")
        run("create_crossfit_revision_figures.py", "--submitted-only")

    run("export_manuscript_tables.py")

    elapsed = time.perf_counter() - started
    print(f"\nReproduction workflow completed in {elapsed:.1f} seconds.")


if __name__ == "__main__":
    main()
