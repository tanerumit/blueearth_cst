# P3 GF27 seed and namespace preservation acceptance

**ACCEPT — bounded GF27 scientific preservation for the final automatic-seed
generation matrix and experiment-rename resolution.** Reviewer: Astra
`model-validator` (`/root/model_validator_p3`), 2026-09-12.
Final software/orchestration signoff and full P3 acceptance remain pending.
GF15 estimator adequacy and milestone seal remain separate.

The coordinator completed three actual generation invocations, 35/35 jobs each,
using the same historical source data and final code with `seed: auto`.
The [capacity comparator](gf27-capacity-comparison.json) passed. The reviewer
independently reopened all three retained collections, checked physical payloads,
and repeated every forcing comparison under the `(rlz, st_id)` crosswalk.
[Independent evidence](gf27-independent-review.json) binds the comparator,
collection/config hashes, exact member mappings and rename-resolution result.

| Capacity | Identifier width | Resolved seed | Collection ID |
|---|---|---|---|
| 21 | 2 | 568532465 | `8fe8b35b958aee6facf909429361cc777f0dc8610b4aad25237699d73a6e69e6` |
| 22 | 2 | 568532465 | `477ef08702a47c5004fb4f88beea3ef97bd97ddfc343750b6877fc3c4eb74007` |
| 100 | 3 | 568532465 | `04a60cb01f94f632f4e1413b8c2e0fbc0f40442be2e5ad21da38c5777682efb3` |

All 14 members exist in each collection, with exactly the same scenario-member
coverage. Every forcing array, coordinate and attribute compares exactly with
capacity 21. The scientific generation payload, including seed projection and
resolution, is identical after removing only `unit_id_capacity`. Capacity
21 versus 22 isolates capacity from width; capacity 100 crosses to width three,
changing identifiers such as `01` to `001`. Width is derived from capacity,
not a separate setting. The three distinct collection identities preserve the
required namespace separation while leaving the draws unchanged. The reviewer
also checked the comparator's arithmetic assignment: it preserves precipitation
attributes in this installed xarray environment. An additional explicit `.data`
+1 precipitation perturbation preserves all attributes and every other variable
and coordinate, yet fails exact equality. The independent JSON records this
value-specific discrimination; no generator rerun was required.

## Experiment rename and old-seed migration

The reviewer copied only the capacity-100 project config into
`.tmp/scratchpad/2026-09-11_0010/gf27-experiment-rename/`, resolved workflow-file
pointers to their absolute paths, and wrote a copy of its simulation settings.
The only changed simulation setting is `experiment_name`, from `p3_final` to
`p3_gf27_renamed`. `resolve_selected_collection` on the original and copied
configs returns the same complete selection and manifest, using
`resolution_mode: project-generation` and the exact capacity-100 plan.
No explicit collection selector bypasses automatic resolution.

The original project config, original simulation settings, scenario plan and
ready manifest have identical hashes before and after both resolver calls.
The reviewer changed no live source file, retained plan, collection or experiment,
and launched no WF4 execution. The copied config paths and their hashes remain
in the independent evidence.

The separate old-seed migration cases are covered by
`tests/test_migrate_project_config.py::test_current_v2_split_preserves_seed_and_path_anchors`:
omitted seed maps to 123; explicit 0 and 8123 remain those integers; old `auto`
is frozen to the predecessor's experiment-derived integer. Source inspection
confirms those assertions. The coordinator's final software gate must retain
their passing execution status. This automatic-seed matrix tests the new
scientific projection; it does not claim that a new `auto` request must equal
the predecessor's experiment-name-derived seed.

## Verification and limits

The independent command used `pixi run --as-is python -B`, completed with exit 0,
and wrote only the named scratch config copies and compact evidence JSON.
It performed collection validation, all 42 member comparisons and two read-only
selection calls. No Snakemake, pytest, generator, Wflow run or benchmark was
launched by the reviewer. This is release / numerical affected verification at
the migration boundary; no tolerance was introduced or widened.

The accepted domain is one fixed source/config/provider/environment projection,
two realizations and six design points, with capacity 21/22/100. It establishes
namespace invariance and exact selection, not uncertainty convergence or
hydrological predictive skill. Parameter, structural, observational, scenario
and internal-variability uncertainties are not quantified. GF15 remains
unassessed; final P3 acceptance still requires the coordinator's remaining
software/orchestration and provenance reconciliation.
