# P2 adapter-backed collection lifecycle — 2026-09-11

Lifecycle: append-only execution evidence.

## Scope and result

Continuation from `6022f330` adds `scenario_collection.py`, without changing any
WF3 call site, workflow configuration or scientific operation. This is storage
infrastructure for the existing stochastic schema. It does not claim a production
ready collection or GF-31 acceptance.

- Fresh collection directories are claimed exclusively. Partial and ready roots
  both refuse initialization; ready reuse has its own read-only API. The claim is
  an in-process handle, not persisted attempt/resume machinery.
- Payloads use exclusive creation. Publication validates retained state before
  same-directory temporary-file flush/fsync and atomic ready-marker replacement.
  Repeated publication of identical ready state preserves bytes and mtimes.
- Consumer validation recomputes identities and document/file hashes, checks
  stochastic table completeness/pairing/order/width, WG-2 lookup shape, exact
  forcing coverage, preparation catalog/ancillary closure and descriptor equality.
  Forcing and ancillary descriptor readers are mandatory adapter dependencies.
- Producer reuse additionally checks the exact planned intent and current source,
  repository-code and environment inputs. Removing original source/code files
  does not prevent consumer reads of the already published collection.
- All artifacts remain durable. Accounting covers every retained file and byte;
  this increment implements no deletion operation or retention cap.

## Representation choices for the source planner

The accepted design leaves subordinate document shapes to implementation. The
first storage binding uses these explicit shapes (all canonical JSON):

| Document | Stored representation |
|---|---|
| Generation config | Scientific projection containing `seed: {requested, resolved}` and `unit_id_capacity`; top-level `compute` and `console` refuse |
| Source inventory | Array sorted by `(role, path)`; each entry has `role`, `path` (original locator), `size_bytes`, `sha256`, `metadata` |
| Provider code inventory | Array sorted by repository-relative `path`; each entry has `path`, `sha256` |
| Environment | `packages` mapping of names to immutable revisions and `locks` mapping of names to SHA-256 |
| Preparation context | Accepted `forcing-preparation/1` fields; ancillary entries carry `id`, `role`, `path`, `size_bytes`, `sha256`, `descriptor`; forcing elevation links `catalog_key` to `artifact_id` |

The catalog validator checks the current preparation binding's executable subset:
`RasterDataset` / `raster_xarray`, `chunks`, `lock`, optional `harmonise_dims` or
`round_latlon` preprocessing, and `rename`/`unit_mult`/`unit_add` adapters. These
cover the current generated-reader and ERA5/E-OBS/CHIRPS elevation settings
inspected in repository code/catalogs. Unknown executable options explicitly
refuse; future bindings must establish their closure before expanding this set.
Descriptive metadata is preserved verbatim. Catalog YAML is parsed directly with
duplicate-key refusal; no HydroMT serialization round-trip strips preprocessing.

This is not the production extraction of these settings. A real source planner
must resolve all actual inputs, preserve their byte and catalog semantics, retain
unit-interpretation evidence, and prove every supported branch against GF-31.

## Synthetic publication example

The successful test collection retained **13 files / 4,987 bytes**. Its two
forcing payloads are JSON-based test doubles named `.nc`, not model forcing.
The test recreates the full example in `tests/test_scenario_collection.py`.

```json
{
  "schema_version": "scenario-collection/1",
  "status": "ready",
  "collection_id": "9da02aa9c82b81a303d92cbdcb5ae058920dedb526dede94dbef59511af768c1",
  "collection_revision": "e17e90567e5f7a3aa68fe0d9369ca5096611a209880c127217f3270c4a4dc910",
  "intent_path": "collection_intent.json",
  "intent_sha256": "88c4e70b33b0f8df99df59dfeac27c8400356b976f0512ac781886b892d34fbe"
}
```

This excerpt omits the table, preparation and forcing inventories for readability;
it is not itself a complete ready manifest. The fixture includes both `01` and
`02`, their descriptors, the lookup and the packaged elevation artifact.

## Checks and review

Verification posture: rapid / numerical unaffected. New behavioral coverage is
warranted by the persistence, immutability and path contracts; the test budget
exceeds the default to exercise independently rehashed defects and failure
retention. Caller search finds only test callers for the new collection APIs.

| Command | Result |
|---|---|
| `pixi run --as-is pytest tests/test_content_identity.py tests/test_scenario_rows.py -q` | Re-entry: 57 passed |
| `pixi run --as-is pytest tests/test_scenario_collection.py -q` before implementation | Expected missing-module failure |
| Expanded preparation/marker tests before fixes | Reproduced external marker symlink acceptance |
| Review regression subset before fixes | Reproduced eight failures: driver shape/options, inert metadata and reserved marker aliases |
| `pixi run --as-is pytest tests/test_content_identity.py -q -k windows_alias` before fixes | Five failures reproduced trailing-dot/space and device-name acceptance |
| `pixi run --as-is pytest tests/test_content_identity.py tests/test_scenario_collection.py tests/test_scenario_rows.py tests/test_scenario_provider.py -q --basetemp .tmp/scratchpad/2026-09-11_0010/pytest-combined` | Final: 112 passed, no skips, 21.33 s |
| `pixi run --as-is lint` | Passed |
| `pixi run --as-is format-check` | Passed; 313 files formatted |
| `pixi run --as-is python -m py_compile blueearth_cst/experiment/content_identity.py blueearth_cst/experiment/scenario_collection.py tests/test_content_identity.py tests/test_scenario_collection.py` | Passed |

The named Python-engineer read-only review first requested changes for reserved
marker aliases and permissive driver validation. After fixes and discriminating
tests, it returned PASS for this infrastructure scope. It did not run tests or
provide scientific acceptance. Raw output remains disposable session scratch.

No CLI, full-suite, real model, baseline or GF-31 run was needed for unused
storage APIs. GF-17/GF-23 now have partial synthetic evidence, not full phase
acceptance. Remaining work is real descriptor/preparation binding and its named
scientific handoff, source planning/resolution, reference-aware deletion and
current-WF3 integration, followed by response and metric-set persistence.
