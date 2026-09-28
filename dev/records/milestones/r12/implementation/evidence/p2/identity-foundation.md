# P2 collection identity foundation — 2026-09-10

Lifecycle: append-only execution evidence.

## Scope and outcome

Starting from accepted P1 at `3b3d5319`, the owner's instruction to continue
R12 released this P2 increment. `main` was already ancestral and the worktree
was clean. `content_identity.py` now implements the accepted §8.2 equations,
without production call-site changes or scientific output changes.

- Canonical JSON is plain UTF-8 with sorted keys, preserved array order, compact
  separators and final LF. Finite floats use Python JSON spelling, pinned by a
  byte vector including `1.0`, `-0.0`, and `1e-07`. Non-string keys, unsupported
  types, nonfinite numbers, duplicate persisted keys and noncanonical bytes refuse.
- Semantic hashing strips only `run_id`; ancestry and ordered payloads remain.
- Intent hashing covers every term of the accepted equation; revision hashing
  covers the produced inventory and descriptors. Audit timestamps and each
  identity's self-field do not enter their respective projections.
- Confined paths resolve from the collection root and reject lexical or resolved
  escapes, including symlinks. No file is written by these helpers.

Existing `shared.provenance.canonical_sha256` intentionally remains unchanged:
its type-tagged encoding differs from collection-canon/1. Complete schema,
scenario consistency, inventory ordering, bytes and physical descriptors remain
the responsibility of the forthcoming collection validator.

## Verification

Verification posture: rapid / numerical unaffected. The default test budget was
exceeded to cover the explicit new persistence-format and identity-invalidation
contracts. Repository-required lint and formatting were also run. New helpers
have only test callers; no workflow, shared helper, rule signature or config changed.

| Command | Result |
|---|---|
| `pixi run --as-is pytest tests/test_scenario_rows.py tests/test_scenario_provider.py -q` | Re-entry: 16 passed |
| `pixi run --as-is pytest tests/test_content_identity.py -q` before implementation | Expected collection failure: module did not exist |
| `pixi run --as-is pytest tests/test_content_identity.py tests/test_scenario_rows.py tests/test_scenario_provider.py -q` | Final: 60 passed, no skips, 4.17 s |
| `pixi run --as-is lint` | Passed |
| `pixi run --as-is format-check` | Passed; 311 files formatted |
| `pixi run --as-is python -m py_compile blueearth_cst/experiment/content_identity.py tests/test_content_identity.py` | Passed |

Read-only named Python-engineer review checked the implemented projections,
canonical decoder and confinement against §8.2 and reported no actionable defects.
It made no scientific acceptance claim. Raw local output is disposable scratch
under `.tmp/scratchpad/2026-09-10_2310/`; commands and results above are retained.
The restricted shell lacked Pixi on PATH; checks used the existing host Pixi
environment with `--as-is`, without installation or lock changes.

## Remaining P2 work

No production manifest example, retained-byte accounting, publication/reuse
trace, or model-validator acceptance exists for this increment. GF persistence
gates remain open. Next implement exclusive collection initialization, immutable
publication and complete validation; bind portable preparation and source
planning before production publication. Then persist simulation responses and
metric sets and prove metrics-only and the required single-invocation mechanisms.
CLI/full-suite/model/baseline runs were not repeated for these unused pure helpers.
