# Scoped verification brief — WF2 starter-suite integration, design-v3.md delta

## Role

You are an independent external reviewer from a different model family than the author. You reviewed the
previous version (design-v2.md) in round 1 and raised ext1-1..ext1-4. This is NOT a full re-review: it is a
scoped verification pass over the revision's delta. Owe the author no deference. Do not copyedit prose.

## Task

Read, in this order:

1. `C:\Users\taner\workspace\blueearth_cst\dev\tasks\t2610071652\design-runs\wf2-suite-integration\design-v3.md`
   — read § 14 "Revision log (v2 → v3)" first, then the changed sections: § 4 (figure contract), § 5.7 (null
   band), § 5.11 (season-year contract), § 5.12 (degenerate variability), § 6.1 (availability), § 9
   (validation), § 10 (commit plan). Read other sections only as needed to judge consistency with the delta.
2. `...\wf2-suite-integration\external-review-r1.md` — your round-1 findings.
3. `...\wf2-suite-integration\ledger.md` — the author's dispositions (rows ext1-1..ext1-4, arch-1..arch-6,
   fit-1..fit-11 are new in v3).

**Settled framing — out of scope** (owner rulings, 2026-10-07): port analysis and revised figures into WF2; one
calculator, aligned change factors byte-identical; lab figure style for WF2; 30-water-year analysis window with
both window pairs recorded and captioned, configured reference used when ≥ 30 years; late horizons shift to
fit the data end keeping 30 years; variability ratios carry a no-change sampling band; pooled member ratios
weighted 1/members-per-model; sign agreement adds family counts, a small-change marker and count-not-likelihood
wording; unlisted models get a provisional family; no placeholder figures (undrawable products listed with
reason); combined cloud only with ≥ 2 horizons; future folders named by analysis-window years; the family table
ships only if its licence permits.

## Duties (scope)

- **Regression duty:** for each of ext1-1..ext1-4, verify the fix in v3 actually resolves your finding; say
  `resolved` or re-raise it. Only you may withdraw your earlier findings.
- **Delta duty:** check that the new mechanisms (run-time availability decided in rule 2.05b with owned
  `directory()` figure outputs plus a captions manifest; per-panel Monte Carlo null bands; new degenerate
  statuses; season-year contract; revised commit plan) are feasible, internally consistent with the rest of the
  document, and introduce no new defect. Apply lenses: scientific validity, operational feasibility, gaps.
- Do not raise findings about unchanged parts of the design unless the delta made them inconsistent.

## Authority boundary

Read-only. Read the files listed; you may skim files the design directly cites for the changed sections. Modify
nothing.

## Evidence burden and output contract

Every `blocking`/`major` finding states an observable consequence and cites the section. `approve` may not
coexist with a blocking/major finding. Return ONLY:

    ## Verdict
    verdict: approve | revise | reject
    doc_version: design-v3.md

    ## Regression
    - ext1-1: resolved | re-raised as ext2-<n>
    - ext1-2: ...
    - ext1-3: ...
    - ext1-4: ...

    ## Findings
    ### ext2-<seq>  [blocking | major | minor]
    - section: <design heading>
    - finding: <one paragraph>
    - rationale: <observable consequence>
    - suggested_fix: <concrete change, or "none">

Severity: `blocking` = would fail, produce wrong results, or cannot be implemented; `major` = meaningful
degradation or risk with a clear fix; `minor` = discretionary. An empty findings list with `approve` is valid.
