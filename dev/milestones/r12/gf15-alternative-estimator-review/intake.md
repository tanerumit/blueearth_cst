# GF15 alternative-estimator proposal intake

Date: 2026-09-12
Status: active; proposal preparation authorized, method selection provisional
Domain-scientific content: yes — estimator choice, finite-sample error, validity,
numerical invariance and qualification claims.

## Request and authority

Owner request: "continue with the recomended option" in response to:
"I recommend a reviewed alternative-estimator proposal before further fitting
or integration, keeping the current criteria intact."

Prepare a scientifically reviewed method proposal. Existing approval covers
the problem, fixed GF15 criteria, and proposal/review work. It does not select an
alternative estimator or authorize further fitting, dependency installation,
production integration, revised screening policy, or milestone sealing.
G1 will present the concrete provisional alternative and scientific findings;
G2 will approve a converged design. Do not re-request unchanged criteria.

## Problem and scope

The accepted R12 migration is held at GF15 after the original estimator and
normalized candidate B failed the reviewed scientific criteria. Propose a
bounded, reproducible alternative-estimator study that addresses the observed
accuracy and numerical failures, rather than another unreviewed optimizer tweak.
Compare serious alternatives, identify one provisional recommendation with
conditions under which others are preferable, and specify its proposed
qualification and stop rules. Assess whether there is credible evidence that
the fixed accuracy target is attainable; do not imply an alternative will pass
because it is standard or numerically invariant.

This is a method-spec proposal, not implementation or an estimator benchmark.
Literature and read-only source/dependency inspection are authorized. Verify
niche scientific and current software claims using primary papers and official
documentation/source. No new GEV fits or simulation runs are authorized here.

## Constraints and success criteria

- Preserve the exact original matrix and all numerical criteria. Keep error
  denominators at generating scale; refusals count against all 1,000 draws.
- Preserve all predecessor evidence and production files. No fitting fallback,
  shape constraint, prior, threshold or dependency may appear as an unstated choice.
- Compare methods as complete estimators, including invalid-sample/parameter
  handling, shape/sign conventions, quantile route and translation behavior.
- Distinguish IID-fixture accuracy, computational validity, real-bundle
  applicability and operational screening. Do not infer a new screening floor.
- Address the selection effect from repeatedly studying the same retained
  draws. Any proposed additional holdout matrix is new scope, not already run
  or approved; specify that boundary without altering the fixed benchmark.
- A second implementer can identify the exact proposed algorithm/API, inputs,
  controls, expected artifacts, criteria and failure disposition from the spec.
- Give each claimed runtime property a falsifier and identify whether its
  verification exists now or needs a future implementation.
- Target 1,500–2,500 words for the self-contained proposal; more only if the
  contract cannot be stated safely within that range, explaining the exception.

## Repository context and evidence register

All paths below resolve from the repository root. Read relevant headings and
sections, not whole milestone histories.

| ID | Premise | Source / exact observation | Precision / reproduction | Confidence |
|---|---|---|---|---|
| E1 | Original estimator fails the fixed GF15 accuracy and translation gates | `dev/milestones/r12/implementation/evidence/gf15/scientific-handoff.md`: 3/24 baseline accuracy cells pass; all six n=18 cells fail; 118,457/120,000 translation deviations | Exact retained counts; raw records and independent-review.json in same directory | Measured |
| E2 | Exposed status and normalization improve numerical behavior without qualifying B | `dev/milestones/r12/implementation/evidence/gf15-normalized-qualification/scientific-handoff.md`: 132,000 fits; 131,922 accepted; 78 refused; 3/24 baseline accuracy and 6/72 eligible relative cells pass | Exact counts checked by independent-review.py/json; commit 85d0b8b6 | Measured |
| E3 | B retains translation and acceptance failures | Same full-B record: 119,899 numerical passes, 30 numerical failures, 70 both-refused, one changed acceptance; max accepted paired delta 4.526265831472642e-6 against 1e-6 | All 120,000 pairs audited; 186 embedded B cases replay exactly | Measured |
| E4 | Status success does not guarantee accuracy or physical mapped likelihood | Full-B scientific-diagnostics.json: all n=18 baseline fits accepted but all six accuracy cells fail; 974 accepted fits have nonfinite physically mapped public log-density while all normalized-fit evaluations are finite | Raw records retain diagnostics; no retroactive refusal; cause not fully isolated | Measured limitation, cause unresolved |
| E5 | Existing evidence does not fully separate sampling error from suboptimal converged fits | Full-B handoff interpretation and `gf15-investigation/scientific-handoff.md`; robust error summaries and count dependence support a sampling contribution without exhaustive decomposition | Diagnostic inference, not an impossibility theorem | Bounded inference |
| E6 | The fixed qualification and applicability contract remains authoritative | `dev/milestones/r12/wf3-simulation-identity-design.md` section 7.5; exact `gf15/results/criteria.json` | 12 shape/count cells x1,000 retained draws; 132,000 fits/144,000 quantiles; criteria byte-exact across B qualification | Owner-approved |
| E7 | Production uses xclim/SciPy GEV fit and immutable metric identities | `blueearth_cst/experiment/metric_registry.py`, `blueearth_cst/shared/metrics_definition.py`, R12 design sections 7.5 and 8.4 | Inspect current source; production unchanged by diagnostic records | Read-only source premise |
| E8 | A replacement may improve fixed-matrix performance but adequacy is unknown | No alternative estimator has been executed under this proposal | Falsifier: a prospectively specified independent implementation and full fixed-matrix qualification; a failure must remain a failure | Hypothesis, untested |
| E9 | Installed xclim exposes PWM and MPS paths, but availability is not the same as a frozen usable candidate | Read-only `.pixi/envs/default/Lib/site-packages/xclim/indices/stats.py`: PWM delegates to an lmoments3 distribution; MPS calls scipy.stats.fit(method="mse") and requires finite parameter bounds. `pixi.lock` lists lmoments3 only under xclim `constrains`; no `*lmom*` package directory was found in this environment | Source inspection on 2026-09-12, not an import or fit test; author must verify API/package details before recommending | Observed interface / bounded availability check |

## Gate materialization

| Gate | Current availability | Boundary |
|---|---|---|
| Original/B evidence integrity | Runnable: independent-review.py in full-B evidence against its results, output to an absent scratch path | Already passed for all fits/rows/cells; rereading counts is not a new benchmark |
| Method/implementation availability | Read-only repository and official source inspection | No installation, fitting or network execution of package code |
| Alternative analytical/translation controls | Needs proposed implementation; author supplies falsifiers, not invented working commands | Mark planned and bind to future implementation brief |
| Alternative full fixed matrix | Inputs/criteria already retained; alternative runner does not exist | New owner execution authorization required after reviewed proposal |
| Production integration / identity / seal | Separate later scope under existing R12 validation map | No implicit authorization or adequacy claim from proposal convergence |

## Derived-artifact register and placement

| Artifact | Owner | Action after reviewed decisions |
|---|---|---|
| `dev/tasks/t2609100916-r12-accepted-design-implementation.md` | Driver | Record authorized scope, review state and remaining gate |
| R12 implementation `master-brief.md` and `validation-map.md` | Driver | Link final proposal and record acceptance; preserve earlier failures |
| Future implementation brief | Not yet created | Derive only from accepted method spec; no speculative implementation task |

Run home: `dev/working/design-runs/gf15-alternative-estimator/`, per dev/README.md.
Proposed durable destination after approval:
`dev/milestones/r12/gf15-alternative-estimator-design.md`, a frozen milestone
method proposal with append-only review history. The author edits only its
versioned design and assigned ledger; the driver owns run state and trackers.

## Evidence-register correction — 2026-09-12 full-panel check

E6's phrase "criteria byte-exact across B qualification" overstated the prior
check. Repo-fit inspection confirms decoded JSON equality, not byte equality:
A criteria SHA-256 988611b6d239b95f7542f8d67470395e4997ac61dd97198fd075fdcba552d643;
B copy SHA-256 0181b4a1044c66ab4c819fded1ae39d35608ea375ddc46bdaf2d87587714ddca.
The scientific criteria are unchanged. Future qualification must preserve A's
original bytes as v2 already requires. Do not rewrite predecessor evidence.
Authority/source: internal-review-repo-fit.md, exact input anchors and cited
independent-review.py equality check. E6 is supported as semantic equality only.
