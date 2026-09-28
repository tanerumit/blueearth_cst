"""Re-score signed GF15 summaries; no estimator imports, new fits or cohort changes."""

import argparse
import copy
import hashlib
import itertools
import json
import math
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> Any:
    def unique(pairs: list) -> dict:
        result = {}
        for key, value in pairs:
            assert key not in result, (path, "duplicate key", key)
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique)


def exact(first: Any, second: Any) -> None:
    assert json.dumps(first, sort_keys=True, allow_nan=False) == json.dumps(
        second, sort_keys=True, allow_nan=False
    ), (first, second)


def write_json(path: Path, data: Any) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2, allow_nan=False)
        stream.write("\n")


def verify_inventory(root: Path, inventory: Path) -> int:
    entries = read_json(inventory)
    seen = set()
    for item in entries:
        target = (root / item["path"]).resolve()
        assert target.is_relative_to(root.resolve()) and target not in seen
        seen.add(target)
        assert target.stat().st_size == item["bytes"]
        assert digest(target) == item["sha256"], target
    return len(entries)


def score(cell: dict, policy: dict) -> dict:
    """Preserve conditional summaries; recompute only policy margins and gates."""
    result = copy.deepcopy(cell)
    assert cell["all_draws"] == policy["draws_per_base_cell"] == 1000
    assert cell["valid_rate"] == cell["accepted_count"] / cell["all_draws"]
    eligible = cell["ratio"] in policy["relative_qualified_ratios"]
    assert cell["relative_eligible"] is eligible
    assert (cell["relative"] is None) == (cell["ratio"] in (None, 0.0))
    margins = {"valid_rate": cell["valid_rate"] - policy["valid_rate_min"]}
    for coordinate in ("scale", "relative"):
        summary = cell[coordinate]
        if summary is None:
            margins[f"{coordinate}_median"] = None
            margins[f"{coordinate}_p90"] = None
        else:
            assert all(math.isfinite(value) for value in summary.values())
            margins[f"{coordinate}_median"] = policy[
                f"median_{coordinate}_abs_max"
            ] - abs(summary["median"])
            margins[f"{coordinate}_p90"] = (
                policy[f"p90_abs_{coordinate}_max"][str(cell["p"])]
                - summary["p90_absolute"]
            )
    result["margins"] = margins
    result["scale_pass"] = all(
        margins[key] >= 0 for key in ("valid_rate", "scale_median", "scale_p90")
    )
    result["relative_pass"] = (
        all(
            margins[key] >= 0
            for key in ("valid_rate", "relative_median", "relative_p90")
        )
        if eligible
        else None
    )
    result["individual_gate_pass"] = result["scale_pass"] and (
        not eligible or result["relative_pass"]
    )
    return result


def counts(cells: list[dict]) -> dict:
    baseline = [cell for cell in cells if cell["ratio"] is None]
    eligible = [cell for cell in cells if cell["relative_eligible"]]
    return {
        "accepted_quantiles": sum(cell["accepted_count"] for cell in cells),
        "baseline_cells": len(baseline),
        "baseline_scale_passed": sum(cell["scale_pass"] for cell in baseline),
        "all_cells": len(cells),
        "all_scale_passed": sum(cell["scale_pass"] for cell in cells),
        "eligible_cells": len(eligible),
        "eligible_scale_and_relative_passed": sum(
            cell["individual_gate_pass"] for cell in eligible
        ),
        "all_combined_passed": sum(cell["individual_gate_pass"] for cell in cells),
        "all_individual_gates_passed": all(
            cell["individual_gate_pass"] for cell in cells
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", required=True, type=Path, help="New, absent output directory"
    )
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    prior = here.parent / "gf15-lmoments-assessment"
    old_path = here.parent / "gf15/results/criteria.json"
    assert (
        digest(prior / "artifact-inventory.json")
        == "8d1acd62f132d332048e2cebf2d1be52809787c65b04cbca3496ec9872d72f2d"
    )
    assert (
        digest(prior / "signed-verdict.json")
        == "4580f25ddc7a1432735448a9976240c757c59d2ca3253ff5d162cbcadc0fe375"
    )
    assert (
        digest(here / "criteria.json")
        == "8f4a0e2fe3b9aca0dafd8cd885dab11a609dccaa62cd1dafcd175a8372ff3cb0"
    )
    old, new = read_json(old_path), read_json(here / "criteria.json")
    assert digest(old_path) == new["original_criteria_sha256"]
    changed = {key for key in old if old[key] != new[key]}
    assert changed == {
        "approval",
        "estimator",
        "scientific_claim_boundary",
        "median_scale_abs_max",
        "median_relative_abs_max",
        "p90_abs_scale_max",
        "p90_abs_relative_max",
    }
    assert set(new) - set(old) == {
        "policy_id",
        "accuracy_multiplier",
        "original_criteria_sha256",
    }
    for coordinate in ("scale", "relative"):
        exact(new[f"median_{coordinate}_abs_max"], 0.3)
        exact(new[f"p90_abs_{coordinate}_max"], {"0.9": 1.5, "0.5": 0.75})
    inventory_count = verify_inventory(prior, prior / "artifact-inventory.json")
    verify_inventory(prior / "results", prior / "results/artifact-inventory.json")
    signed = read_json(prior / "signed-verdict.json")
    for name, sha in signed["bindings"].items():
        assert digest(prior / name) == sha, name
    assert signed["mechanical_integrity"] == "complete_independent_audit_passed"
    assert signed["scientific_gate_conjunction"] is False
    inputs = [
        old_path,
        prior / "artifact-inventory.json",
        prior / "signed-verdict.json",
        prior / "results/individual-cells.json",
        prior / "results/translation-cells.json",
        prior / "results/audit-results.json",
    ]
    sources = [
        here / name
        for name in (
            "rescore.py",
            "check-rescore.py",
            "criteria.json",
            "README.md",
            "scientific-handoff.md",
        )
    ]
    sources.extend(sorted((here / "verification").rglob("*.*")))
    frozen = {str(path): digest(path) for path in inputs + sources}
    output = args.output.resolve()
    assert output.is_relative_to(Path.cwd().resolve())
    output.mkdir(parents=True, exist_ok=False)
    write_json(
        output / "source-freeze.json",
        {
            "frozen_utc": datetime.now(timezone.utc).isoformat(),
            "bindings": frozen,
            "python": sys.version,
            "executable": sys.executable,
            "platform": platform.platform(),
            "stage3_inventory_entries_verified": inventory_count,
        },
    )
    individual = read_json(prior / "results/individual-cells.json")
    audit = read_json(prior / "results/audit-results.json")
    translation = read_json(prior / "results/translation-cells.json")
    expected = set(
        itertools.product(
            new["shapes_scipy_c"],
            new["usable_counts"],
            new["probabilities"],
            [None, *new["ratios_true_quantile_over_generating_scale"]],
        )
    )
    assert set(individual) == {"A", "B", "C"}
    rescored, comparisons, failures = {}, {}, []
    for method, cells in individual.items():
        assert len(cells) == len(expected) == 144
        assert {
            (cell["shape_c"], cell["n"], cell["p"], cell["ratio"]) for cell in cells
        } == expected
        for cell in cells:
            exact(score(cell, old), cell)
        old_counts = counts(cells)
        for key, value in audit["individual_outcomes"][method].items():
            exact(old_counts[key], value)
        rescored[method] = [score(cell, new) for cell in cells]
        comparisons[method] = {
            "original": old_counts,
            "accuracy_3x": counts(rescored[method]),
        }
        for cell in rescored[method]:
            for criterion, margin in cell["margins"].items():
                if margin is None or (
                    criterion.startswith("relative") and not cell["relative_eligible"]
                ):
                    continue
                if margin < 0:
                    failures.append(
                        {
                            "method": method,
                            **{
                                key: cell[key] for key in ("shape_c", "n", "p", "ratio")
                            },
                            "criterion": criterion,
                            "passing_margin": margin,
                            "excess_over_limit": -margin,
                            "failure_class": "scale_or_validity"
                            if not cell["scale_pass"]
                            else "relative_only",
                        }
                    )
    assert len(translation["cells"]) == 120
    assert {
        (cell["shape_c"], cell["n"], cell["p"], cell["ratio"])
        for cell in translation["cells"]
    } == {key for key in expected if key[3] is not None}
    for cell in translation["cells"]:
        assert cell["acceptance_unchanged"] is True and cell["translation_pass"] is True
        assert (
            cell["numerical_failures"] == 0
            and cell["numerical_passes"] == cell["all_draws"] == 1000
        )
    exact(audit["translation"], signed["translation"])
    assert (
        audit["translation"]["max_absolute_delta_scale_error"]
        <= new["translation_paired_abs_max"]
    )
    groups = {}
    for dimension in ("shape_c", "n", "p", "ratio"):
        groups[dimension] = [
            {
                "value": value,
                **{
                    method: counts([cell for cell in cells if cell[dimension] == value])
                    for method, cells in rescored.items()
                },
            }
            for value in dict.fromkeys(cell[dimension] for cell in rescored["C"])
        ]
    summary = {
        "policy_id": new["policy_id"],
        "counts": comparisons,
        "by_regime": groups,
        "n18": {
            method: counts([cell for cell in cells if cell["n"] == 18])
            for method, cells in rescored.items()
        },
        "translation_unchanged": audit["translation"],
        "scientific_gate_conjunction": all(
            cell["individual_gate_pass"] for cell in rescored["C"]
        )
        and all(cell["translation_pass"] for cell in translation["cells"]),
        "new_fits": 0,
    }
    write_json(output / "individual-cells.json", rescored)
    write_json(output / "failures.json", failures)
    write_json(output / "summary.json", summary)
    write_json(output / "translation-cells.json", translation)
    for path, sha in frozen.items():
        assert digest(Path(path)) == sha, path
    verify_inventory(prior, prior / "artifact-inventory.json")
    bindings = {path.name: digest(path) for path in sorted(output.iterdir())}
    write_json(
        output / "signed-verdict.json",
        {
            "signed_by": "model-validator /root/model_validator_gf15_3x",
            "signed_utc": datetime.now(timezone.utc).isoformat(),
            "policy_id": new["policy_id"],
            "mechanical_integrity": "signed_input_bindings_and_original_decisions_verified",
            "scientific_gate_conjunction": summary["scientific_gate_conjunction"],
            "verdict": "passes_relaxed_fixed_matrix_policy"
            if summary["scientific_gate_conjunction"]
            else "fails_relaxed_fixed_matrix_policy",
            "original_verdict_preserved": True,
            "scope": "Owner-selected post-results policy re-score of signed summaries; not independent out-of-sample validation",
            "new_fits": 0,
            "production_integration_authorized": False,
            "screening_change_authorized": False,
            "r12_seal_authorized": False,
            "bindings": bindings,
            "source_and_input_bindings": frozen,
        },
    )
    write_json(
        output / "artifact-inventory.json",
        [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": digest(path)}
            for path in sorted(output.iterdir())
        ],
    )
    print(
        json.dumps(
            {
                "counts": comparisons,
                "C_n18": summary["n18"]["C"],
                "scientific_gate_conjunction": summary["scientific_gate_conjunction"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
