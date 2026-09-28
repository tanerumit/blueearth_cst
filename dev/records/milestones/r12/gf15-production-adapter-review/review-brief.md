# External review contract — GF15 production adapter

Contract fixed for this run. Round/version and settled framing below are dispatch
state, updated from status.md before each round. Reviewer has no prior authorship.

## Dispatch

Round: 1 (clean-room)
Document: `C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3/dev/working/design-runs/gf15-production-adapter/design-v2.md`
SHA256: `c83245ba06a412d5a38a00c138f7268e04da9a342d37e49c7f231440a32c5ef6`

The design maps a fixed L-moment GEV candidate into a workflow's retained-response
metric stage, packages bounded benchmark evidence, and preserves immutable metric
identity and old-set reading. It proposes provisional operational point estimates.
This is a design review, not a request to implement or perform scientific runs.

## Settled framing

- Owner G1 approved Option A on2026-09-13: fixed candidate C integration for provisional operational estimates with complete report/metadata/identity, compatibility, isolated setup and snapshot/parity gates.
- Owner approved policy gf15-accuracy-8x-v1: retained-matrix assessment at median.80, upper/lowerP90 4/2 in scale and eligible relative coordinates. Threshold choice is settled; no fresh-data or real-bundle adequacy claim follows.
- Existing member-local extraction and provisional screening ratio1/floor10 remain fixed. Actual-bundle adequacy stays unestablished; a new empirical validation program is outside this integration scope.
- G1 accepted the unbiasedness wording clarification and keeping production parity explicitly outstanding. G2 production design acceptance has not occurred.

Do not argue settled choices should have been different. Raise downstream
inconsistencies or failure to implement their required limits.

## Role and authority

Act as an independent cross-vendor domain referee, with no deference to the
author or prior approvals. Read the named design. You may inspect repository
files/evidence directly cited by it when needed to settle a premise. Do not
read broadly, access credentials/private unrelated material, or modify anything.
Do not open prior reviews, ledger, index, intake or status, even when the draft
links them: round1 is clean-room and settled framing is fully supplied above.
No external web access, computation tools, shell, edits, nested agents or workflow
execution are exposed. Do not invent results when evidence is unavailable.

## Lenses

1. Scientific/methodological validity: mapping fidelity, assumptions, physical/statistical semantics, uncertainty and falsifiable validation appropriate to the approved limited scope.
2. Operational feasibility: would the specified contracts work, with available declared inputs and explicit prerequisite gates?
3. Gaps: missing design content with a concrete consequence for this integration.

Do not copyedit or pad findings. An unexecuted prerequisite already honestly
gated is not itself proof the design fails. Distinguish existing gaps from
regressions or omissions the proposed mechanism introduces.

## Evidence and verdict contract

Blocking = design would fail, produce wrong results or cannot be implemented;
major = meaningful degradation/risk with clear fix; minor = worthwhile detail.
Every blocking/major finding must name an observable consequence and its design
section, not a preference. Approve may not coexist with blocking or major findings.
Name every finding ext1-N, never reuse IDs. If sound, approve with no findings.

Return ONLY a Markdown review, beginning with YAML frontmatter:

```yaml
---
verdict: approve | revise | reject
doc_version: design-v2.md
findings:
  - id: ext1-1
    severity: blocking | major | minor
    section: exact heading
    finding: claim
    rationale: observable consequence
    suggested_fix: concrete change or none
---
```

Use `findings: []` if none. Supporting reasoning may follow. This output will be
captured verbatim; it is not a cryptographic signature or production acceptance.
