# Session-2 landing evidence

Verified on 2026-10-09 for `chore/tmp-cleanup`, synchronized with local `main` at `e66358d0`.
Final executable candidate: `5f8a345a`; environment: Windows 11, Python 3.12.13, Pixi default.
Lock SHA256: `797afdad5a8f8c37dd62b2f1e2f88f3fea120c3fc53b7e7c792b860700a6782b`.

The batch improves disabled-workflow feedback and retires a removed scratch pointer. Landing found
that the invocation-history dry-run test supplied a nonexistent config despite the new parent-side
enabled check. Its fixture now supplies an enabled config; all nonproductive-attempt assertions remain.

| Command | Result |
|---|---|
| `pixi run lint` | Passed |
| `pixi run format-check` | Passed |
| `pixi run pytest tests/test_invocation_history.py -q` | 6 passed |
| `pixi run test-full` | 4,092 passed, 17 optional skips, 1 expected failure |
| `pixi run test-e2e` | 1 passed, no skips; all five workflows executed |

The full-suite skips concern optional local parity fixtures and the separately executed integration
test. The expected failure pins the known HydroMT catalog serialization workaround. No numerical
algorithms or figure styles changed, so baseline comparison and additional visual gates were not owed.

The E2E case used the rapid config set in a fresh pytest-owned root, with production readers checking
historical stores, projection factors, scenario collections, simulations and metric sets. Output root:
`C:/Users/taner/AppData/Local/Temp/pytest-of-taner/pytest-4761/test_all_five_workflows_run_en0/project`.
These outputs are disposable and are not a retained dataset.

E2E started on `76ba2e35d47b165f42139b3b06bb8c3dda153c84`. Its recorder refused candidate drift
after the fixture-only commit. Reuse was explicitly checked against that original candidate: the sole
changed path was `tests/test_invocation_history.py`; all runtime code, configuration, lock identity
and E2E test source were unchanged. The corrected full suite passed on `5f8a345a`.
Passed E2E log SHA256: `46b51c9a1c11a827eae6b1c8e051e0a6a449714230bcb3fe991782e237c82088`.

`verify_landing.py` recorded the final full-suite pass and a separate `test-e2e-reuse` attestation.
Landing verified both records before merging; tree equality and ancestry were proved for `5f8a345a`.
Raw landing logs and JSON were removed at task closure after recording the checks here; this note
retains the durable result. Earlier sandbox attempts failed on Windows temporary-directory access,
and the first unrestricted full suite exposed the now-corrected fixture failure.
