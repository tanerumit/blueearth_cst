---
verdict: revise
doc_version: design-v2.md
findings:
  - id: repo-fit-1
    severity: major
    section: Method
    finding: Estimator exceptions are not distinguished from unexpected execution faults.
    rationale: D1 step 4 can turn infrastructure or adapter defects into complete-looking refusal rows and depress the all-draw valid rate without triggering a run stop. The cited library really raises a built-in Exception for non-convergence; the predecessor harness also demonstrates broad catches, so copying it would preserve this risk.
    suggested_fix: Specify an allowlist of anticipated numerical or domain exceptions at the narrow library-call boundary, including the exact non-convergence exception type and message with verified traceback origin. Record type, origin and message; re-raise every unrecognized exception and stop the run. Do not identify origin through the exception class module, which is builtins for this exception.
  - id: repo-fit-2
    severity: minor
    section: Inputs and provenance
    finding: The design omits the available inventory anchors and concrete flattening map for predecessor comparisons.
    rationale: The data are usable and a retained harness already implements the joins, but a second implementer must rediscover that B baseline probability is nested and that baseline null differs from translated ratio zero.
    suggested_fix: Name the two inventories and their hashes below, bind their selected fixture and row entries, and require uniqueness and complete key coverage before candidate execution. Preserve A valid and B accepted without retroactive reclassification.
  - id: repo-fit-3
    severity: minor
    section: Validation regime
    finding: Planned branch controls lack concrete inputs and a separation between approximation characterization and implementation correctness.
    rationale: The three generating shapes exercise positive sample-skewness inversion, including the Gumbel snap, but do not by themselves exercise the negative-skewness branches. V2 separately requires every branch to be controlled, so this is incomplete readiness detail rather than an absent validation obligation.
    suggested_fix: Freeze a branch control table and independently derived references at Stage 1, covering both sides of boundaries and the snap; distinguish fixed control tolerances from measured library approximation error. Stop before the matrix if any required control remains undefined or fails; no post-result tolerance adjustment.
  - id: repo-fit-4
    severity: minor
    section: Method
    finding: Shared baseline acceptance should explicitly say that failure of either requested quantile refuses the entire baseline fit.
    rationale: That interpretation is consistent with D2 and predecessor B protocol, but A records per-probability valid flags. Implementers must not silently harmonize A and B acceptance while constructing comparisons.
    suggested_fix: State the candidate baseline all-requested-quantiles conjunction, apply it to both baseline rows and their translation comparisons, and keep any per-probability diagnostic flags separate.
  - id: repo-fit-5
    severity: minor
    section: Validation regime
    finding: The SciPy quantile diagnostic is independently implemented but shares the analytical expression.
    rationale: Installed SciPy genextreme _ppf uses the same expm1 relation. Agreement checks mapping and transcription, not an independent derivation of the probability relation.
    suggested_fix: Describe this as a mapping and sign diagnostic; add independently derived CDF round-trip or fixed analytical reference values with a prospective tolerance if stronger oracle independence is intended.
---

# Repo-fit review — frozen

Review mode only. Read design-v2.md, review-brief.md, intake.md and the G1 authority section of status.md. G1's range normalization, finite-mean domain and diagnostic-only support policy are respected. No defect is inferred from likely scientific failure. No installation, fitting, benchmark, candidate implementation or production change was performed.

## External premise dispositions

External severities below are preserved as received; these dispositions are independent assessments, not edits to that review.

| External ID / severity | Independently checked disposition |
|---|---|
| ext1-2 / major | Supported exception ambiguity; repo-fit-1. A broad catch is not logically forced: an exact-type/message/origin filter can catch and re-raise unknown exceptions. Thus the claimed inevitability is overstated, but the missing policy is material. |
| ext1-3 / major | Branch-coverage premise supported; severity/consequence overstated. V2 already requires branch/exception controls, independent calculations and a pre-execution readiness stop. It does not claim the three population cases cover every branch. No measured evidence here establishes that 1e-5 is inadequate. Concrete controls remain necessary at readiness (repo-fit-3). |
| ext1-4 / major | Missing explicit bindings supported; unproducibility premise not supported. Opened representative retained A/B records and inspected the existing joining harness: all keys exist and flatten cleanly. Exact inventory anchors and mapping below resolve discovery. Require full key verification before execution (repo-fit-2). |
| ext1-6 / minor | Worth clarifying, but shared acceptance naturally means conjunction; B explicitly specifies that rule. A has probability-specific validity. Preserve the distinction (repo-fit-4). |
| ext1-8 / minor | Same-expression premise confirmed in installed SciPy source. Independently implemented mapping checks remain useful; they are not the same fitting routine used as its own oracle. Stronger derivation checks are a bounded improvement (repo-fit-5). |

## Primary evidence and exact input anchors

Paths below are relative to `dev/milestones/r12/implementation/evidence/`.

- A inventory: `gf15/artifact-inventory.json`, SHA-256 `3f13145d29c377a1c92042b3845695ce293edd58e565e17a67851767026719e1`.
- B inventory: `gf15-normalized-qualification/artifact-inventory.json`, SHA-256 `07148bb3b165ef2d1785fb49fc57908d260009cd7885c7b39712e1148aefdf4a`.
- Authoritative criteria: `gf15/results/criteria.json`, SHA-256 `988611b6d239b95f7542f8d67470395e4997ac61dd97198fd075fdcba552d643`.
- Original provenance: `gf15/results/provenance.json`, inventory SHA-256 `0d85d2a63c6be70683e2a1485de7bfc6266a265fd383cf96b124b6facdc67db2`.
- B provenance: `gf15-normalized-qualification/results/provenance.json`, inventory SHA-256 `a1ea18808890a1c270e75a35441b1bb4eecdb901551c6fafce0565be822686ae`. It records Python 3.12.13, NumPy 2.4.6, SciPy 1.18.0, xclim 0.60.0 and lock SHA-256 `ca888ef1c4547ee0624fc4da319de87fd9284418b2fbe16171118bc8f7b64041`.

Use the inventory `files[].path`, `bytes` and `sha256` entries as the complete file-level input manifest, rather than transcribing hundreds of hashes into prose. Select all 12 `gf15/results/samples-c{i}-n{n}.npy`, all 240 `gf15/results/draws-c{i}-n{n}-{start:04d}.jsonl.gz`, and all 240 `gf15-normalized-qualification/results/fits-c{i}-n{n}-{start:04d}.jsonl.gz`; i=0,1,2 maps to c=-.2,0,.2; n=10,18,30,60; start=0,50,...,950. B's matching `.json` receipts bind chunk SHA-256, fit/quantile counts and a binding digest.

Example pinned entries: A `samples-c0-n10.npy` = `d4d31acd7971da58c2430f7cb9647ee3db30061093f1d5cd568bedc62541c970`; A `draws-c0-n10-0000.jsonl.gz` = `97a8ee9aef565c43f8635d015a29651df5d08d38805d25282c1086ccb9386f04`; B `fits-c0-n10-0000.jsonl.gz` = `29129b38214b23e4efc9bcef84b07293bfda23c4ffe68556876d897cad17c270`.

Important byte distinction: B's criteria copy has inventory digest `0181b4a1044c66ab4c819fded1ae39d35608ea375ddc46bdaf2d87587714ddca`, different from A. B's `independent-review.py:89` checks decoded JSON equality, not byte equality. Its `criteria_exact: true` therefore must not be cited as byte equality. V2 correctly selects the original file for future byte-exact preservation; do not substitute the B serialization.

The original `benchmark-estimator.py:430` emits A rows. `gf15-normalized-qualification/qualify-normalized.py:224` reads the A rows keyed by probability, ratio and draw, loads the stored array with `allow_pickle=False`, and supplies `samples[draw] + old["mu"]`. Reuse these retained offsets; do not regenerate samples from the seed recipe. B's `independent-review.py` and retained `independent-review.json` document its prior complete audit (132,000 fits, 144,000 quantiles, 120,000 pairs); that audit was read, not rerun.

## Field mapping and readiness checks

Canonical quantile join key: `(shape_c, n, draw, p, ratio)`; `ratio=null` denotes baseline and `ratio=0` denotes a translated case, never interchangeable.

| Quantity | A draw row | B fit row flattened once per quantile |
|---|---|---|
| Generating shape/count/draw | `shape_c`, `n`, `draw` | Same top-level fields |
| Probability | `p` | `quantiles[j].p`; baseline top-level `p` is null |
| Baseline/translated and ratio | `ratio` | top-level `ratio` |
| Acceptance used in comparisons | `valid` | top-level `accepted`, shared by nested rows |
| Estimate/errors/truth | `estimate`, `scale_error`, `relative_error`, `true_quantile` | Same fields under `quantiles[j]` |
| Offset into physical supplied sample | `mu` plus `samples[draw]` | `mu`, inherited from A |
| Parameters | `parameters_c_loc_scale` | `raw_normalized_parameters`, `raw_physical_parameters` |

Do not join A to B using `fit_id`: A has no such field. Do not use B's `original_*` copies instead of the pinned A source records. Check exact expected key sets, no duplicates, legal draw ranges, two baseline quantiles/one translated quantile, consistent offsets/truth, input array dimensions/dtype and inventory integrity before candidate execution. All-draw cohort classification must include refused rows before calculating accepted intersections.

Opened first A and B compressed records with read-only .NET gzip streams; their fields match the harness. Only representative records were decompressed, not full row coverage. Array payloads were not loaded. Thus schema feasibility is directly supported, but full integrity/key coverage remains a future readiness check.

## API/source evidence and limitations

The [official lmoments3 GEV source](https://lmoments3.readthedocs.io/stable/_modules/lmoments3/distr.html) confirms the named parameter return, rational/iterative branches and a built-in non-convergence exception. Its class module cannot identify the raising package; a traceback can. The three-moment `lmom_fit(lmom_ratios=...)` interface is available. This is documentation source review, not wheel execution or a runtime compatibility claim.

Installed `.pixi/envs/default/Lib/site-packages/scipy/stats/_continuous_distns.py:3444` confirms the shared inverse expression. The immutable candidate wheel and effective installed sources still need the design's Stage 1 verification. No upstream or production adapter changes are implied.

Verification scope: rapid / numerical unaffected for this read-only review; `.testing-policy.yml` checked. PowerShell source/JSON reads, SHA-256 hashing of both inventories and original criteria, and representative .NET gzip inspection completed. The dispatched Pixi executable was unavailable and pixi was absent from PATH; parent authorized the read-only .NET alternative. No environment repair attempted. No full suite, fits, branch arithmetic experiment, full inventory rehash or new tests ran. The sole authored file is this review; freeze at handoff.
