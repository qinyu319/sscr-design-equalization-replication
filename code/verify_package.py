"""Verify release integrity, data invariants, portability, and GitHub file limits."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path, PurePosixPath

from prepare_archive import ensure_archive


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest_sha256.csv"
DATA = ROOT / "data" / "combined_runs_120960.csv.gz"
GITHUB_LIMIT = 100 * 1024 * 1024
REQUIRED = [
    ROOT / "requirements.txt",
    ROOT / "code" / "run_complete_u_validation.py",
    ROOT / "code" / "create_complete_u_figures.py",
    ROOT / "code" / "create_figures.py",
    DATA,
]
KEYS = [
    "design",
    "topology",
    "message_condition",
    "inoculation",
    "seeding_regime",
    "replication",
]
SEED_COLUMNS = [
    "master_seed",
    "network_seed",
    "initialization_seed",
    "seeding_seed",
    "sharing_seed",
    "noise_seed",
    "inoculation_seed",
]
TEXT_SUFFIXES = {".py", ".md", ".yml", ".yaml", ".json", ".cff", ".txt", ".ipynb", ".csv", ".svg"}
EMAIL_RE = re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b")
WIN_ABS_RE = re.compile(r"(?i)(?<![A-Z0-9_])[A-Z]:[\\/]")
HOME_ABS_RE = re.compile(r"/(?:Users|home)/[^/\s]+/")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def check_manifest(errors: list[str]) -> int:
    checked = 0
    with MANIFEST.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            rel = PurePosixPath(row["path"])
            path = ROOT.joinpath(*rel.parts)
            if not path.is_file():
                errors.append(f"manifest file missing: {rel}")
                continue
            checked += 1
            if path.stat().st_size != int(row["bytes"]):
                errors.append(f"size mismatch: {rel}")
            elif sha256(path).lower() != row["sha256"].lower():
                errors.append(f"SHA-256 mismatch: {rel}")
    return checked


def check_archive(errors: list[str]) -> dict[str, object]:
    row_count = 0
    designs: set[str] = set()
    seen: set[tuple[str, ...]] = set()
    duplicates = 0
    replication_sets: dict[tuple[str, ...], set[int]] = {}

    with gzip.open(DATA, "rt", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        columns = set(reader.fieldnames or [])
        missing = [column for column in KEYS + SEED_COLUMNS if column not in columns]
        if missing:
            errors.append("archive columns missing: " + ", ".join(missing))
            return {"rows": 0, "designs": 0, "replication_counts": []}

        for row in reader:
            row_count += 1
            key = tuple(row[column] for column in KEYS)
            if key in seen:
                duplicates += 1
            else:
                seen.add(key)
            designs.add(row["design"])
            cell = tuple(row[column] for column in KEYS[:-1])
            replication_sets.setdefault(cell, set()).add(int(row["replication"]))
            for column in SEED_COLUMNS:
                if not row[column].strip():
                    errors.append(f"blank {column} at archive row {row_count + 1}")
                    return {"rows": row_count, "designs": len(designs), "replication_counts": []}

    counts = sorted({len(values) for values in replication_sets.values()})
    extended = {"E-SD", "J-S06-D05", "J-S18-D05"}
    for design in designs:
        cells = {key: values for key, values in replication_sets.items() if key[0] == design}
        expected_reps = set(range(60 if design in extended else 30))
        if len(cells) != 144 or any(values != expected_reps for values in cells.values()):
            errors.append(f"incomplete cell grid or replication indices: {design}")
    if row_count != 120_960:
        errors.append(f"archive row count is {row_count}, expected 120960")
    if len(designs) != 25:
        errors.append(f"archive design count is {len(designs)}, expected 25")
    if counts != [30, 60]:
        errors.append(f"native replication counts are {counts}, expected [30, 60]")
    if duplicates:
        errors.append(f"archive contains {duplicates} duplicate design/cell/replication keys")
    return {"rows": row_count, "designs": len(designs), "replication_counts": counts}


def check_public_files(errors: list[str]) -> dict[str, int]:
    oversized = 0
    identity_hits = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in {".git", ".venv", "__pycache__", "outputs"} for part in path.relative_to(ROOT).parts):
            continue
        if path.stat().st_size >= GITHUB_LIMIT:
            oversized += 1
            errors.append(f"file reaches GitHub's 100 MiB limit: {path.relative_to(ROOT)}")
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if EMAIL_RE.search(text) or WIN_ABS_RE.search(text) or HOME_ABS_RE.search(text):
            identity_hits += 1
            errors.append(f"possible identity or absolute-path string: {path.relative_to(ROOT)}")
    return {"oversized_files": oversized, "identity_or_absolute_path_hits": identity_hits}


def main() -> None:
    errors: list[str] = []
    try:
        ensure_archive()
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "FAIL", "errors": [str(exc)]}, indent=2))
        sys.exit(1)
    for path in REQUIRED + [MANIFEST]:
        if not path.is_file():
            errors.append(f"required file missing: {path.relative_to(ROOT)}")

    manifest_files = check_manifest(errors) if MANIFEST.is_file() else 0
    archive = check_archive(errors) if DATA.is_file() else {}
    public = check_public_files(errors)
    result = {
        "status": "PASS" if not errors else "FAIL",
        "manifest_files_checked": manifest_files,
        **archive,
        **public,
        "errors": errors,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
