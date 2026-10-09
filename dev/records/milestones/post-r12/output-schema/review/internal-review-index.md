# P0 internal review index — design-v1.md

All four immutable lens reports returned `revise`. This index groups concerns; the reports retain each original finding's exact claim, severity, rationale and suggested fix. No finding is re-graded here.

| Concern | Original findings | Next revision boundary |
|---|---|---|
| Scientific comparator and source dependence | [domain-1](internal-review-domain.md), [domain-2](internal-review-domain.md), [domain-3](internal-review-domain.md), [domain-4](internal-review-domain.md) | Name a predecessor WF4 comparator, classify CHIRPS cold-store elevation, separate unit evidence from simulation identity, mark unexecuted premises. |
| Identity and pinned execution | [risk-1](internal-review-risk.md), [risk-2](internal-review-risk.md), [risk-4](internal-review-risk.md) | Define path-neutral response projection, creator-versus-candidate reuse binding, and immutable scientific input consumption. |
| Archive and reference closure | [risk-3](internal-review-risk.md), [arch-1](internal-review-architecture.md), [arch-2](internal-review-architecture.md), [arch-3](internal-review-architecture.md), [arch-4](internal-review-architecture.md) | Close rollback state, creator archive edge, predecessor rerun anchor, in-document temporal reference, and generated-YAML ordering. |
| Runnable phase and launch coverage | [repo-1](internal-review-repo-fit.md), [repo-2](internal-review-repo-fit.md) | Require pre-parse byte capture for new-schema WF0–2, and preserve a runnable WF3 handoff until P5 switches it. |

## Conflicts

No factual contradiction or severity divergence between lenses was identified. The two blocking findings, risk-1 and repo-1, have recommended resolutions within the owner's selected scope. Weakening path-neutral identity or dropping exact source capture would change that scope and return to the owner framing gate.

## Evidence state

The clean pre-change reference is in progress under `.tmp/scratchpad/2026-09-21_1541/prechange-wf3-reference/`. A cold WF3 dry-run passed after local source-cache routing; no scientific parity result is claimed yet. The four reviews are design judgments, not implementation verification.
