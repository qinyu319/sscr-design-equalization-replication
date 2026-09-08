"""Rebuild the SHA-256 release manifest after intentional package changes."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "manifest_sha256.csv"
EXCLUDED_PARTS = {".git", ".venv", "__pycache__", "outputs", "tmp", "temp"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def included(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    return (
        path.is_file()
        and path != OUTPUT
        and relative.as_posix() != "data/combined_runs_120960.csv.gz"
        and not any(part in EXCLUDED_PARTS for part in relative.parts)
        and path.suffix.lower() not in {".zip", ".7z", ".tar"}
    )


def main() -> None:
    paths = sorted(
        (path for path in ROOT.rglob("*") if included(path)),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )
    with OUTPUT.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["path", "bytes", "sha256"])
        for path in paths:
            writer.writerow(
                [path.relative_to(ROOT).as_posix(), path.stat().st_size, sha256(path)]
            )
    print(f"Wrote {len(paths)} entries to {OUTPUT.name}")


if __name__ == "__main__":
    main()
