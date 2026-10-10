# Review allocation

2026-10-10: coordinator plans inline; frontier capability follows the runtime GPT-6 family declaration.
Exact parent model/effort is not observable here. Driver/integrator: /root. Max live review workers: 1.
Author preferred: gpt-6-astra/high; fallback gpt-6.1-sol/high for retryable transport only, with recorded
capability check. Requested/effective settings are distinguished; effective is unverified until reported.

| Task | Role | Preferred model/effort | Dependencies and ownership | Acceptance |
|---|---|---|---|---|
| Draft + inventory | cst_architect | gpt-6-astra/high | Intake; two owned files | Complete self-contained v1 |
| Domain lens | cst_architect | gpt-6-astra/high | v1; domain review only | Premise dispositions + findings |
| Risk lens | critical_thinker | gpt-6-astra/high | G1; risk review only | Refutable assumptions |
| Revisions | cst_architect | gpt-6-astra/high | Review artifacts; next version | Original IDs dispositioned |
| External review | Headless Codex | Probe supported model first | Reviewed design; immutable output | Named verdict |

Owner fast-track override, 2026-10-10: after the domain-finding revision, dispatch one independent
critical_thinker combined risk/feasibility review at gpt-6-astra/high. This replaces the separate risk
and headless external stages; single-provider review is the disclosed limitation. One round maximum;
no optional architecture/repo-fit workers or promotion. Sequential dispatch;
no nested delegation. Reopen a packet only for a failed falsifier or changed contract. Driver alone
integrates gate state. No human gate added by allocation. Preserve independent fresh-context review;
surviving blockers return to the owner under the cap instead of another round.

First-use compliance benchmark: record dispatch timing, requested/effective configuration, model usage
if available, and rework in status. Pricing and comparable baseline unavailable; savings undetermined.
