# Release 1.2.0 — submission package

Prepared 8 September 2026 for the supplied SSCR manuscript and supplement.

- Preserved the original 120,960-run archive and frozen model implementation.
- Added portable copies of the original R30 descriptive-analysis and one-shot screening scripts. Their mathematical procedures and random seeds are unchanged; input/output paths now resolve inside the repository.
- Added the independently archived initial paired seed manifest and a preparation command that maps 28 configurations onto all 120,960 archived runs, exports exact seed replay inputs and records release configuration hashes.
- Repaired the executed notebook's old analysis-directory reference; retained 20 cells, including 11 code cells, and added the final complete-U outputs to its existing result view.
- Added manuscript table exports, displayed-value checks and the current figure/table map.
- Restored the missing archived extension-width input used by the legacy figure command and added a direct entry point for Supplement Figure F1.
- Preserved all eight submitted figure images. Computational versions and final submission artwork are explicitly distinguished.
- Extended the verifier to check every design's 144-cell grid, exact replication indices and public notebook/CSV/SVG text.

Result reproduction was tested in a clean Python 3.12 environment using the pinned analysis dependencies. Primary and descriptive tables were compared with the pre-existing frozen package; comparison tolerances and results are recorded in `validation/reproduction_comparison.json`.

The full 120,960-run ABM matrix was not rerun for this release. A separate representative seed-replay check is documented in `validation/simulation_replay_checks.json`. The optional one-shot screening computation is separate from that archived main simulation matrix.

Original plans and method addenda retain their historical dates and claims. This release does not turn those documents into preregistration. No new license or DOI has been assigned.

The 1.2.0 packaging correction enforces LF line endings for all text files so Git archives and Windows checkouts preserve the frozen manifest hashes.

Release 1.2.0 transports the original compressed archive in eight lossless binary parts because large HTTP uploads were rejected. `verify_package.py` reassembles the identical original gzip locally and checks both part hashes and the original full-file SHA-256. Simulation values and analysis methods are unchanged.
