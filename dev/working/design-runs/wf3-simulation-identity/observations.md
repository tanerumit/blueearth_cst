# Process observations — wf3-simulation-identity

Process friction only, never design content. Feeds the post-run retrospective.
The skill is left unchanged for the whole run.

## 2026-09-07 — stage-1 spawn died on resource exhaustion; skeleton-first paid

The `cst-architect` stage-1 spawn terminated with HTTP 429, *"You've hit your
session limit · resets 3:30am (Europe/Istanbul)"*, model `claude-opus-5`. It had
been running ~2 minutes and had completed exactly one action: writing the
`design-v1.md` section skeleton.

Classified per `roles-and-recovery.md` § Classifying a failed spawn as
**resource exhaustion**, not retryable transport — the error names a *limit*, not
a fault. The reference's rung is "stop and surface to the owner; a resume
consumes the same exhausted resource and fails identically". Applied, with one
check the reference does not name: **whether the named reset time had already
passed.** It had — the failure landed at 00:17 local, the owner's next message
arrived at 04:09 Istanbul, and the ceiling resets at 03:30. So the run resumed
without owner escalation, because the resource was no longer exhausted.

Two notes for the retrospective:

1. **Skeleton-first was worth its cost here, and the value was not what the rule
   advertises.** The rule sells it as leaving *resumable work*. The 889-byte
   skeleton contains no design content, so almost nothing was salvaged in
   token terms. What it actually preserved was the **section plan** — the
   author's own decomposition of the deliverable — which is the part a resume
   brief would otherwise have to re-specify or let drift. That is a different
   and better argument for the rule than the one it states.

2. **The exhaustion rung's stop condition is under-specified.** "Wait for the
   limit to clear" is correct, but the reference gives the driver no instruction
   to *read the reset time out of the error and compare it to now* — which is the
   difference between escalating to the owner and simply resuming. A driver
   following the rung literally would have surfaced a resolved problem.
