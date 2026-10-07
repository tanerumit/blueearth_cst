# Internal review index — design-v1.md

Lenses: `internal-review-domain.md` (stage 1b, model-validator, verdict revise) and
`internal-review-risk.md` (stage 2, critical-thinker, verdict revise). Lean panel. Every original ID is listed
by reference; the review files are authoritative for each finding's text, severity and suggested fix. Nothing
is re-graded or merged away.

## Findings by concern

| Concern | IDs (severity as filed) |
|---|---|
| Analysis vs configured windows; reference choice | dom-1 (major) — ruled at G1 |
| Window placement near data ends, join, water year, per-model data ends | dom-2 (major) — ruled at G1; risk-3 (major); dom-10 (minor) |
| Variability ratios: noise band, pooling weights | dom-3 (major), dom-4 (major) — both ruled at G1 |
| Dry-reference rule | dom-5 (major), risk-2 (major) — **see Conflicts** |
| Sign agreement: noise, family dependence, labelling | dom-6 (major) — ruled at G1; dom-12 (minor) |
| Validation: known-answer tests; parity scope | dom-7 (major), risk-6 (major) |
| Captions and labelling | dom-8 (minor), dom-9 (minor) |
| Unlisted model families | dom-11 (minor) — ruled at G1 |
| Declared figures vs undrawable products | risk-1 (major) |
| Commit plan ordering and testability | risk-4 (major) |
| Rule 2.05 figure-list param re-runs | risk-5 (major) |
| Stage-B hash discipline | risk-7 (minor) |
| WF0 token coupling | risk-8 (minor) |
| Baseline manifest and stale project files | risk-9 (minor), risk-10 (minor) |

## Conflicts

**Factual/approach contradiction — which dry-reference rule the new analysis rows use.**
- dom-5 (`internal-review-domain.md:88-113`): apply ONE rule to all analysis rows, **per period keyed on the
  reference mean** (the lab rule, `wf2_lab/core.py:302-321`), as a post-process of the kernel's analysis-slice
  output; kernel and aligned CSV untouched; aligned CSV keeps the kernel's per-statistic rule.
- risk-2 (`internal-review-risk.md:30-49`): implement dom-5 by applying **the kernel's existing per-statistic
  rule** (`get_change_climate_proj.py:249-251`) inside the new seasonal/CV code only; kernel untouched.
- Agreement: both forbid editing the kernel and both ask for a synthetic dry-reference test. Disagreement:
  which rule governs the new rows (mean-keyed per period vs per statistic). Under dom-5 the monthly analysis
  rows come from the kernel (per-statistic) and are post-processed to the mean-keyed rule; under risk-2 the
  analysis table follows the kernel rule everywhere and matches the aligned CSV's semantics.
- Cheap settling evidence: a synthetic month with reference mean ≥ 0.1 mm/day and reference SD < 0.1 mm/day —
  the rules disagree exactly there (dom-5 rationale); the author should state which behaviour the figures need
  and why.

**Scope interaction (not a contradiction) — parity tolerance vs G1 method changes.** dom-7 asks for known-answer
tests beyond lab parity; risk-6 asks to restrict parity to unchanged tables/columns. Complementary; both apply.

**Severity divergences:** none (the overlapping concerns are both graded major).

## G1 status of findings

Ruled at G1 (accepted, to be implemented in r1): dom-1, dom-2, dom-3, dom-4, dom-6, dom-11; accepted by the
driver as correctness fixes: dom-5, dom-7 (dom-5's mechanism is subject to the conflict above). All other IDs
are open for the author's disposition. No finding admits a scope-divergent resolution; no gate return.

## Extension after promotion (full panel on design-v2.md)

Added lenses: `internal-review-architecture.md` (general-purpose, verdict revise; arch-1..6) and
`internal-review-repo-fit.md` (python-engineer, verdict revise; fit-1..11). External round 1:
`external-review-r1.md` (verdict revise; ext1-1..4). Review files are authoritative.

| Concern | IDs (severity as filed) |
|---|---|
| Runtime product availability vs parse-time declaration | ext1-2 (major), arch-2 (major) — **see Conflicts (2)** |
| Variability null band validity per panel | ext1-1 (major) |
| Zero / degenerate variability | ext1-3 (major) |
| Season-year boundaries and completeness | ext1-4 (major) |
| Commit plan: 5a breaks Snakefile load | arch-1 (major) |
| Shared analysis-window folders: table keying | arch-3 (major) |
| Tree inventory `analysis/` tier | fit-1 (major) |
| Retired code's tests | fit-2 (major) |
| Validation ladder (test-full, test-e2e scope) | fit-3 (major) |
| Live docs and rule-index sections | fit-4 (major) |
| Figure count formula; availability placement; helper placement | arch-4, arch-5, arch-6 (minor) |
| WF2_TARGETS; script-body conventions; save path; console rows; hydromt import timing; package data; identity wording | fit-5..fit-11 (minor) |

## Conflicts (2)

**Approach divergence — where final product availability is decided.**
- ext1-2 (`external-review-r1.md:13-18`): decide availability after reading and validating the series; let
  rendering consume that result; use an owned figure directory plus a manifest, or a checkpoint.
- arch-2 (`internal-review-architecture.md`, arch-2): either record each member's data end in the sidecars so
  availability is computable at parse time, **or** let 2.06 own a per-window directory with the captions
  manifest as the declared contract.
- Overlap: both reject the current "declare at parse time from POINTS, raise if empty" rule. Divergence:
  arch-2 keeps a parse-time option (data ends in sidecars); ext1-2 says parse-time inputs cannot establish
  usable observations or valid ratios (only run time can). Settling evidence: whether any availability
  condition depends on values (valid ratios, paired points, non-degenerate variability — ext1-3) rather than
  on spans; if yes, only the run-time boundary covers it.

No finding admits a scope-divergent resolution relative to the G1 rulings (no placeholders; unavailable listed
with reason): both options keep that. No gate return.
