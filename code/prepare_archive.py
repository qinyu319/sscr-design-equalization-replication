"""Reassemble and verify the frozen archive from transport-sized binary parts."""
from pathlib import Path
import hashlib
import json
import os

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def ensure_archive():
    description = json.loads((ROOT / "data/archive_parts.json").read_text(encoding="utf-8"))
    output = ROOT / "data/combined_runs_120960.csv.gz"
    for part in description["parts"]:
        path = ROOT / part["path"]
        if not path.is_file() or path.stat().st_size != part["bytes"] or digest(path) != part["sha256"]:
            raise ValueError(f"Missing or corrupt archive part: {part['path']}")
    if output.exists():
        if output.stat().st_size != description["bytes"] or digest(output) != description["sha256"]:
            raise ValueError("Existing assembled archive differs from the frozen input; inspect it before replacing it.")
        return output
    temporary = output.with_suffix(".gz.assembling")
    with temporary.open("wb") as handle:
        for part in description["parts"]:
            with (ROOT / part["path"]).open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    handle.write(chunk)
    if temporary.stat().st_size != description["bytes"] or digest(temporary) != description["sha256"]:
        raise ValueError("Reassembled archive checksum differs from the frozen input")
    os.replace(temporary, output)
    print("Reassembled and verified data/combined_runs_120960.csv.gz", flush=True)
    return output


if __name__ == "__main__":
    ensure_archive()
