---
run: prepared-charts
target-repo: blueearth_cst
genre: decision-record
author-binding: cst-architect
started: 2026-10-10
variant: lean
stage: G2
external-rounds-completed: 1
allocation: "Frontier allocation below"
dispatches: 7
gates:
  G1: approved 2026-10-10
  G2: pending
flags: [canonical-board-on-main, same-provider-review, external-review-owner-authorized]
---

# Prepared charts review state

## Framing authority

The user approved the saved four-stage plan, including prepared-input charts, and explicitly directed
continuation to this stage. As in the foundations run, use that approval for settled problem, scope and
constraints. Confirm the draft stays within that direction after the pre-G1 scientific review; record
its concrete tree and user-facing inventory. A material departure requires a new framing decision.
Exact interface/design bytes remain subject to G2; prior approval is not exact-version approval.

## Frontier allocation

Planning-only dispatch `chart_allocation`: default role, requested GPT-6 Astra/high. Effective settings
not exposed; no measured token or cost data. Root integrates. At most two workers; one source writer.
Prior caption diagnostics support bounded serial writers; they establish no measured savings.

| Work | Role | Requested model/effort | Ownership / ceiling |
|---|---|---|---|
| Draft/revisions | cst-architect, fresh each stage | gpt-6-astra/high | One design plus ledger |
| Scientific lens | model-validator | gpt-6-astra/high | One immutable report |
| Risk lens | critical-thinker | gpt-6-astra/high | One immutable report |
| External lens | headless Codex | gpt-6-astra/high | One captured report |
| Implementation after G2 | python-engineer | gpt-6.1-sol/medium | At most six source files |
| Visual acceptance | dataviz-designer | gpt-6.1-sol/medium | Two evidence files |
| Integration/evidence | Root | Inherited; unverified | Docs, run state, final verification |

Conceptual fallback: appropriate transport retry with same frontier choice, otherwise hold and report.
Scientific fallback role: cst-architect with the domain-review contract, same frontier allocation.
Implementation/visual escalation: Astra/high for unresolved reasoning, not for unavailable data/tools.
Optional full panel follows skill promotion rules; architecture Astra/high, Python repo-fit Sol/medium.
Reopen a packet only for a failed falsifier or changed contract. No routine scope accretion.
All models are GPT family: review is independent-context same-provider, not cross-vendor.
Implementation ceiling reserves a new module and three known callers; no persistent figure-only tests.
Nearby documentation and evidence are root-owned. No dispatch inherits permission to spawn others.

## Stage log

- [done] 0-intake — intake.md; source inspection and existing baseline inventory completed.
- [done] 1-draft — design-v1.md, 1,929 words; four-source-file packet and explicit API.
- [done] 1b-domain — approve v1, zero findings; supplement corrects E7's disposition.
- [done] G1 — existing owner approval of Stage 2 framing applies; v1 retains that scope.
  Scientific lens raises no framing findings. Concrete tree: one prepared_charts.py addition,
  three caller edits, nearby docs. No product names, config, commands or user steps change.
  Displayed/retained v1 SHA256: ed2f9691aff7886698883a6087c13ab1cf78abff10e706d89924baa78fd6186e.
  This records continuation authority, not a claim that the owner reviewed the detailed API bytes.
- [done] 2-risk — approve v1, zero findings; internal-review-index.md retains scientific correction.
- [done] 3-revision-r1 — fresh author captured byte-identical v2; root verified exact bytes/hash.
- [blocked] 4-external-r1 — automatic approval review rejected process launch; no review ran.
  Private design/repository context transmission needs explicit owner approval before retry.
- [done] External payload approval — user answered "yes" to sending this design, directly cited
  source context and repository instructions to OpenAI through codex exec for independent review.
- [done] 4-external-r1 resumed — approve design-v2.md, zero findings; explicitly authorized launch.
- [done] 5-convergence-r1 — external verdict names v2; all internal/external findings lists empty.
  Domain correction changes only the premise-disposition wording, not design or findings.
  No findings need disposition; explicit empty closure verified, no ledger or revision required.
- [open] G2 — owner approval of exact reviewed v2 is pending. Implementation has not started.

Scientific, risk and independent external reviews contain zero findings. Design review has converged.
No exact-design implementation approval is recorded; no empty ledger is created.

Stage 3 allocation narrowed after empty reviews: a byte-identical capture needs no conceptual work.
Request cst-architect on gpt-6-luna/low, fallback gpt-6.1-sol/low; no edits to approved framing or text.
Fresh author requirement remains in force. This replaces only the stage-3 effort/model allocation.

## External dispatch identity

The settled-framing block below is supplied verbatim in `review-brief.md`.
Design v2 SHA256: `ed2f9691aff7886698883a6087c13ab1cf78abff10e706d89924baa78fd6186e`.
Fixed brief SHA256: `97565f84048358c75985ee9b07a16495cdbcc858e21879b28cfa5f99a5fbae85`.
No supplement or sketch. Both files are retained unchanged for dispatch recovery.
Requested model/effort: gpt-6-astra/high; approval never, sandbox read-only, ephemeral.
Same-provider limitation remains explicit in the brief. No implementation authority added.

The first launch was rejected before process creation by automatic approval review:
"The headless review may transmit private design and repository context to an external model service;
the user authorized delegation generally but not this specific sensitive payload to that destination."
No external process ran for that first attempt. The owner then explicitly authorized the payload,
and the same execution route succeeded. The rejection was not bypassed. No run datasets were sent.
The completed external report is `external-review-r1.md`; approval never and read-only sandbox were
confirmed in the runtime banner. G2 remains pending after this successful review.

## Converged review and approval identity

Exact revision: `dev/tasks/t2610082103/design-runs/prepared-charts/design-v2.md` on main.
SHA256: `ed2f9691aff7886698883a6087c13ab1cf78abff10e706d89924baa78fd6186e`.
The retained v1/v2 bytes are identical, including the original proposed header; status owns lifecycle.
Independent report: approve, doc_version design-v2.md, findings empty. Internal domain/risk approvals
and domain supplement were reconciled; no contested premises remain except future empirical parity,
explicitly a falsifiable implementation hypothesis rather than a validated runtime claim.
No stage-6 revision or second external round is needed after an approval with empty findings.
Next action: owner approves these exact bytes for implementation, then claim-to-falsifier handoff.

## Allocation diagnostics — external review completed

The owner-authorized retry completed the fifth planned pre-G2 worker packet. Total observed dispatch
calls are seven: four original worker packets, one domain clarification, one rejected launch and one
successful external review; the separate planning bootstrap is excluded. No new agents or design edits.
External effective settings confirmed: gpt-6-astra/high, OpenAI, approval never, read-only sandbox.
CLI exit code: zero. CLI-reported token usage: 44,861 for this external review; cost and savings unknown.
Source tree remained clean after review. No broader tests or renders were run for a document-only step.
All scope ceilings held. Prior rejection remains historical evidence; authorization block is resolved.

## Allocation diagnostics — checkpoint before external review

Run/task: prepared-charts / t2610082103; lean design-review-loop. Planned pre-G2 worker packets: five
(draft, domain, risk, revision, external), plus one planning-only bootstrap. Observed: four completed
worker packets, one domain clarification follow-up, one rejected external launch; bootstrap completed.
The frontmatter dispatch count includes the clarification and rejected launch, excludes bootstrap.

Requested: planner/author/domain/risk Astra/high; mechanical revision Luna/low; external Astra/high.
Effective worker settings unverified; external process never started. One writer per artifact;
no source files changed. Ceiling held. Internal design rework: zero; review-schema correction: one.
External permission escalation: one rejection, no retry. Reviews retained verbatim with supplement.
Token usage, monetary cost and savings are undetermined. Planner overhead and total elapsed time
were not instrumented; no measured cost reduction is claimed. The first-use pilot was already recorded
in the preceding packet and was not repeated. Integration and later implementation remain root-owned.

## Settled framing for review

- Python rendering first, using a small internal core with a portable dependency direction.
- Stabilize annual-series and monthly-cycle interfaces for WF0 climate, WF1 forcing and hydrological summaries.
- Keep scientific preparation in workflow adapters; preserve current appearance and figure-specific exceptions.
- Preserve outputs, captions, configuration and user workflow; maps and external packaging are later increments.
- Continue on the pinned session branch; no landing or push is authorized.

## Execution evidence

- `chart_design`: cst-architect, fresh, requested Astra/high; one design, no source authority.
- `chart_domain_review`: model-validator, fresh, requested Astra/high; one report, no design/source edits.
  One evidence-only follow-up requested a schema correction: its E7 disposition said untestable while
  its prose correctly treated E7 as a testable prospective hypothesis. Original report stays immutable;
  reviewer writes an addendum before scientific closure. No design or source rework.
- Import/materialization probe passed via `pixi run python -c ...`: Python 3.12.13,
  Matplotlib 3.11.0; diagnostic_figures, forcing_figures and func_plot_signature imported.
  Existing caption candidate has 158 PNGs; WF1 candidate has 15 PNGs. No new render pass claimed.
- `codex --version`: 0.162.0, same CLI version as this session's successful read-only sandbox probe.
  Reuse `.tmp/scratchpad/shared-rendering/sandbox-preflight.log`: effective approval never,
  read-only sandbox, owned sentinel write denied. The forthcoming external invocation must use
  the same explicit flags and check its banner. PATH-alias temp cleanup warnings are not review results.
- Session identity matches the pinned branch. Main lag consists of task documentation; no follow-up
  synchronization or source changes. Primary checkout was clean before saving this run's intake/state.

## Installed contract provenance

Repository: `C:/Users/taner/workspace/brain-infrastructure`. Recoverable commit: `1c50048ae051faa7dfb2e8b5edfea83dc83fac9a`.
Installed bytes were compared with the pinned Git blobs, not inferred from version labels.
Resume selects these recorded bytes; host permissions still apply.

| Path under artifacts/skills/design-review-loop | SHA256 |
|---|---|
| SKILL.md | d05a6677273450bda8c20151ff51e79f2777bd41d8ec5122646429bca48e0793 |
| references/stage-contracts.md | 8d27819b4734e166afe94d4c1963afe31a5ff783ba64da8d6d914fade670809e |
| references/run-artifacts.md | 8b42b93bbf7cc8eecd7abaf4d0e384530491b09e835581ac2a703213dc0ce379 |
| references/roles-and-recovery.md | 946626b61a7b062bc5cd2c3f87810b5f5bae74d1cb9efd4deff96be6985a61d7 |
| references/evidence-and-gates.md | da14f1cba3a2ffb482c8856000849c911d0e13e22fda76a5f3bc42d9d3cd3830 |
| references/journey-and-sketch.md | c53f7ae05e2711db959b507f2ccb4ffe923d1facb92eea04a3c8c0740ae14022 |
| references/findings-and-closure.md | 55f23a42ffc4ef1ad0cfbe38b87af54b49c1c652038bb51d726cb987b263dbc1 |
| references/external-review-brief.md | 0d8a7a3ef805af02c74c0a97bf1dd1c2cfe20b2d1c59dcf1eb66f632613cfbcf |
