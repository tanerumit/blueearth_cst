---
run: expert-model-revisions
target-repo: blueearth_cst
genre: decision-record
author-binding: cst_architect
started: 2026-09-28
variant: lean
stage: G1-framing
external-rounds-completed: 0
allocation: "Frontier plan: coordinator gpt-6-astra/high (effective unverified); author cst_architect gpt-6-astra/high; domain model_validator gpt-6-sol/high; risk critical_thinker gpt-6-astra/high; external headless codex exec gpt-6-astra/high. Fallback sol/high for architectural stages; max two active agents; no nested delegation. See stage log for observed settings."
dispatches: 3
gates:
  G1: pending
  G2: pending
flags: []
---

- [done] 0-intake — outputs: intake.md; design-scoping confirmed full revisions and recipe plus direct-edit support.
- [done] 1-draft — outputs: design-v1.md
- [done] 1b-domain-review — outputs: internal-review-domain.md (verdict: revise; 3 major framing findings, 2 minor premise findings)
- [open] G1-framing — awaiting user ruling on provisional alternative and domain-1..3

Owner paused the run on 2026-09-28 to resume later. Board item: `dev/tasks/t2609281102-complete-reviewed-expert-wflow-model-revisions-design.md`. Do not advance G1 without an explicit ruling.

The planning-only dispatch (`gpt-6-astra`, high) produced no stage artifact. The external reviewer and later gates remain pending.

Stage 1 author dispatch: `cst_architect`, requested `gpt-6-astra` high; effective settings unverified.
Stage 1b domain dispatch: `model_validator`, requested `gpt-6-sol` high; effective settings unverified.
