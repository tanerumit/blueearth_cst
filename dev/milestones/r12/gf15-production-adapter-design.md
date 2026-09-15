# GF15 production adapter — decision record v3

Status: ACCEPTED; G1 Option A approved 2026-09-13; G2 approved exact v3 on 2026-09-14 for finalization and implementation handoff  
Date: 2026-09-13  
Decider: owner at G1/G2; author: cst-architect  
Lifecycle: frozen-with-supersession in the R12 milestone, with verbatim review archive and append-only revisions.  
Supersedes: none; proposes the narrow estimator/validation integration delta to accepted R12 §§7.5–7.6/8.4, preserving the frozen original.  
Revisions: 2026-09-13 — v1, initial production integration proposal.  
2026-09-13 — v2, G1 Option A framing recorded; domain-1 moment qualification, domain-2 outstanding parity handoff and risk-1 incomplete comparison coverage clarified. Scope unchanged.
2026-09-13 — v3, external round1 and promoted architecture/repo-fit findings resolved: export disclosure, constant/probability routing, live environment freshness, relocated source resource test and operational artifact allowance. G1 Option A unchanged; G2 pending.
2026-09-14 — G2: owner "yes I approve it" accepted exact reviewed v3. Stage 7 editorial landing records acceptance/lifecycle and relocates evidence citations; D1–D8 remain verbatim. External round1's v2 revise verdict remains historical; the scoped verification approves v3. Implementation gates remain unexecuted.

Reading guide: D1–D3 fix numerical behavior; D4–D6 fix evidence and identity; D7–D8 fix deployment and migration. The longer contract is needed to review scientific and software boundaries together. New paths, types, field schemas and identifiers below are **proposed**, unless explicitly described as existing.

Acceptance note: retained proposal wording identifies the accepted design's planned implementation surfaces; it does not assert that implementation exists or has passed its gates.

## Context and evidence boundary

Request type: **improve**. Map fixed range-normalized L-moment candidate C into WF4 for provisional operational point estimation, together with portable bounded-benchmark evidence, under the G1 Option A framing approved on 2026-09-13. The production design was accepted at G2 on 2026-09-14. Approval of “8x” selected performance policy `gf15-accuracy-8x-v1`; it did not approve this adapter, screening policy, real-bundle adequacy or estimator superiority.

Authoritative inputs are [intake.md](gf15-production-adapter-review/intake.md), [ledger.md](gf15-production-adapter-review/ledger.md), and the G1/G2 record in [status.md](gf15-production-adapter-review/status.md). Original findings are authoritative in [internal-review-domain.md](gf15-production-adapter-review/internal-review-domain.md) (domain-1, domain-2) and [internal-review-risk.md](gf15-production-adapter-review/internal-review-risk.md) (risk-1); the [review index](gf15-production-adapter-review/internal-review-index.md) groups them without replacing their wording. Paths below are repository-relative. The frozen method is `dev/milestones/r12/gf15-alternative-estimator-design.md` (accepted v4 D1–D6); integration authority is `dev/milestones/r12/wf3-simulation-identity-design.md` §§7.5–7.6/8.4. The separate adapter record is required by the frozen candidate design; it does not revise that method.

Evidence abbreviations resolve under `dev/milestones/r12/implementation/evidence/`:

| Premise | Source and supported conclusion | Boundary |
|---|---|---|
| E1 | `gf15-accuracy-8x/results/signed-verdict.json`, `summary.json`, `criteria.json`: C passes 144/144 cells, 24/24 baseline, 72/72 eligible relative cells and 120000 translation pairs under 8x; original 15/144 and 3x 124/144 remain failed | Retained development data, post-results policy choice; no new fits or fresh-data validation |
| E2–E3 | `gf15-production-applicability/{inspection.json,integration-readiness.md}` and current `metric_registry.py` / `metric_plan.py`: predecessor fitting, placeholder-only metadata, no report payload | Existing measured/source-inspected gap, not a new regression |
| E4 | Same inspection and `gf15-lmoments-readiness/environment/effective-environment.json`: shared environment lacked lmoments3 and Pixi was absent from PATH; study used 1.0.8 | Setup must be rechecked; no installation or solve claimed here |
| E5 | `content_identity.py::repository_code_inventory` and `metric_plan.py`: source closure, validation and environment feed metric identity | New adapter/report mutations still need discriminating tests |
| E6 | R12 §§7.5–7.6 and `gf15-production-applicability/scientific-assessment.md` | Operational screening and actual-bundle adequacy remain separate, provisional/unestablished |
| E7 | `gf15-lmoments-readiness/results/attempt-2/` and `results/independent/` contain accepted controls | Outstanding and untestable before a production adapter and qualified production environment exist; accepted reference controls and design approval are not a production parity pass. D8 and the validation plan carry the implementation prerequisite. |

## Affected capabilities and roadmap

| Slot | Binding / immutable revision | Owner / validation authority |
|---|---|---|
| `performance_analysis` | Fixed C, accepted method v4 and readiness attempt-2; lmoments3 hashes in D7; production binding will be accepted implementation commit, currently absent | python-engineer / model-validator for numerical mapping and bounded claims |
| `orchestrator` | Existing WF4 planning/publication interfaces at assessment commit `d761a65b`; proposed adapter contract v3, no new Snakemake DAG | cst-architect, implementation by python-engineer / independent integration reviewer |

`decision_framing` is not applicable: no basin decision criterion changes. `data_adapter`, `ensemble_generator`, `simulation_engine`, `system_model_validation` and `impact_model` are not applicable: no preparation, generation, simulation, model-validation or impact outputs. `robustness_evaluation` and `projection_overlay` are not applicable: no robustness/overlay outputs. Stochastic perturbations remain stress-test forcing; projections remain terminal plausibility overlays and cannot select or drive a run.

Roadmap: predecessor/C mismatch → explicit adapter → candidate estimates (reduction); missing evidence contract → shipped report and full validation → portable provenance (planning/publication/reading); unpinned dependency → isolated setup and parity → reproducible mapping (environment); migration risk → pre-change snapshot and new identity → upstream reuse (metrics-only).

No managed-project run enters `ready` here; namespace claim and run-control conformance are not applicable and none is claimed. A later executor must determine the selected root's managed status and satisfy applicable immutable intent, atomic namespace ownership, fenced writer, typed resources and resume controls before readiness. Folder separation and the existing metric writer alone do not prove that conformance.

## Decision — accepted candidate integration

### D1. Preserve production estimands and extraction

Change fitting only after `metric_registry.py::reduce_bundle` builds its per-location block sample. Preserve `compatible_bundle`, units/calendars/coverage, missingness, partial years, water-year anchor, warm-up, member ordering and response validation. Annual maxima remain member-local; low flow applies the existing seven-observation rolling mean before annual minima, never across members. Concatenate finite scalar blocks in increasing numeric `run_id`; do not censor finite negatives, zeros or ties.

Retain `required=max(ceil(1.0*T),10)` and `InsufficientReturnLevelBlocks` before the adapter. Keep p=1−1/T=.9 for peak T=10 and p=1/T=.5 for low T=2; no sign reversal. Low flow remains the median of annual seven-day minima. The metrics have different samples and separate scalar adapter calls; synthetic shared two-probability baseline acceptance must not couple production peak and low metrics.

Remove the predecessor `np.ptp(sample) == 0` guard: a screened constant sample reaches the adapter and refuses as `invalid_range`, carrying its structured `FitResult`. Insufficient blocks still refuse before fitting; extraction/compatibility errors retain their existing boundary.

No fallback, alternate estimator, retry, shrinkage, shape bound beyond c>−1, new sampling rule or interval. Preserve four result columns and float32/export formatting in `metric_plan.py` / `export_wflow_results.py`; compare float64 fit values as well as exports.

### D2. Typed adapter and fixed arithmetic

Add shipped `blueearth_cst/experiment/gev_lmoments.py`, statically imported by `metric_registry.py`. Proposed API: `fit_case(sample: NDArray[float64], probabilities: tuple[float, ...]) -> FitResult`. No metric/run ids, truth, generating parameters, ratio, RNG or config enters this API. The reducer owns context. Numeric conversion errors propagate; after conversion, invalid shape/content is a typed refusal.

`FitResult` is an immutable accepted/refused discriminated record (`status: accepted|refused`) carrying ordered refusal codes, source identity, warnings and available diagnostic stages. Acceptance requires every requested quantile valid; refused results provide no usable metric value. Arithmetic stays float64; persistence uses D3's finite-number dialect.

| Step | Normative mapping of frozen candidate C |
|---|---|
| Input | One-dimensional finite float64 sample, n≥4; one-dimensional nonempty probability collection; finite scalar p in (0,1). Preserve ties. |
| Normalize | a=min(x), s=max(x)−a; refuse nonfinite/nonpositive s. y=(x−a)/s; refuse nonfinite y. |
| Moments | Call `lmoments3.lmom_ratios(y,nmom=3)` once for l1,l2,t3. Order-statistic PWM formula: b_r=n⁻¹Σ_i [C(i−1,r)/C(n−1,r)]y_(i), r=0,1,2; l1=b0, l2=2b1−b0, t3=(6b2−6b1+b0)/l2. Unbiasedness concerns raw-sample/back-mapped linear L-moments under the sampling assumptions in exact arithmetic; random range normalization and float64 recovery create no new unbiasedness or exactness guarantee. Refuse nonfinite moments, l2≤0 or abs(t3)≥1. |
| Parameters | Call `lmoments3.distr.gev.lmom_fit(lmom_ratios=[l1,l2,t3])` once; read named c,loc,scale. Refuse nonfinite parameters, c≤−1 or normalized scale≤0. ξ=−c. Preserve pinned branches/approximations, 19 updates, relative shape tolerance 1e−6, positive-t3 branch Gumbel snap abs(c)<1e−5 and Euler constant .57721566; no replacement root solver. |
| Map | physical c=c_y, loc=a+s*loc_y, scale=s*scale_y; refuse nonfinite physical parameters or scale≤0. |
| Quantile | Float64 z=−expm1(c*log(−log(p)))/c, with c=0 branch z=−log(−log(p)); q_y=loc_y+scale_y*z; q=a+s*q_y. Refuse nonfinite intermediate/returned values. Compute all requested probability diagnostics and accept their conjunction. |

The finite-mean L-moment domain c>−1 is not a tuned prior. Fitted parameters, t3 and quantiles do not inherit the qualified linear-moment unbiasedness property above. The pinned implementation defines parity.

### D3. Refusals, faults and diagnostics

Refusal codes preserve the study: `invalid_sample`, `invalid_probability_collection`, `invalid_range`, `nonfinite_normalization`, `invalid_moments`, `invalid_parameters`, `invalid_physical_parameters`, `allowlisted_library_exception`, `quantile_conjunction`; probability reasons: `invalid_probability`, `nonfinite_quantile`, `shared_baseline_revocation`. Record reached stages/reasons; do not invent checks after early refusal.

Only exact built-in `ValueError("L-Moments Invalid")` at line 1307 and exact built-in `Exception("Iteration has not converged")` at line 1342 of verified `lmoments3.distr.GenextremeGen._lmom_fit` become exception-derived refusals. Require final raising frame resolved file=loaded `distr.__file__`, code-object identity with loaded method, module `lmoments3.distr`, function `_lmom_fit`, exact line/type/message and D7 digest. Subclasses or identical messages elsewhere are faults. Catch only around inversion to classify, immediately re-raising everything else. Every `lmom_ratios` exception, including ValueError, is a fault.

Map only `FitResult.status=refused` to existing `InvalidReturnLevelFit`, with structured `fit_result` and metric/unit-members/location/T/count/range/environment/implementation context. Remove predecessor adapter-wide `except Exception` conversion. Unexpected faults preserve traceback, with warnings attached as exception notes; never convert to refusal rows or blanks. Source mismatch is proposed `EstimatorSourceMismatch(RuntimeError)` before fitting. A warning alone never refuses.

Any refusal, unexpected fault or diagnostic computation exception aborts complete publication: no `metrics.json` marker and no omitted rows. Preserve reduction of all tables before payload writing. Failure diagnostics go to attempt logs, not a ready manifest; partial sets cannot be overwritten and recovery follows existing rules plus applicable run control.

An aborted old/new migration comparison is incomplete and cannot pass migration acceptance. Record the first failure with its metric/location/unit key and identify every remaining unvisited key as not evaluated. Any later diagnostic continuation is a separately identified nonpublishing check; it cannot turn the failed production attempt into acceptance or supply a ready marker.

Extend `ReturnLevelEvidence` with `fit`, `member_count`, and explicit extraction/missingness/partial-block policy identifiers. Retain location, member counts/coverage, total, required and physical `parameters` ordered `(c,loc,scale)` for callers. New `fit` fields:

| Field | Type / semantics |
|---|---|
| `schema_version`, `estimator_id`, `source` | `gev-fit/1`, `gf15-lmoments-c/1`, verified version/file hashes |
| `status`, `refusal_reasons`, `exception_refusal` | discriminant, ordered string codes, null or type/class-module/raising-module/function/line/file-hash/verbatim-message record |
| `input` | count, SHA-256 of ordered little-endian float64 sample bytes, requested probabilities; no raw x/y arrays |
| `normalization`, `moments` | a,s; normalized l1,l2,l3=t3*l2; physical l1=a+s*l1_y,l2=s*l2_y,l3=s*l3_y; invariant t3 |
| `normalized_parameters`, `physical_parameters` | named c,loc,scale or null before stage |
| `quantiles` | ordered p, normalized/physical estimate, diagnostic_valid, accepted, refusal_reason or null |
| `warnings` | ordered category name/verbatim message through success/refusal/fault |
| `normalized_diagnostics`, `physical_diagnostics` | separate sample_outside_support and nonfinite_log_density_count; null if not reached |

Use candidate strict `<lower`/`>upper` support tests and SciPy `genextreme` log-density in both coordinates. Support violations/nonfinite densities are **diagnostic only**, including physical endpoint rounding. Diagnostic exceptions are faults. Do not add physical PPF/CDF acceptance vetoes; those are validation controls only.

Nonfinite diagnostic numbers serialize as `nan`, `inf`, `-inf` strings; null means unavailable, never zero. Accepted parameters/quantiles are finite JSON numbers, counts nonnegative integers and booleans genuine booleans. Use the same dialect in refusal logs. Retain summary moments/parameters/counts, not raw samples or per-sample log densities.

### D4. Complete validation declaration

Replace planner placeholder equality with closed schema validation from shipped evidence, not arbitrary user annotation. Proposed declaration `return-level-validation/1` has exactly:

| Field | Required value / type |
|---|---|
| `schema_version`, `estimator_id`, `policy_id` | `return-level-validation/1`, `gf15-lmoments-c/1`, `gf15-accuracy-8x-v1` |
| `screening_ratio`, `screening_floor`, `screening_policy_status` | 1.0, 10, `provisional_operational` |
| `benchmark_status`, `benchmark_record` | `reviewed_bounded`; `{path: "return_level_benchmark.json", sha256: <actual packaged report bytes>}` |
| `tested_domain` | shapes_c [-.2,0,.2], counts [10,18,30,60], probabilities [.9,.5], ratios [0,.05,.5,2,10], relative_qualified_ratios [.5,2,10], draws_per_base_cell 1000 |
| `criteria` | decoded exact `gf15-accuracy-8x/criteria.json`, including policy history/claim boundary; original file digest also in report |
| `application_scope`, `relative_error_near_zero`, `actual_bundle_applicability` | `operational_screen_only`, `unvalidated`, `unestablished` |
| `evidence_use`, `screening_policy_validated`, `fit_uncertainty` | `post_results_development_rescore`, false, `point_estimates_only` |

Criteria retain valid rate≥.95; absolute signed median scale error≤.80 and P90 absolute scale error≤4 upper/2 lower. Relative eligible limits are **80% signed median magnitude / 400% upper P90 / 200% lower P90**. Translation acceptance is unchanged, accepted-pair absolute scale-error difference≤1e−6; both-refused pairs are not passes. Summaries use `method="linear"` on valid cohorts with denominators; refusals count against all 1000. Zero relative error is undefined/null; .05 is diagnostic. No averaging away failures.

These fields describe synthetic cells; never assign real bundles to that domain from fitted shape/scale, count or discharge ratio. `reviewed_bounded` means performance under the named relaxed retained-data policy, not independent/application validation. C's original and 3x failures remain in the report.

Before each production `fit_case` call, the reducer must check every actually requested probability against the verified declaration's `tested_domain.probabilities`, using exact numeric membership for the fixed .9/.5 values. A mismatch raises proposed `ReturnLevelProbabilityNotCovered(ValueError)` with the requested and declared probabilities before library invocation; it is a configuration/evidence-contract fault, not an estimator refusal, and aborts publication. Do not clamp, substitute, or expand the domain. This check remains outside the context-free adapter; generic adapter probability validation in D2 is unchanged. Changing a return period cannot silently inherit this bounded declaration.

### D5. Shipped portable report and immutable identity

Add shipped asset `blueearth_cst/experiment/data/gf15-accuracy-8x-v1.json` and loader `blueearth_cst/experiment/return_level_validation.py` (proposed). Load as package resource; no runtime dev import, absolute source-path lookup, network or scratch dependency. The asset is tracked in the existing plain importable source tree, per `pyproject.toml`; no installable distribution, build backend or packaging manifest is introduced. Test both in-tree and from a relocated copy containing the required package source and asset, with the original checkout, dev evidence and session scratch inaccessible to the loader. A future installable distribution requires a separate decision.

Report `gf15-benchmark-report/1` contains estimator/method identity; full D4 domain/criteria; original criteria hash; frozen wheel/source/environment identity; readiness attempt; retained RNG/seed recipe and inventory anchors; original/3x failed counts; complete 8x individual cells, translation cells, summary, failures and verdict; limitations; and `embedded_sources`.

Each embedded source has repository-relative `source_path`, exact byte `sha256` and original UTF-8 `text`. Embed `gf15-accuracy-8x/criteria.json`, `README.md`, `scientific-handoff.md`, `results/{individual-cells,translation-cells,summary,failures,source-freeze,signed-verdict}.json`, plus readiness `environment/effective-environment.json` and `results/independent/{signed-verdict.json,scientific-handoff.md}`. Verify duplicated summary/criteria against embedded sources. Historical absolute paths inside original text remain documentary only, never resolved. Compute actual hashes during packaging and check frozen inventories; none is invented here.

The report is self-contained for inspecting the verdict/thresholds, not a raw-data rerun archive. Raw samples/fits, full control programs and wheels remain in frozen evidence archives; inventory references state that boundary. `signed_by` is retained reviewer attribution, not a public-key signature.

Use existing `canonical_json_bytes` / SHA-256 (sorted keys, ordered arrays, finite JSON, final LF). No self-referential whole-report digest inside report; D4 carries it externally. Static adapter/loader imports enter existing `repository_code_inventory`; report data is bound explicitly through D4, not import discovery.

Keep metric_set_id hashing simulation_id, response_inventory_sha256, metric_definition_sha256 and metric_environment_sha256. D4 enters request/definition: report bytes, policy, adapter source and relevant dependencies each change identity. Exclude absolute asset paths, timestamps, scratch prefixes and whole-repo HEAD. Retain bounded stage-environment projection with D7 addition.

Planning verifies packaged schema/source bindings and digest. Recheck before reduction/publication and raise `MetricPlanStale` on change. Copy exact checked bytes to `return_level_benchmark.json`, flush with other payloads, then publish sole ready marker last. Missing/tampered assets fail; no downgrade to unassessed. Reader validates copied report bytes/schema/digest and definition/declaration consistency without the installed current report. Missing report, path escape, altered criteria or digest mismatch raises `ImmutableMetricSetError`.

For new-set execution, use one proposed `resolve_metric_environment()` in `metric_plan.py`, shared by `current_metric_request` and execution freshness checks. It freshly calls existing `stage_environment` with the existing NumPy/pandas/SciPy/xarray/xclim/netCDF4/pyproj/PyYAML roots plus lmoments3, then adds D7's observed and verified lmoments3 version/source hashes. Retain the resolver's bounded Python/distribution/native closure and platform fields; exclude installation paths and timestamps. Do not derive this observation from the retained request, a cached planning descriptor or lock-file intent. Compare canonical descriptor bytes and their digest with the retained `metric_environment` and `metric_environment_sha256`; both must agree. Existing `build_metric_plan` reconstruction using the retained descriptor alone is not this check.

The execution process resolves and compares before any `reduce_metric_plan` fitting, and `publish_metric_set` resolves and compares before reduction/payload writing and again immediately before the final ready marker after payload flush. A changed live descriptor raises `MetricPlanStale`; no fitting occurs on an initial mismatch and no ready marker appears on any mismatch. A late mismatch leaves an unready partial destination subject to existing recovery rules, never a silently relabeled result. Failure to resolve also aborts without a marker; the qualified-source mismatch retains D3's `EstimatorSourceMismatch`. Resolving a new request explicitly is the route to a distinct identity, never mutating the retained request. No live environment check is added to `read_metric_set` or explicit historical ready-set reads. Use an isolated, unchanged environment for each execution; these boundary checks detect observed drift but do not provide an atomic lock against concurrent external package mutation.

### D6. Existing-ready-set compatibility

Continue reading `metric-set/1`. Dispatch on retained validation: exact legacy `{status: provisional_operational, benchmark: not assessed}` uses existing checks with no report; new `return-level-validation/1` requires D4–D5. Reject other unversioned shapes/unknown versions; no missing-field defaults. Keep outer `metric-set/1` as a versioned inner-record extension. Older readers may reject new sets; backward reading by new software is the guarantee.

Never rewrite old manifests, annotate them as C, recompute retained definitions from current registry, or require lmoments3 to read them. Retained source/environment hashes are provenance, not installation demands. Make numerical dependency imports lazy until new fitting. Reader still requires retained simulation/response artifacts; report portability does not make an incomplete experiment portable.

New requests emit only D4; legacy acceptance is read compatibility, not a write escape hatch. Previous plans become stale under changed live code; new plans create distinct sets while explicit old-set reads work. Exact ready reuse preserves every byte; partial destinations retain existing refusal/recovery rules.

### D7. Dependency pin and isolated setup prerequisite

Pin `lmoments3==1.0.8`, wheel SHA-256 `984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e`. Before fitting verify `__init__.py` SHA-256 `1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2` and `distr.py` SHA-256 `f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee`. No configurable bypass. A same-version repack with different source is unqualified.

Preparation resolves actual Pixi executable and isolated install prefix; never install into shared symlinked `.pixi`. Apply pixi-env procedure, add explicit dependency in `pixi.toml`, solver-generate `pixi.lock` for win-64/linux-64, capture commands/solver version/artifacts. Never hand-edit lock; preserve Julia management. Unavailable tooling/wheel blocks setup and is reported, not silently replaced. No solve success is claimed.

Study Python 3.12.13, NumPy 2.4.6, SciPy 1.18.0 are initial parity targets; record actual build/platform and full numerical closure separately. D5's single resolver adds lmoments3 to the metric stage-environment roots and retains roots needed by other reducers; it binds installed source hashes as well as versions/artifacts at planning and execution. Platform/native differences need distinct environment records and parity; version equality alone is insufficient. Unavailable exact platform targets return to owner rather than silently relaxing pins.

### D8. Metrics-only migration and acceptance sequence

Before first implementation commit, select a complete retained experiment and freeze a read-only pre-change snapshot outside output write targets. Record its path and inventory: collection id/revision, simulation id, response inventory/artifact hashes/request, old metric manifest/id/report if present, indicator tables, unit index, member counts/coverage, configs, old source commit/inventory, environment and exact old execution command. No suitable comparison means stop at this prerequisite; do not substitute stale standing evidence or generate a successor baseline.

Keep snapshot immutable until independent comparison acceptance. New metrics use a distinct claimed namespace with retained upstream inputs, never the snapshot as a write target. Materialize selected config and documented invocation before execution: existing entry point is `scripts/simulate_system.py`, operation selected in workflow config. No guessed `--metrics-only` flag or preselected basin is introduced.

Preserve the four-column CSV schema and export formatting explicitly. Existing in-tree `metrics.json` is already a sibling manifest binding table digests; D4–D5 extend that provenance for C. A bare detached CSV carries neither estimator nor metric-set discriminator: identical metric names across old/new vintages can silently mix predecessor and C values. Handoff 2/4 user docs and the 3/4 migration record must disclose this limitation and instruct consumers to retain the metric-set manifest, checked report and required retained context when comparing vintages; never infer estimator from CSV schema or metric name. Select external finding ext1-1 alternative (b), disclosure within the preserved export surface. Alternative (a), a new sibling export provenance product, is not adopted: the existing in-tree manifest already binds tables and a new export product is outside G1's preservation boundary. Reconsider it only through G1 if standalone export provenance becomes required.

Within the selected experiment's results namespace, allow only the new metric-plan/set/report artifacts. Separately allow the existing `project_dir/config/runs/invocations/simulation-<id>.json` bookkeeping and declared attempt logs outside retained scientific inputs. Record those paths in the comparison; they do not excuse any collection, simulation, response request/inventory or native-response byte change.

| Handoff | Owner / deliverable | Acceptance authority |
|---|---|---|
| 1/4 snapshot/setup | python-engineer: pre-change inventory, exact commands, isolated lock/environment | independent integrity review; snapshot before first implementation commit |
| 2/4 adapter/report | python-engineer: D1–D7 shipped code, owning tests, user docs; carry E7 as outstanding until source-verified production-versus-frozen-control parity is recorded on every supported platform | model-validator returns parity/fault/diagnostic verdict before integration, using unchanged frozen tolerances, exact acceptance/refusal checks and a wrong-result mutant that fails |
| 3/4 metrics comparison | python-engineer: old/new tables, float64 evidence, upstream inventory and explicit comparison coverage; after an abort, first failure and all remaining not-evaluated keys per D3 | model-validator accepts preserved extraction and documented estimator changes only with complete comparison coverage; an aborted comparison cannot pass; no model/generation reruns |
| 4/4 integration acceptance | cst-architect reconciles evidence and scientific verdict; acceptance record retains E7's per-platform evidence/verdict and comparison coverage, with any unexecuted prerequisite explicitly outstanding | named reviewer/owner under accepted gates; neither design approval nor nonpublishing diagnostics settles a failed or unexecuted acceptance gate; baseline/seal separate |

Affected existing files: `blueearth_cst/experiment/{metric_registry,metric_plan}.py`, `pixi.toml`, solver-generated `pixi.lock`, owning tests below and user metric docs located during implementation. New adapter/loader/asset are above. Leave `content_identity.py` unchanged unless its projection cannot represent D7; shared changes take broader gates. `export_wflow_results.py`, simulation/generation identity and Snakefiles are preservation surfaces, not planned numerical edits. Commits stay runnable: no dependency consumer without setup/lock support or candidate writer without report/schema.

## Validation plan and falsifiable consequences

Future gates below are unexecuted. Driver reports 71 owning tests collected, exit 0; no tests executed and no new integration/scientific acceptance follows. After implementation the existing owning command is `pixi run pytest tests/test_metric_registry.py tests/test_metric_plan.py tests/test_content_identity.py tests/test_export_wflow_results.py`, plus proposed candidate tests. Capture full logs to scratch. Run `pixi run lint` / `pixi run format-check` before Python commits, `pixi run test-fast` at integration and documented full gate when shared code/script signatures change. No baseline/seal execution here.

| Claim | Independent falsifier / required result |
|---|---|
| C mapping | Retain attempt-2 independent oracle/control inputs with provenance; production code cannot be its oracle. Preserve frozen population/branch tolerances and stop rules. Fixed-sample study/production acceptance/refusal codes agree exactly; quantities meet specific frozen tolerances. Wrong sign, omitted scale map, wrong c=0 branch, c≤−1 acceptance or deliberate quantile perturbation must fail. |
| Extraction | Existing annual/rolling/calendar/missingness/partial-year fixtures plus member-boundary-crossing mutant; sample order/hash and usable counts match old extraction. required−1 refuses before library invocation. A screened constant sample must produce structured `invalid_range` matching the frozen candidate; retaining the old unstructured constant guard must fail this test. |
| Probability coverage | Keep code/report/declaration otherwise fixed and change a reducer's requested return-period probability outside [.9,.5]: typed coverage fault before fitting and no ready marker. Fixed peak/low .9/.5 pass coverage separately; the guard does not couple their samples or expand empirical applicability. |
| Fault boundary | Actual pinned raising statements refuse; foreign frame with identical message, subclass, lmom_ratios error, source mutation and arbitrary RuntimeError propagate with no ready marker. Assert one fitting call, no retry. |
| Diagnostics | Retained endpoint-rounding/support controls stay accepted when validity passes; nonfinite density increments diagnostic count. Veto mutant fails. Overflow warnings survive refusal; diagnostic exception stops attempt. |
| Identity/report | Independently alter adapter bytes, policy/report and dependency/source identity: each changes identity. Alter/remove copied ready report: reader fails. Unknown schema/declaration-report disagreement fail. |
| Live environment | Build and retain plan/request A; change the executing resolver's observed NumPy/SciPy or native descriptor to B while keeping request, code, report and pinned lmoments3 source hashes unchanged. Both direct reduction and publication must raise `MetricPlanStale` before fitting, with zero fit calls and no marker. Separately switch the observation only at the final pre-marker check: no marker and an unready destination. A newly resolved B request gets a distinct metric identity with unchanged collection/simulation/response identities. Reusing A's descriptor instead of observing B must make these tests fail. These are unexecuted discriminating contract tests, not evidence of a qualified B environment. |
| Resource portability | Relocate the required importable package source and tracked asset; deny original-checkout/dev/scratch access. Loader returns exactly the same verified report bytes/digest; omit or corrupt the relocated asset and require failure. No wheel/build configuration is part of this gate. |
| Compatibility | Read real pre-change ready snapshot without lmoments3/current report. Read new set with package asset unavailable; copied report suffices. Old bytes/hash stay exact; tampered legacy bytes fail. |
| Metrics-only | Disable Wflow/Julia/generation access during retained-response reduction. Collection/revision, simulation, native bytes/request/inventory stay exact. Only new metric-plan/set/report artifacts appear within the selected experiment's results namespace; outside it, record and allow only the existing invocation bookkeeping and declared attempt logs per D8. Non-return-level exported rows remain exact; compare return levels by metric/location/unit keys and document every evaluated change/refusal without arbitrary old/new equality thresholds. Verify the docs and migration record disclose the detached-CSV vintage hazard and preserve four-column formatting. A refusal/fault abort must yield an incomplete comparison record identifying the first failure and every remaining not-evaluated key, no ready marker and no migration acceptance. Any diagnostic continuation is separately identified and nonpublishing and cannot convert that failed attempt into acceptance. |

The 1e−6 translation criterion is not a blanket parity tolerance. Use specific accepted controls in `gf15-lmoments-readiness/{test_readiness.py,reference_oracle.py}` and `results/attempt-2/numerical-controls.json`; preserve population-gate precedence, branch characterization and bounded oracle enclosure. Changed tolerances require scientific review. Production parity must pass on each supported platform; unavailable Linux execution remains outstanding, not a Windows-derived pass.

Observable gains: new sets identify C and carry verifiable bounded evidence; old sets remain readable; report changes create new identities. Costs: dependency/source guards can prevent fits, repeated bounded environment resolution adds execution overhead, reports add size and readers maintain two validation dialects. Detached bare CSVs remain estimator-ambiguous across vintages and can silently mix predecessor/C results; D8 requires disclosure and retention of provenance context, without changing the export surface. Return-level differences are expected and documented, never hidden by baseline refresh. No prediction of better real-system accuracy follows.

## Alternatives considered and G1 decision

**A — provisional C integration (selected at G1):** adopt D1–D8 only after G2 design acceptance and later implementation gates. This explicitly maps the assessed candidate and closes provenance gaps together. The owner selected this framing for provisional point estimates under permissive, adaptively selected retained-data policy with actual-bundle adequacy unestablished. It imposes dependency/source pinning, compatibility tests and disclosure; no new estimator research.

**B — retain xclim/SciPy predecessor:** preserve current numerics and separately repair metadata for truthful predecessor evidence; never attach C's pass to it. Prefer when avoiding setup/migration cost outweighs candidate use, or parity cannot be demonstrated. It preserves continuity but does not repair original predecessor qualification failure; unchanged is not adequate by implication.

**C — require actual-bundle validation before all C production use:** defer integration for separately scoped dependence, stationarity, sample-regime and decision-uncertainty assessment. Prefer when use requires defensible real-system threshold decisions. It addresses the actual scientific limitation but expands data/method scope and delays use; 8x cannot satisfy this prerequisite. No such study is authorized here.

G1 approved A and the domain-1/domain-2 minor actions on 2026-09-13 after the v1 scientific review. V3 retains those actions and risk-1, and accepts all seven round1/promotion findings as detailed in the append-only ledger. Authoritative finding text remains in [external-review-r1.md](gf15-production-adapter-review/external-review-r1.md), [internal-review-architecture.md](gf15-production-adapter-review/internal-review-architecture.md) and [internal-review-repo-fit.md](gf15-production-adapter-review/internal-review-repo-fit.md). The two major environment findings share D5's new live-resolution check; neither is regraded. No blocking or major finding is rejected. The export alternative selection above adds no product. No scientific method, policy, screening or G1 Option A scope changes. G2 accepted exact [design-v3.md](gf15-production-adapter-review/design-v3.md) on 2026-09-14: owner "yes I approve it", as recorded in [status.md](gf15-production-adapter-review/status.md). External round1 remains a revise verdict on v2; round2 was waived after the recorded trigger checks, and [scoped-review-v3.md](gf15-production-adapter-review/scoped-review-v3.md) approves exact v3 with zero findings. This acceptance releases finalization and implementation handoff; it is not a full external approval of v3 or an implementation-validation pass.

Remaining risks: production/environment parity unmeasured; isolated Pixi setup unresolved; retained pre-change snapshot not yet selected; cross-platform parity and packaged asset inclusion untested; real fits may refuse complete set publication. These are gates, not reasons to alter C or reinterpret benchmark evidence. Standing successor-baseline/seal prerequisites remain separate and excluded.
