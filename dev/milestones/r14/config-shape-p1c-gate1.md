# R14 P1c — Gate 1, released 2026-08-29

The gate the brief says "releases the phase". Three decisions were listed; one
had already been corrected to a non-question before the gate was reached, and a
fourth item filed under it turned out to be closed.

## Ruled

**a. The registry is a Python module in `shared/`** —
`blueearth_cst/shared/variable_registry.py`.

`shared/` rather than `projections/` because variable metadata is already read
outside WF2: WF0's figures and WF1's `plot_map_forcing.py` both use
`CLIMATE_VARS`, so a `projections/`-local home would be wrong the day it landed.

Python rather than YAML because **the long form stays valid**. Required change 2
keeps it working, so a variable outside the registry can always be declared in
full — which makes the registry toolbox vocabulary rather than a project
surface. YAML would add a file, a schema and the coupled-edit discipline `C-65`
already imposes, for a document no project edits; and `canonical` and `change`
are enums Python validates for free. `K1` also puts `config/defaults/**` out of
reach, so a YAML registry would have had to invent a new home as well.

`C-49` — get `CLIMATE_VARS` out of Python — is untouched by this and stays
outside P1c by owner ruling.

**b. One record per variable, with `CLIMATE_VARS` a derived view.** One entry
carrying both attribute groups, satisfying D-10.6's "an attribute of one entity
belongs to that entity's registry" and S5's objection to two records of one
entity — while changing none of the 22 existing `CLIMATE_VARS` sites, which keep
importing the same name. It also leaves `C-49` strictly cheaper: a later move to
YAML acts on one file instead of reconciling two.

**c. `min_denominator` vs `min_reference`** — not a conflict. Settled in the
brief on 2026-08-27: `C-62` is the rename, so `min_reference` is the v1 name the
code reads and `min_denominator` is the v2 name the design documents.

## Two corrections to the brief, found while measuring

**`C-32` is closed, not open.** The brief's Gate 1 lists a live conflict between
the register's ruled `transient | constant` and the code's `transient | step`.
The register won and shipped: `prepare_weagen_config.TRAJECTORY_KINDS` is
`frozenset({"transient", "constant"})`. Ruled 2026-08-27, landed in P1b.

**The rung-4 reconciliation target no longer exists.** The brief says to
reconcile `test-fast` against `tests/data/r14_expected_red.txt`, "73 entries at
`31e9493b`, all P4-owed". P4 paid them: the list went 73 → 0 and both it and
`tests/test_r14_expected_red.py` were deleted. Rung 4 for this phase is
`test-fast` green with no reconciliation step.

## Re-measured scope

The brief says its counts are stale the moment P1c starts and to re-measure.
At `d97e1521`, and the difference matters for decision (b):

| token | brief (`31e9493b`) | measured (`d97e1521`) |
|---|---|---|
| `CLIMATE_VARS` | 8, "all in `climate_figures.py`" | **22, across 4 files in 3 packages** |
| `min_reference` | 4 | **11, across 5 files** |
| `max_flagged_months` | not counted | 10 |
| `relative_change` | 3 | 5 |

`CLIMATE_VARS` is read by `climate_analysis/climate_figures.py`,
`climate_analysis/climate_levels.py`, `climate_analysis/compare_sources.py` and
`model/plot_map_forcing.py`. It is not a WF0-local table, which is what put the
registry in `shared/`.

## Two findings that change the implementation, not the ruling

**`unit` and `units` are not the same fact.** This was the one attribute the two
tables appeared to duplicate, and the appearance is wrong:

| | `CLIMATE_VARS["precip"]["unit"]` | `VariableSpec.units` for `precip` |
|---|---|---|
| value | `mm` | `mm/day` |
| means | the figure's yearly TOTAL | the canonical monthly mean RATE |

Both are correct for their reader. The registry therefore carries both, under
both names, and a test pins the inequality — because the obvious "cleanup" is to
notice two spellings of one word and collapse them, which would silently
mislabel every axis or every change factor depending on which way it went.

**`pet` has no projections spec, and should not be given one.** No shipped
config declares it in `variables:`; it exists only in the figures table. So the
registry's projections group is NULLABLE, which buys a precise refusal: an
unknown variable and a known variable with no projections defaults are different
errors with different remedies — "add it to the registry" for the first,
"declare it long-form" for the second. Required change 3 asks for both remedies;
this is what makes each one true when it is printed.

## Consequences for the commit plan

`C-62` and `C-64` land as **separate** commits, per the brief's own commit-plan
invariants: `C-62` alone must leave the tree green with the renamed key still
read from `DEFAULT_MIN_REFERENCE`, and `C-64` alone moves the storage. Together
they cannot be reverted independently, and the phase's stated rollback point —
land 1–5, stop before `C-66` — gets coarser for no gain.

Three risks recorded before the work, each with the observation that would catch
it:

1. **The params boundary flattens the spec.** `analyze_projections.smk:1150`
   passes `{k: list(v) for k, v in VARIABLE_SPEC.items()}`, and
   `resolve_thresholds` recovers `change` as `fields[4]` — a positional read.
   Adding a field in the wrong position makes it read the wrong attribute and
   fall through to `"absolute"`, which skips the threshold check silently. The
   index becomes derived from `VariableSpec._fields`.
2. **`C-64` changes threshold PRECEDENCE.** Today it is `configured` →
   `DEFAULT_MIN_REFERENCE` → raise. After the move both a registry value and a
   configured value exist, and the config must still win. A wrong precedence is
   quieter than the failure the brief describes: a plausible number rather than
   an error.
3. **`ThresholdError`'s message names `relative_change.min_reference`**, a path
   that stops existing at `C-62` and whose parent stops existing at `C-66`. It
   is a string that names a key back to the user, so the tier rule moves it.
