# P3 scientific review preparation

Reviewer: Astra `model-validator` (`/root/model_validator_p3`), 2026-09-11.
**Comparator correction accepted; final P3 scientific acceptance pending.**
This reviews the accepted criteria and development evidence, not a final run.
The reviewed working tree is based on `078f508d3ea3a2368d15602f68e7867daf400f3d`
with uncommitted P3 changes. No numerical implementation or tolerance was changed
by this reviewer.

## Class-C comparator ruling

The correction in [compare-scientific-crosswalk.py](compare-scientific-crosswalk.py)
follows accepted design sections 7.2 and 12.3. The established table tolerance
applies to Class A/B. Class C changes publication grain, so
`mean(round(run))` and `round(mean(raw runs))` need not agree. The comparator
independently calculates raw run values from native responses, requires each
published Class-C run value to reproduce exactly at the unchanged float32,
four-significant-digit representation, and requires the raw mean to reproduce
the old pooled publication at that same representation. This is also the
explicit method of the accepted [P2 scientific handoff](../p2/scientific-handoff.md).
It introduces no new tolerance and needs no owner criteria ruling.

The development report at
`.tmp/scratchpad/2026-09-11_0010/gf9-development.json` records 546 Class-A and
70 Class-B rows with zero differences, 140 independently checked Class-C run
publications, and 70 exact pooled projections after publication formatting.
All 686 old and 756 new keys are accounted for. The original failure was a
rounded-mean value of 0.022755 against a pooled publication of 0.022750 at
`q_driest_month_mean`, location `1040`, unperturbed group. Its 0.000005
difference exceeded that group's absolute table tolerance of approximately
0.0000047443. Other rounded-mean deltas reach 0.005 in higher-magnitude rows;
they remain recorded in the crosswalk. These are explained representation
effects of the accepted grain change, not evidence of changed native responses.

The comparator checks both directions of row coverage, duplicated joins,
reference invariance under four combinations of artifact/series order, and
opposite-season native gauges with a wrong-ordinal control. Numeric-perturbation,
lost-row and duplicate-row controls also discriminate. Its development flag
correctly prevents treating this report as final acceptance.

## Final evidence prerequisites

| Gate | Required final evidence and bounded scope |
|---|---|
| GF9 | Fresh final entry-point run against immutable P0, unchanged scientific settings, all 14 forcing/native crosswalks, all A/B/C checks, source/model/environment/config/code provenance and exact retained manifest identities. Run the comparator without `--development` only once those inputs are final, then obtain the named scientific handoff. |
| GF27 | Actual generation with `seed: auto`, otherwise identical settings, at capacities 21, 22, and 100. The first pair varies capacity while retaining width two; 100 crosses to width three. There is no independent width setting. Require equal resolved seeds and all 14 forcing arrays under the scenario crosswalk, distinct collection namespaces, and expected padded IDs. Experiment rename must leave collection selection unchanged. Preserve default/explicit/old-auto migration integer evidence from `test_current_v2_split_preserves_seed_and_path_anchors`. |
| GF28 | Carry forward accepted P2 bounded temporal evidence, with final-code test results and actual final-run source/prepared/response clock and endpoint comparison. Preserve the recorded no-leap reader conversion, clipping, TOML refresh, interval-end response labels and annual reductions. The opposite-season fixture includes a leap day; existing non-January and partial-year metric checks must remain covered. Any new mismatch requires diagnosis, not calendar repair. |
| GF31 | Repeat the existing four-branch portable preparation comparison on final code: ERA5, CHIRPS, CHIRPS-global and dormant E-OBS. P3 changes the generated catalog selector from `forcing` to `run_<id>`, so existing P2 execution alone does not exercise the final binding. Compare actual arrays, grid/time/units and parsed result-affecting TOML values while original fixture paths are unavailable; exclude only declared locator relocation. Retain missing/changed-ancillary refusal evidence. |
| GF29/GF30 | Coordinator supplies fresh direct-generation and all-workflow-runner checkpoint logs, final dedicated-simulation and all-workflow-runner logs, and retained-only metrics evidence. These establish orchestration and are not implied by the numerical comparator. |

The earlier `validator-gf27-witness.json` is development evidence from before
the automatic-seed projection correction: it records
`console_seed_invariant=false` and lacks the current `generator_settings`
projection field. Recompute the witness on final code; do not promote the
earlier record. Generating only explicit seed 123 proves preservation against
P0 but does not demonstrate automatic-seed independence under capacity changes.

Use new scratch roots for repeats. Preserve P0 and all P2 evidence. The retained
P2 portable probe source is [portable-preparation-probe.txt](../p2/portable-preparation-probe.txt);
its hardcoded scratch root and synthetic manifest must be adapted to the final
contract without changing the fixture values or physical method. The existing
P2 limitations remain: ERA5 values with synthetic elevation exercise the CHIRPS
branches, and E-OBS retains its production limitation. This is branch-preservation
evidence, not real-CHIRPS model validation.

## GF15 recommendation for the owner gate

Recommend authorizing the exact proposed section 7.5 benchmark as a bounded
estimator diagnostic, with its existing cell choices and criteria unchanged.
No benchmark has been executed or approved by this review. The owner must accept
the concrete criteria before execution, under Master Gate 2.

The proposal comprises 1,000 seeded draws per shape `{-0.2, 0, 0.2}` and block
count `{10, 18, 30, 60}`, evaluated at probabilities 0.9 and 0.5. Pin the RNG,
seeds, GEV sign convention, unchanged estimator and environment. The proposed
criteria are valid-fit rate at least 95%, absolute median scale-normalized error
at most 0.10, and 90th-percentile absolute scale error at most 0.50 (upper) or
0.25 (lower). Translation checks use the same draws at ratios
`{0, 0.05, 0.5, 2, 10}`, paired scale-error tolerance 1e-6, and unchanged validity
classification. Relative criteria apply only at ratios `{0.5, 2, 10}`: absolute
median bias at most 10%, and 90th-percentile absolute error at most 50% (upper)
or 25% (lower). Both scale and relative criteria must hold in a claimed cell.

These are performance targets to test, not established precision guarantees.
At a nonzero generating ratio, relative error equals scale-normalized error
divided by that ratio; consequently the low-ratio cells impose stricter effective
scale-error requirements. Keep all cells, denominators, refusals, translation
failures and zero/near-zero diagnostics visible. Do not pool results to hide a
failed cell, choose a replacement estimator, or adjust criteria after results.
A failure returns to the owner for a method ruling. Even a pass cannot validate
the screening floor/ratio, dependent or nonstationary blocks, or actual-bundle
applicability; metadata must retain `provisional_operational` and the explicit
application limits. Class-B interval estimation remains outside this migration.

## Verification and applicability

Review posture: release / numerical affected for the P3 migration acceptance
boundary; this preparatory subtask was read-only inspection plus this record.
Read the accepted design, master/phase briefs, P2 signed handoffs, final working
comparator, development report and failure diagnosis; inspected the touched
preparation binding and existing seed/temporal tests. No workflow, benchmark or
software test was run for that initial review. The coordinator owns the ongoing
full software gate and final executions.

The coordinator subsequently assigned the two bounded probes to this reviewer.
[probe-generation-capacity.py](probe-generation-capacity.py) stages generation-only
configs and compares three explicit manifests; it never launches Snakemake.
[probe-portable-preparation.py](probe-portable-preparation.py) repeats the retained
four-branch fixture in an exclusively new `--work` directory and explicitly
requires the final `run_01` catalog entry. Both probes passed Ruff check and format.
GF27's staging command passed using the development smoke config and wrote only
`.tmp/scratchpad/2026-09-11_0010/gf27-staging-review/`; GF31's import/`--help`
check passed. Full physical and capacity executions remain pending and belong
to the coordinator. The checks used the existing Pixi environment with
`run --as-is`; no environment or production code was changed.

The demonstrated domain remains the seed-123 ERA5 migration reference, two
realizations, six design points and the 2046–2054 simulation window. Equality
demonstrates preservation, not held-out hydrological skill. No observational,
parameter, structural, scenario or internal-variability uncertainty bounds are
estimated here; two realizations do not establish adequate uncertainty sampling.
Final acceptance requires the identified artifacts and comparisons and remains
pending.

## GF31 selector metadata ruling, 2026-09-12

The first final probe stopped at ERA5's strict attribute comparison. Independent
read-only inspection of `gf31-final-physical/era5/{old,new}/forcing.nc` found
all values and coordinates exactly equal on 3,287 times by 16 latitudes by
24 longitudes. The only differing attributes were `precip.precip_fn`,
`pet.pet_fn`, and `temp.temp_fn`, each `forcing` in the old path and `run_01`
in the final path. Checking and excluding exactly these selectors in memory
left complete attribute equality; complete parsed TOMLs also match.

This is the declared metadata relocation of the accepted WG-5 catalog-selector
migration. It does not require a numerical tolerance or owner criteria change.
The probe now refuses any other spelling, records the exact three pairs, and
compares all remaining attributes/coordinates/values exactly. Its precipitation
perturbation control now preserves attributes so its failure specifically
demonstrates numerical discrimination. The failed root was preserved unchanged;
the coordinator must execute the corrected probe in fresh
`gf31-final-physical2`. No full probe rerun or final GF31 acceptance is implied
by this diagnosis.
