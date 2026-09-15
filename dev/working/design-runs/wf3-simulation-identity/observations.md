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

## 2026-09-07 — the ledger has no disposition for "major, correct, deliberately not closed"

`domain-7` (major — no fit uncertainty crosses the seam) is filed `deferred`.
`findings-and-closure.md` § Ledger rules says **"`deferred` is valid only for
`minor`"**, so the row is out of grammar as written.

The author's reasoning is the right instinct and is recorded in the row itself:
the finding is correct, the design states its position, and the *substantive gap
is not closed* — so filing it `accepted` would certify a fix that does not exist,
which is precisely what the disposition column is for preventing. But the enum
offers only `accepted` / `rejected` / `deferred` / `withdrawn`, and:

- `accepted` would be false;
- `deferred` is barred at this severity;
- `rejected` reads as "the objection does not hold", which is not the author's
  claim — the author agrees with it.

**Driver resolution for this run:** treat it as a de facto `rejected` for
*process* purposes only — i.e. route it to the user for ratification no later
than G2, which is exactly what `findings-and-closure.md` requires of a rejected
`major`, and what § Convergence requires anyway ("adjudicated by the user"). The
ledger row's own text is left as the author wrote it, because it is more accurate
than any enum value available.

**Candidate for the skill:** the enum needs a fifth value, or `deferred` needs to
be admissible at `major` **with a mandatory user ratification** attached. The
present rule pushes an honest author toward one of two misrepresentations, and
the more likely one — `accepted` — is invisible at the gate, because an accepted
row is exactly what a driver's structural check is looking for. A rule that makes
the honest disposition unavailable does not eliminate the case; it hides it.

## 2026-09-07 — `codex exec` exits 0 on a quota refusal, writing no output file

The round-1 external dispatch returned **exit code 0** while producing no `-o`
file at all. The log's last two lines were:

```
ERROR: You've hit your usage limit. ... try again at Sep 8th, 2026 12:53 AM.
```

Caught by verifying the artifact exists rather than by trusting the exit status.
A driver that marked the stage `[done]` on exit 0 would have recorded a completed
external round with no review on disk — and `run-artifacts.md`'s reconcile rule
calls recorded-but-missing **corruption, stop and report**, so the mistake would
have surfaced later as a false corruption alarm rather than as the quota refusal
it actually is.

**Candidate for the skill:** `workflow-driver`'s codex adapter should state that
`codex exec`'s exit code is not a completion signal, and that the post-dispatch
check is *the `-o` file exists and parses to the verdict schema*. The existing
verification line covers the read-only intent (`git status --short`) but not
whether the round produced anything. Two different post-conditions, and only one
is currently named.
