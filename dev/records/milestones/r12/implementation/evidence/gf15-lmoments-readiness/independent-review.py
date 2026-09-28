"""Mechanically verify frozen Stage 1 evidence; scientific signoff is separate.

This checker imports neither candidate nor oracle and cannot issue readiness
acceptance. The independent model-validator owns the signed scientific verdict.
"""

import argparse
import hashlib
import json
import struct
from decimal import Decimal, localcontext
from pathlib import Path


def digest(path: Path) -> str:
    """Hash an immutable artifact's exact bytes."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path: Path):
    """Read UTF-8 evidence without importing its implementation."""
    return json.loads(path.read_text(encoding="utf-8"))


def verify(results: Path) -> dict:
    """Recompute core hashes, counts and quantile interval gates independently."""
    root = Path(__file__).resolve().parent
    manifest = read(results / "attempt.json")
    receipt = read(results / "completion.json")
    if digest(results / "attempt.json") != receipt["attempt_sha256"]:
        raise ValueError("attempt identity mismatch")
    for name, expected in manifest["source"].items():
        if digest(root / name) != expected:
            raise ValueError(f"source changed: {name}")
    if (
        digest(root / "environment/artifact-inventory.json")
        != manifest["environment_inventory_sha256"]
    ):
        raise ValueError("environment identity mismatch")
    for name, expected in receipt["files"].items():
        if digest(results / name) != expected:
            raise ValueError(f"result changed: {name}")
    audit = read(results / "input-audit.json")
    if (audit["A_keys"], audit["B_keys"], audit["selected_file_count"]) != (
        144000,
        144000,
        732,
    ):
        raise ValueError("incomplete predecessor audit")
    for record in audit["files"]:
        path = root.parent / record["path"]
        if digest(path) != record["sha256"] or path.stat().st_size != record["bytes"]:
            raise ValueError("predecessor changed")
    controls = read(results / "numerical-controls.json")
    if tuple(len(controls[k]) for k in ("population", "branches", "quantiles")) != (
        3,
        19,
        44,
    ):
        raise ValueError("missing fixed controls")
    for row in controls["population"]:
        if not row["passed"] or any(value > 1e-5 for value in row["errors"].values()):
            raise ValueError("failed original population gate")
    comparisons = 0
    with localcontext() as context:
        context.prec = 120
        for case in controls["quantiles"]:
            for coordinate in ("normalized", "physical"):
                row = case[coordinate]
                output = struct.unpack(">d", bytes.fromhex(row["output_bits"]))[0]
                if output != row["output"]:
                    raise ValueError("output bits mismatch")
                intervals = [
                    tuple(map(Decimal, item["enclosure"]))
                    for item in row["precision_passes"]
                ]
                if max(a for a, _ in intervals) > min(b for _, b in intervals):
                    raise ValueError("enclosures do not overlap")
                lower, upper = (
                    min(a for a, _ in intervals),
                    max(b for _, b in intervals),
                )
                s = Decimal.from_float(row["normalization_scale"])
                exact_output = Decimal.from_float(output)
                tolerance = Decimal(row["T_normalized"])
                if (
                    max(abs(exact_output - lower), abs(exact_output - upper)) / s
                    > tolerance
                ):
                    raise ValueError("quantile-space gate failed")
                if (upper - lower) / s > tolerance * Decimal("2e-20"):
                    raise ValueError("reference-width budget failed")
                if (
                    row["outcome"] != "pass"
                    or not row["rounding_cell_intersects_support"]
                ):
                    raise ValueError("unsupported quantile")
                comparisons += 1
    return {
        "mechanical_verification": "passed",
        "scientific_verdict": "requires independent model-validator",
        "completion_sha256": digest(results / "completion.json"),
        "source": manifest["source"],
        "A_keys": 144000,
        "B_keys": 144000,
        "selected_files": 732,
        "population_controls": 3,
        "branch_controls": 19,
        "dual_precision_quantile_comparisons": comparisons,
        "matrix_fits_executed": 0,
    }


def main() -> None:
    """Write an exclusive mechanical review record to the requested destination."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    result = verify(arguments.results)
    with arguments.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("Mechanical verification passed; scientific verdict remains independent")


if __name__ == "__main__":
    main()
