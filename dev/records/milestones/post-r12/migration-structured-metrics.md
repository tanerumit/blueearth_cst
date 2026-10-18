# Structured metric sets and historical inspection

New WF4 metric publications use `metric-set/5` and `metric-set-identity/5`. The result table columns,
units, grouping, native missingness, water-year selection and production reductions remain unchanged.
The manifest adds a saved execution request and metric definition for numerical eligibility checks.
Old `/3` and `/4` publications remain readable; no in-place migration rewrites their bytes.

Calculation implementations now live in the independent `blueearth_cst.metrics` module. Moved or
changed source bytes legitimately change content-derived implementation revisions and metric-set IDs.
Scientific equivalence does not imply identity equality. Existing declarative definitions, authored
aliases, legacy selection and immutable publications retain their compatibility adapters.

A local authored calculation includes `calculation.set`, `method` and explicit `parameters`.
Its identity is `<trusted-set>:<authored-metric>`; its legacy equivalent is empty. YAML remains data,
with no arbitrary Python imports. `selection.registry` expands the selected trusted set's declarations.
The default selection still expands the existing suite. The five-period flood example remains opt-in;
the unchanged production qualification gate refuses probabilities outside the shipped evidence.

`scripts/inspect_metrics.py` separates saved-artifact integrity, historical check evidence and fresh
numerical rechecking. Integrity-only inspection can succeed without original inputs or current
registries. Old publications lacking complete execution provenance are conservatively ineligible
for numerical rechecking. Strict readers and new-calculation cache validity remain unchanged.

Independent checker sources are excluded from execution identity. Fresh verification receipts bind
the checker hashes and runtime to the exact immutable manifest; checker changes cannot inherit a
previous check's attribution. Receipts do not establish authenticity against coordinated tampering.

The misleading internal `rolling7_annual_min` selector has an explicit legacy compatibility alias.
New local declarations use `rolling_annual_min`. Daily retained input counts and usable annual fit
block counts remain distinct quantities; existing export columns retain their names.
