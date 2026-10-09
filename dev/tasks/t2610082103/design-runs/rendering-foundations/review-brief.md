# External review brief — rendering foundations, round 1

## Role

You are an independent external design reviewer using a different model variant from the author.
Both are supplied by OpenAI; this run claims independent review, not cross-vendor diversity.
You did not write this design and owe it no deference — no deference to the author, earlier rounds or
earlier approvals. Challenge feasibility and completeness; do not copyedit prose.

## Task

Review exactly one document:

`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-1/.tmp/scratchpad/shared-rendering/design-v2.md`

The design extracts existing Matplotlib fundamentals from a workflow-specific module and migrates
current Python workflow consumers. The workflow engine spans historical climate diagnostics, hydrological
model QA and projection plots. This first packet preserves methods, products and reviewed appearance.

Settled framing, supplied verbatim from status.md — out of scope for your review:

- Python rendering first; R/WF3 alignment is a later integration target.
- Develop a small internal Matplotlib core with a portable dependency boundary before packaging.
- Preserve scientific preparation, established plot styles and existing workflow products.
- First increment: common rendering fundamentals and bounded adoption by active WF0–WF2 callers.
- Prepared-input chart interfaces, map-reference production and external packaging follow separately.
- Stay on session-1/chore/minor-fixes for source work; no landing or push is authorized.

Do not spend findings arguing these should have been decided differently; do raise a finding if a ruling
creates a downstream inconsistency or its implementation fails to satisfy it. Test the written journey
and actor/artifact boundary: does every stage serve a confirmed need, and would a simpler boundary meet
the same outcome? Report mismatches and consequences rather than overriding a ruling.

This is clean-room round 1. Do not read intake, internal reviews, ledger, status or other review artifacts.

## Authority boundary

Read-only. Read the one design above; skim only directly cited source files as needed to verify a
specific premise, at most six source files unless a concrete blocking finding needs another. Do not
broadly inventory the repository. Do not write, edit, commit, spawn agents or run scientific workflows.
The driver captures your final answer. The source is unchanged; baseline rendering may be active in
other processes and must remain untouched.

## Review lenses, in priority order

Domain-content flag: no. No scientific method, data treatment or uncertainty interpretation is proposed.
Review lenses 2–5. If the specification actually introduces such a change, identify that scope defect.

2. Operational feasibility: ambiguous contracts, unimplementable steps, missing inputs, undefined behavior.
3. Failure modes missed: realistic ways the designed system degrades that it does not cover.
4. Over-engineering: costs without value, unnecessary artifacts or stages, simpler ownership boundaries.
5. Gaps: anything this software-system design should cover and does not.

## Evidence burden

Every blocking or major finding must state an observable consequence — what fails, degrades or costs —
not a preference. Cite the design section. An approve verdict cannot coexist with blocking/major findings.
Pending execution is not by itself a finding where a concrete before-edit gate correctly requires it.
Review the design's ability to falsify its claims, not whether implementation has already happened.

## Output contract

Return ONLY a Markdown document, with no preamble:

```text
## Verdict
verdict: approve | revise | reject
doc_version: design-v2.md

## Findings
### ext1-1 [blocking | major | minor]
- section: <design heading>
- finding: <one paragraph>
- rationale: <observable consequence>
- suggested_fix: <concrete change or none>
```

Use stable ext1-N IDs. Blocking means the specified design fails, produces wrong results or cannot be
implemented. Major means meaningful degradation, cost or risk with a clear fix. Minor is worth noting,
at the author's discretion. List highest severity first; do not pad. An empty findings list and approve
is valid. If no findings, state `findings: []`. Keep the report under 1,200 words unless evidence needs more.
