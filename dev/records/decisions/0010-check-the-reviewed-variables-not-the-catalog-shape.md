# ADR 0010 — Check the reviewed variables, not the catalog's shape

- **Status:** accepted
- **Date:** 2026-09-17
- **Supersedes:** the exact-equality form of `resolved_unit_interpretation`, not
  the binding it checks. `dev/milestones/r12/implementation/evidence/p1-forcing-units.md`
  stands unamended; this decision changes how that record is enforced, not what
  it established.

### Context

`resolved_unit_interpretation`
(`blueearth_cst/climate_analysis/prepare_climate_data_catalog.py`) is the gate
between a data catalog and the weather generator. It exists because the seven
forcing variables reach weathergenr already converted, carrying stale native
unit labels — the values are right and the attributes lie, so nothing
downstream can re-derive the arithmetic from the data. P1 established that
arithmetic by inspecting the executed path and witnessing it through the public
`RasterDatasetAdapter.transform`, and the guard's job is to refuse any catalog
the review did not cover.

It implemented that as **exact dict equality** over the adapter's `unit_add`,
`unit_mult` and `rename`. That is stricter than the property P1 established.
P1's subject is seven variables — `precip`, `temp`, `temp_min`, `temp_max`,
`press_msl`, `kin`, `kout` — and its witness table asserts the configured
arithmetic for those seven and nothing else. Equality additionally requires that
the catalog entry describe *no other variable*, which P1 never claimed and which
is not a property of the forcing at all.

The gap is not hypothetical. hydromt's own predefined `deltares_data` catalog —
the upstream Deltares publishes and the one a project reads when it takes its
data from the network store rather than a local copy — states the identical
seven conversions and additionally describes dewpoint (`d2m`), the two 10 m wind
components (`u10`, `v10`) and net shortwave radiation (`ssr`). None is read by
this toolbox. The guard refused it, and a project pointed at it failed at WF3
rule 3.04 with `UnverifiedForcingUnits` — a message that names an arithmetic
difference where there was none. Found by the external test case
`gabon-ntoum-deltares`, whose whole subject is reading from the network store.

So the guard had become a version pin on one catalog file. Any upstream revision
that adds a variable would be refused, and the failure would read as a numeric
problem rather than a shape one.

### Decision

Check the reviewed variables. An adapter departs from the reviewed binding when,
and only when, one of these holds:

1. a reviewed conversion is missing, or has a different value;
2. it converts a reviewed variable the review left unconverted — an extra
   `unit_add` or `unit_mult` entry keyed on one of the seven, such as a
   `unit_mult: {precip: 1000}` that would silently rescale precipitation;
3. it renames some other native variable **onto** a reviewed name, which would
   shadow the reviewed source of that variable.

Anything else the catalog describes is surplus and is ignored.

Clauses 2 and 3 are what keep this a check rather than a relaxation: the set
being reasoned about is the seven post-rename names, so every route by which a
catalog could reach a reviewed variable is still covered. What is no longer
covered is the catalog's size, which was never evidence about the forcing.

**The CHIRPS branch keeps exact equality.** Its assertion is that precipitation
carries the time shift and *no scaling at all*, and `unit_mult` being empty is
the substance of that claim rather than an incidental shape. Loosening it would
discard the assertion.

`UnitInterpretation.revision` moves to
`daily-catalog-hydromt1.3.1-weathergenr2.0.0/2`. The values it describes are
unchanged; the revision moves because the retained provenance must distinguish a
run whose catalog was admitted under the new rule.

### Consequences

- A project may read the Deltares network store through hydromt's published
  `deltares_data` catalog, which is what `gabon-ntoum-deltares` exercises.
- The guard survives an upstream catalog revision that adds variables, and still
  fails one that touches the seven.
- No number moves. Every catalog accepted before is still accepted, with
  identical arithmetic; the reviewed conversions are asserted exactly as before.
  Re-recording the baseline is therefore not required — but a run's retained
  `revision` string changes, which is deliberate and is the only observable
  difference in an existing project's outputs.
- `tests/test_prepare_climate_data_catalog.py` pins both halves: surplus
  variables accepted, and each of the three departure routes refused.

### Alternatives considered

**Leave the guard; carry a trimmed catalog per project.** Rejected. It makes
every project that reads from the network store maintain an edited copy of a
catalog Deltares publishes, and the edit — deleting descriptions of variables
nobody reads — has no scientific content. It also breaks the vendored file's
pinned upstream hash, which is the property that makes vendoring defensible
rather than drifty.

**Re-review against the upstream catalog and re-pin equality to it.** Rejected.
It restores the same brittleness one version later, and spends a model-validator
review on a question — how many variables does this file describe — that the
review cannot usefully answer.
