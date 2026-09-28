"""Bounded boundary and mutation checks for the accuracy-policy reducer."""

import copy
import runpy
from pathlib import Path


def main() -> None:
    module = runpy.run_path(str(Path(__file__).with_name("rescore.py")))
    score = module["score"]
    policy = module["read_json"](Path(__file__).with_name("criteria.json"))
    cell = {
        "shape_c": 0.0,
        "n": 18,
        "p": 0.5,
        "ratio": 0.5,
        "all_draws": 1000,
        "accepted_count": 950,
        "valid_rate": 0.95,
        "scale": {"median": -0.80, "median_absolute": 0.4, "p90_absolute": 2.00},
        "relative": {"median": 0.80, "median_absolute": 0.4, "p90_absolute": 2.00},
        "relative_eligible": True,
    }
    assert score(cell, policy)["individual_gate_pass"]
    upper = copy.deepcopy(cell)
    upper["p"] = 0.9
    for coordinate in ("scale", "relative"):
        upper[coordinate]["p90_absolute"] = 4.00
    assert score(upper, policy)["individual_gate_pass"]
    upper["relative"]["p90_absolute"] = 4.0000000001
    assert not score(upper, policy)["individual_gate_pass"]
    for field, value in [("median", -0.8000000001), ("p90_absolute", 2.0000000001)]:
        for coordinate in ("scale", "relative"):
            wrong = copy.deepcopy(cell)
            wrong[coordinate][field] = value
            assert not score(wrong, policy)["individual_gate_pass"]
    wrong = copy.deepcopy(cell)
    wrong.update(accepted_count=949, valid_rate=0.949)
    assert not score(wrong, policy)["individual_gate_pass"]
    for ratio, eligible in [
        (None, False),
        (0.0, False),
        (0.05, False),
        (2.0, True),
        (10.0, True),
    ]:
        changed = copy.deepcopy(cell)
        changed.update(ratio=ratio, relative_eligible=eligible)
        changed["relative"] = None if ratio in (None, 0.0) else changed["relative"]
        assert score(changed, policy)["relative_pass"] is (True if eligible else None)
    wrong = copy.deepcopy(cell)
    wrong["relative_eligible"] = False
    try:
        score(wrong, policy)
    except AssertionError:
        pass
    else:
        raise AssertionError("wrong eligible cohort was accepted")
    print(
        "PASS: inclusive bias/P90/rate boundaries; over-limit and 949 failures; rho eligibility/nulls"
    )


if __name__ == "__main__":
    main()
