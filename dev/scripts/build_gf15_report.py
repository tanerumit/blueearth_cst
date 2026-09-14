"""Package the frozen GF15 8x benchmark into the shipped report asset.

This is a repository maintenance tool, not part of any run: nothing under
`blueearth_cst/` or `scripts/` imports it, and the shipped loader only ever
reads the asset it writes. It exists so
`blueearth_cst/experiment/data/gf15-accuracy-8x-v1.json` is reproducible from
the frozen evidence rather than being a hand-assembled blob.

Every hash it writes is computed from the evidence bytes and then checked
against the hashes the frozen records already carry (accepted design D5:
"Compute actual hashes during packaging and check frozen inventories; none is
invented here"). A disagreement is a hard failure -- the point is to catch drift
in the evidence archive, so a generator that simply concatenated what it read
would be worthless.

Usage, from the repository root:

    python dev/scripts/build_gf15_report.py            # write the asset
    python dev/scripts/build_gf15_report.py --check    # verify, write nothing
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from blueearth_cst.experiment.content_identity import (  # noqa: E402
    canonical_json_bytes,
)

EVIDENCE = REPO / "dev/milestones/r12/implementation/evidence"
ACCURACY = EVIDENCE / "gf15-accuracy-8x"
READINESS = EVIDENCE / "gf15-lmoments-readiness"
ASSET = REPO / "blueearth_cst/experiment/data/gf15-accuracy-8x-v1.json"

SCHEMA_VERSION = "gf15-benchmark-report/1"
ESTIMATOR_ID = "gf15-lmoments-c/1"
POLICY_ID = "gf15-accuracy-8x-v1"

# D7's pinned dependency identity. Repeated here so packaging fails loudly if the
# frozen environment record ever disagrees with the design.
WHEEL_SHA256 = "984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e"
SOURCE_SHA256 = {
    "__init__.py": "1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2",
    "distr.py": "f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee",
}

# D5's embedded set, as repository-relative paths.
EMBEDDED = (
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/criteria.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/README.md",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/scientific-handoff.md",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/individual-cells.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/translation-cells.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/summary.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/failures.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/source-freeze.json",
    "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results/signed-verdict.json",
    "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/effective-environment.json",
    "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/independent/signed-verdict.json",
    "dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/results/independent/scientific-handoff.md",
)

LIMITATIONS = (
    "The 8x limits were selected by the owner after the original and 3x results "
    "were observed, and were re-scored on that same retained development data. "
    "This is a post-results development rescore, not independent validation.",
    "The tested domain is synthetic IID block fixtures. They do not simulate "
    "block extraction, temporal dependence, or real discharge, and no real "
    "bundle may be assigned to a domain cell from its fitted shape, scale, "
    "count or discharge ratio.",
    "The screening policy (ratio 1.0, floor 10) is carried unchanged and is NOT "
    "validated by this benchmark; its status remains provisional_operational.",
    "Estimates are point estimates. No fit interval, estimator-noise bound or "
    "uncertainty quantification is established (accepted limitation domain-7).",
    "Relative error is undefined where the true quantile is zero; the 0.05 "
    "ratio is diagnostic only and is not part of the qualified relative cohort.",
    "Applicability to an actual scenario bundle is unestablished, and no claim "
    "of better real-system accuracy than the predecessor estimator follows.",
    "The report is self-contained for inspecting the verdict and thresholds. It "
    "is not a raw-data rerun archive: raw samples, individual fits, the full "
    "control programs and the wheels remain in the frozen evidence archives.",
    "signed_by records retained reviewer attribution. It is not a public-key "
    "signature and verifies no identity.",
)


class PackagingError(RuntimeError):
    """The frozen evidence does not support the report this tool would write."""


def _read(relative: str) -> tuple[bytes, str]:
    path = REPO / relative
    if not path.is_file():
        raise PackagingError(f"missing frozen evidence: {relative}")
    data = path.read_bytes()
    return data, hashlib.sha256(data).hexdigest()


def _repo_relative(recorded: str) -> str | None:
    """Reduce a historical absolute path to its repository-relative tail.

    This is textual normalization, never resolution: D5 keeps the absolute paths
    inside frozen records documentary, and none of them is opened. Anything that
    does not carry a recognisable evidence tail is left unclaimed rather than
    guessed at.
    """
    text = recorded.replace("\\", "/")
    marker = "dev/milestones/"
    index = text.find(marker)
    return text[index:] if index >= 0 else None


def _checked(relative: str, expected: dict[str, str]) -> dict:
    """Embed one source, refusing any file the frozen records do not vouch for."""
    data, digest = _read(relative)
    if relative in expected and expected[relative] != digest:
        raise PackagingError(
            f"{relative}: computed {digest} but frozen records carry {expected[relative]}"
        )
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise PackagingError(f"{relative}: not valid UTF-8") from error
    return {"source_path": relative, "sha256": digest, "text": text}


def _frozen_expectations() -> dict[str, str]:
    """Collect every hash the frozen records assert, keyed by repository path.

    Three independent records are merged -- the results inventory, the signed
    verdict's bindings, and the source freeze -- so a file vouched for by more
    than one must agree with all of them. Keys are repository-relative paths, not
    bare file names: the 3x and 8x archives both contain an `individual-cells.json`
    and they are different files, so a name-keyed merge reports a spurious
    conflict between two correct records.
    """
    expected: dict[str, str] = {}
    results = "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x/results"

    def claim(path: str | None, digest: str, origin: str) -> None:
        if path is None:
            return
        if path in expected and expected[path] != digest:
            raise PackagingError(
                f"frozen records disagree about {path}: "
                f"{expected[path]} versus {digest} from {origin}"
            )
        expected[path] = digest

    inventory = json.loads(
        (ACCURACY / "results/artifact-inventory.json").read_text("utf-8")
    )
    for entry in inventory:
        claim(
            f"{results}/{entry['path']}",
            entry["sha256"],
            "results/artifact-inventory.json",
        )

    verdict = json.loads((ACCURACY / "results/signed-verdict.json").read_text("utf-8"))
    for name, digest in verdict["bindings"].items():
        claim(f"{results}/{name}", digest, "signed-verdict.json bindings")
    for path, digest in verdict["source_and_input_bindings"].items():
        claim(_repo_relative(path), digest, "signed-verdict.json sources")

    freeze = json.loads((ACCURACY / "results/source-freeze.json").read_text("utf-8"))
    for path, digest in freeze["bindings"].items():
        claim(_repo_relative(path), digest, "source-freeze.json")

    return expected


def build_report() -> dict:
    expected = _frozen_expectations()

    criteria = json.loads((ACCURACY / "criteria.json").read_text("utf-8"))
    summary = json.loads((ACCURACY / "results/summary.json").read_text("utf-8"))
    individual = json.loads(
        (ACCURACY / "results/individual-cells.json").read_text("utf-8")
    )
    translation = json.loads(
        (ACCURACY / "results/translation-cells.json").read_text("utf-8")
    )
    failures = json.loads((ACCURACY / "results/failures.json").read_text("utf-8"))
    verdict = json.loads((ACCURACY / "results/signed-verdict.json").read_text("utf-8"))
    freeze = json.loads((ACCURACY / "results/source-freeze.json").read_text("utf-8"))
    environment = json.loads(
        (READINESS / "environment/effective-environment.json").read_text("utf-8")
    )
    attempt = json.loads((READINESS / "results/attempt.json").read_text("utf-8"))
    completion = json.loads((READINESS / "results/completion.json").read_text("utf-8"))
    independent = json.loads(
        (READINESS / "results/independent/signed-verdict.json").read_text("utf-8")
    )

    if criteria["policy_id"] != POLICY_ID:
        raise PackagingError(f"criteria policy_id is {criteria['policy_id']!r}")
    if verdict["policy_id"] != POLICY_ID or summary["policy_id"] != POLICY_ID:
        raise PackagingError("verdict or summary policy_id differs from the criteria")
    if not verdict["scientific_gate_conjunction"] or verdict["new_fits"] != 0:
        raise PackagingError(
            "signed verdict does not carry a zero-new-fit passing gate"
        )
    if summary["scientific_gate_conjunction"] != verdict["scientific_gate_conjunction"]:
        raise PackagingError("summary and verdict disagree about the gate")

    counts = summary["counts"]["C"]
    if not counts["accuracy_8x"]["all_individual_gates_passed"]:
        raise PackagingError("candidate C does not pass the 8x individual gates")
    if counts["original"]["all_individual_gates_passed"]:
        raise PackagingError("original failures must be preserved, not erased")
    if counts["accuracy_3x"]["all_individual_gates_passed"]:
        raise PackagingError("threefold failures must be preserved, not erased")

    # Hashes the packaged report asserts are cross-checked against the freeze.
    original_digest = criteria["original_criteria_sha256"]
    if not any(
        (_repo_relative(path) or "").endswith("evidence/gf15/results/criteria.json")
        and digest == original_digest
        for path, digest in freeze["bindings"].items()
    ):
        raise PackagingError(
            "criteria.original_criteria_sha256 is not vouched for by the source freeze"
        )

    lmoments = environment.get("lmoments3_sources") or environment.get("sources") or {}
    observed = {name: lmoments[name] for name in SOURCE_SHA256 if name in lmoments}
    if observed and observed != {
        k: v for k, v in SOURCE_SHA256.items() if k in observed
    }:
        raise PackagingError(
            f"frozen environment source hashes differ from D7: {observed}"
        )

    embedded = [_checked(relative, expected) for relative in EMBEDDED]
    # Keyed by full path: two different files in this set are named
    # signed-verdict.json and two are named scientific-handoff.md.
    by_path = {item["source_path"]: item for item in embedded}

    # D5 requires the structured duplicates to agree with the embedded raw text.
    accuracy = "dev/milestones/r12/implementation/evidence/gf15-accuracy-8x"
    for relative, structured in (
        (f"{accuracy}/criteria.json", criteria),
        (f"{accuracy}/results/summary.json", summary),
        (f"{accuracy}/results/individual-cells.json", individual),
        (f"{accuracy}/results/translation-cells.json", translation),
        (f"{accuracy}/results/failures.json", failures),
        (f"{accuracy}/results/signed-verdict.json", verdict),
    ):
        if json.loads(by_path[relative]["text"]) != structured:
            raise PackagingError(
                f"packaged {relative} differs from its embedded source"
            )

    return {
        "schema_version": SCHEMA_VERSION,
        "estimator_id": ESTIMATOR_ID,
        "policy_id": POLICY_ID,
        "method": {
            "name": "Range-normalized sample L-moment GEV (candidate C)",
            "normalization": "a=min(x); s=max(x)-a; y=(x-a)/s",
            "moments": "lmoments3.lmom_ratios(y, nmom=3) once, for l1, l2, t3",
            "inversion": "lmoments3.distr.gev.lmom_fit(lmom_ratios=[l1,l2,t3]) once",
            "mapping": "c=c_y; loc=a+s*loc_y; scale=s*scale_y",
            "quantile": criteria["quantile_formula"],
            "shape_convention": criteria["extreme_value_shape_xi"],
            "pinned_behaviour": (
                "19 updates, relative shape tolerance 1e-6, positive-t3 branch "
                "Gumbel snap abs(c)<1e-5, Euler constant 0.57721566; no "
                "replacement root solver, retry, fallback or shrinkage"
            ),
            "domain": "finite-mean L-moment domain c>-1",
        },
        "dependency": {
            "package": "lmoments3",
            "version": "1.0.8",
            "wheel_sha256": WHEEL_SHA256,
            "source_sha256": dict(sorted(SOURCE_SHA256.items())),
        },
        "environment": {
            "python": environment.get("python"),
            "platform": environment.get("platform"),
            "packages": environment.get("packages"),
            "note": (
                "The benchmark environment is the isolated readiness venv. It is "
                "the environment the numbers were produced in, not a claim about "
                "any environment the estimator later runs in."
            ),
        },
        "readiness_attempt": {
            "utc": attempt["utc"],
            "python": attempt["python"],
            "source_sha256": attempt["source"],
            "environment_inventory_sha256": attempt.get("environment_inventory_sha256"),
            "attempt_sha256": completion["attempt_sha256"],
            "status": completion["status"],
            "independent_verdict": {
                "signed_by": independent.get("signed_by"),
                "verdict": independent.get("verdict"),
            },
        },
        "rng": {
            "recipe": criteria["rng"],
            "master_seed": criteria["master_seed"],
            "sample_generation": criteria["sample_generation"],
            "generating_scale": criteria["generating_scale"],
            "standardized_location": criteria["standardized_location"],
            "translated_location": criteria["translated_location"],
        },
        "tested_domain": {
            "shapes_c": criteria["shapes_scipy_c"],
            "counts": criteria["usable_counts"],
            "probabilities": criteria["probabilities"],
            "ratios": criteria["ratios_true_quantile_over_generating_scale"],
            "relative_qualified_ratios": criteria["relative_qualified_ratios"],
            "draws_per_base_cell": criteria["draws_per_base_cell"],
            "base_cells": criteria["base_cells"],
            "total_fits": criteria["total_fits"],
            "total_quantile_rows": criteria["total_quantile_rows"],
        },
        "criteria": criteria,
        "original_criteria_sha256": original_digest,
        "counts": summary["counts"],
        "results": {
            "individual_cells": individual,
            "translation_cells": translation,
            "summary": summary,
            "failures": failures,
        },
        "verdict": verdict,
        "inventory_anchors": {
            "results": json.loads(
                (ACCURACY / "results/artifact-inventory.json").read_text("utf-8")
            ),
            "source_freeze_entries_verified": freeze[
                "stage3_inventory_entries_verified"
            ],
            "boundary": (
                "Raw samples, individual fits, control programs and wheels are NOT "
                "embedded here; they remain in the frozen evidence archives these "
                "anchors name."
            ),
        },
        "limitations": list(LIMITATIONS),
        "embedded_sources": embedded,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify the committed asset reproduces, writing nothing",
    )
    args = parser.parse_args(argv)

    payload = canonical_json_bytes(build_report())
    digest = hashlib.sha256(payload).hexdigest()

    if args.check:
        if not ASSET.is_file():
            print(f"MISSING {ASSET.relative_to(REPO).as_posix()}")
            return 1
        current = ASSET.read_bytes()
        if current != payload:
            print(
                f"DIFFERS {ASSET.relative_to(REPO).as_posix()}: "
                f"committed {hashlib.sha256(current).hexdigest()}, rebuilt {digest}"
            )
            return 1
        print(f"OK {ASSET.relative_to(REPO).as_posix()} sha256={digest}")
        return 0

    ASSET.parent.mkdir(parents=True, exist_ok=True)
    ASSET.write_bytes(payload)
    print(
        f"wrote {ASSET.relative_to(REPO).as_posix()} bytes={len(payload)} sha256={digest}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
