# Independent external design review: prepared charts, round 1

## Role

You are an independent external design reviewer. You did not write this design and owe it no
deference, including to previous approvals. Challenge feasibility, scientific preservation and
completeness; do not copyedit. Runtime limitation: this is an independent-context GPT review of
a GPT-authored design, not a cross-vendor review. Preserve the same adversarial evidence burden.

## Task

Review exactly this document:
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/.tmp/scratchpad/shared-rendering/prepared-charts/design-v2.md`.

It proposes a small Matplotlib interface for prepared annual and monthly charts used by climate
diagnostics and hydrological summaries. Read this draft as the sole design; this is a clean-room
first external round. Do not read the internal reviews, ledger or conversation history.

**Settled framing — out of scope for your review.** Verbatim from run status:

- Python rendering first, using a small internal core with a portable dependency direction.
- Stabilize annual-series and monthly-cycle interfaces for WF0 climate, WF1 forcing and hydrological summaries.
- Keep scientific preparation in workflow adapters; preserve current appearance and figure-specific exceptions.
- Preserve outputs, captions, configuration and user workflow; maps and external packaging are later increments.
- Continue on the pinned session branch; no landing or push is authorized.

Do not argue these should have been decided differently. Do raise an inconsistency they create or a
failure of the document to implement them. Test the written user journey and ownership boundary:
does each component serve the confirmed need, and would a simpler boundary meet the same outcome?
Report a mismatch and its consequence as a framing issue; do not silently override the ruling.

## Authority boundary

Read-only repository access. Read the named document and, if needed, narrowly inspect files it directly
cites. No broad repository or external research. Do not modify files, run workflows, spawn agents,
install packages, commit or change Git state. The driver captures your final report using `-o`.

## Lenses, in priority order

1. Scientific and methodological validity: can the interface preserve current estimands, ordering,
   gaps, fitted trends and band meaning? Do caller obligations preserve data treatment? Can the
   validation plan falsify these claims? This is preservation, not qualification of existing methods.
2. Operational feasibility: ambiguous contracts, impossible steps, missing inputs or undefined behavior.
3. Gaps: omissions a bounded interface/migration decision must resolve.

## Evidence burden and output

Every blocking or major finding must state an observable consequence, cite the design section and
explain what fails, degrades or costs. A preference is insufficient. Approve cannot coexist with
blocking or major findings. Return only a Markdown document with:

```text
## Verdict
verdict: approve | revise | reject
doc_version: design-v2.md

## Findings
### ext1-1 [blocking | major | minor]
- section: <design section>
- finding: <claim>
- rationale: <observable consequence>
- suggested_fix: <concrete action or none>
```

Blocking: wrong results, unimplementable behavior or invalid scientific assumptions. Major: meaningful
degradation, cost or risk with a clear fix. Minor: worth noting, author's discretion. Use stable
ext1-N IDs, ordered by severity. If sound, return `verdict: approve` and `findings: []`. Do not pad.
