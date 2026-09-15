# Scoped verification of design v5

This is the design-review-loop verification of the v4-to-v5 delta after external
round 1. It is not a second full external round. The driver dispatches this
brief only after the author releases v5 and both round-2 triggers are checked.

## Task and inputs

Act as an independent scientific/methodological and architectural verifier.
Use Astra under the owner's scientific-evaluation ruling. You did not author
this revision. The author also used Astra; independence here is a fresh review
context, not model or vendor diversity. No nested delegation.

Read these files in this run directory:

- `external-review-r1.md`: authoritative original `ext1-1` through `ext1-4`.
- `design-v4.md`: the reviewed base version.
- `design-v5.md`: the candidate whose delta you must verify.
- `v4-v5.diff`: driver-captured delta, checked against both files.
- `ledger.md`: read the new v5 dispositions for those four external IDs.

Review only those changes and their necessary cross-references/interactions.
Inspect directly cited factual repository sources when needed to test a premise.
Do not seed findings from unrelated prior reviews, old ledger dispositions,
review indexes, or status. Do not re-review unchanged decisions or copyedit.

For every external ID, determine whether each accepted fix actually resolves
the finding, whether the resolution introduces a defect, and whether its
scientific claims and validation criteria are justified at design stage.
Assess new mechanisms introduced by the delta, including their compatibility
with independently runnable workflows and the agreed identity boundaries.
Distinguish a missing execution result from a false claim of execution; this
review does not authorize scientific runs or implementation.

## Settled scope

Two workflows, three stages; production stochastic scenario type and Wflow only;
terminal CMIP overlay; no local calibration, third workflow, second production
provider or general execution-control framework. Approved terminology and
R-1 through R-6 remain as stated in the design. GEV screening values and new
scientific benchmark criteria remain provisional; no automatic estimator change,
ratio-2.0 substitution, partial-year removal or fit intervals is approved.
Historical Class-B interval deferral remains a distinct G2 owner ruling.

The owner approved revising the contracts; that approval is not evidence that
the revision meets them. Raise any concrete inconsistency introduced by a fix.

## Authority and output

Read-only, no file writes, commits, delegation or execution of simulations.
The driver captures your final response. Return a Markdown report with:

```yaml
verdict: approve | revise | reject
doc_version: design-v5.md
scope: v4-to-v5 delta resolving ext1-1 through ext1-4
```

Then a verification table with one row per original external ID, its resolution
status and evidence. New findings use stable IDs `delta-v5-1`, etc., with
severity `blocking | major | minor`, section, finding, observable rationale,
and concrete suggested fix. If a prior finding survives, identify its original
ID explicitly; do not silently withdraw or re-grade it. No approval with a
blocking or major finding. `blocking` means would fail, produce wrong results
or cannot be implemented; `major` means meaningful observable degradation/risk
with a clear fix; `minor` is discretionary. An empty finding list with approve
is valid when the changed contract is sound.

Conclude with any still-unexecuted empirical gates required for implementation
or scientific acceptance, keeping those separate from defects in the design.
