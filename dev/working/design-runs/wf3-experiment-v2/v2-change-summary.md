# WF3 v2 — what changed and why, in plain language

Companion to `design-v2.md` (the normative document) and `ledger.md` (the formal
disposition of all 52 review findings). This file is neither: it is a readable
walkthrough of the same changes for someone who has not read the reviews.

**Context.** An internal review panel read `design-v1.md` under three lenses —
risk and assumptions, architecture and internal consistency, repository fit —
and filed 52 findings (8 blocking, 22 major, 22 minor). All 52 were accepted;
one *part* of one major finding was declined, and that is item 33 below. No
architectural decision changed. Every fix repairs a **claim the architecture
rested on**, not the architecture itself.

Numbering matches the item list in the session summary. Findings are cited in
parentheses so each item can be traced back to `ledger.md`.

---

## Vocabulary

Several items below depend on these, so they are worth fixing first.

- A **member** is one cell of the stress test: one realization of generated
  weather at one temperature/precipitation perturbation. A basin assessment is a
  **sweep** over all of them.
- The **manifest** is the run's up-front plan — which members exist, and what
  each one was built from. The **ledger** is the append-only record of what
  actually happened to each member. Together they let a killed run resume
  without redoing finished work. This is the core of the redesign: member-level
  incrementality moves out of Snakemake and into our own code.
- A **gate** is an executable test with a named injection and an expected
  observation. A **falsifier** is the observation that would prove a stated
  claim wrong. The discipline the design commits to is that every claim has one,
  and that the test is written before the code.
- The **fingerprint** (`member_hash` in the document) is a digest of everything
  that affects a member's result. The sweep skips any member whose fingerprint
  is unchanged and whose outputs are still intact. Items 2 and 5 are about what
  that fingerprint did and did not cover.

---

# Part 1 — The changes that would have produced wrong or unrunnable work

## 1. The fixture arithmetic was wrong, and it broke the tests that matter

*(arch-1 blocking, risk-9 major)*

v1 sized every example, job count and test expectation for a 14-member test
case. The test configuration actually tracked in the repository produces **12**
members — it does not include the unperturbed baseline slice — and because it
averages across realizations, its main output table has **6** rows regardless of
how many members exist.

The consequence was not cosmetic. The two gates that verify the most delicate
new behaviour (what happens when a member fails, with and without the
partial-results mode) stated pass conditions that could never occur on the named
fixture. At implementation time someone would either have "corrected" them ad
hoc — exactly the drift that writing tests before code exists to prevent — or
read the mismatch as a real failure and chased it.

v2 recomputes every fixture-scale number, and states the arithmetic **once** at
the top of the document with its sources, so it cannot drift apart again. The
owner ruled that the fixture itself is not changed to match the document.

## 2. The sweep could silently publish results computed from the wrong weather

*(risk-1 blocking, arch-3 blocking, arch-2 blocking, arch-7 major,
repo-fit-10 minor)*

This is the most serious finding in the set, and the four findings above are one
defect seen from four angles.

The fingerprint covered the member's *hydrology* inputs and its *outputs* — and
**no generation-side input at all**. Not the random seed. Not the generator's
settings template. Not the weather series the member actually reads.

Trace what that means. Change the master seed and re-run:

1. the plan is rewritten with new per-realization seeds — but every fingerprint
   is byte-identical, because the seed was never in it;
2. the weather series regenerate, because *their* configuration changed;
3. the sweep re-enters, because one of its declared inputs changed;
4. the sweep checks each member, finds the fingerprint unchanged and the outputs
   present and intact, and **skips all 12**;
5. the reduction publishes a response surface computed from the **previous**
   weather, while the plan on disk records the new seeds.

Nothing fails. Nothing warns. The status command reports all-done. The run's own
provenance record asserts a pairing that never existed. Re-seeding a stress test
is routine practice, so this was a reachable operation rather than a corner case.

A related problem sat next to it: the fingerprint keyed on a digest of a file
produced by a rule that runs *after* the plan is written, so on a fresh
experiment no fingerprint was computable at all, and on a re-run it would have
digested the previous generation's file — hashing a stress-grid edit one
generation late, which is worse than failing outright.

**v2 fixes this in two layers, because either alone is insufficient.**

- *Planning time.* The seed, the generator template's digest, and a digest of
  the stress-test configuration section all go **into** the fingerprint. Every
  term is now computable when the plan is written. A configuration change
  therefore invalidates the right members immediately.
- *Sweep time.* Every finished member additionally **records the digests of the
  files it was actually computed from**, and the sweep re-checks those before
  reusing it. This catches what no fingerprint can: bytes that changed on disk
  with no configuration change at all — a regeneration for any reason, a torn
  write, a hand edit, a different generator build.

A new gate changes the master seed and requires all 12 members to re-run; a
skipped member fails it. The invalidation table in the document was rewritten so
that each row names the layer that actually catches that case, rather than
asserting an outcome the mechanism could not deliver.

## 3. "Partial results" did not produce partial results

*(arch-15 blocking, risk-2 blocking, repo-fit-6 major, risk-5 major)*

The owner approved a mode where a sweep with a failed member still publishes
what it has, with the gaps recorded. v1 described the outcome as "a grid with
holes; the missing rows simply absent."

Read against the reduction code, a hole cannot take that shape. The output
frames are **pre-allocated** at full grid size and the loop runs over every grid
cell regardless of what is on disk. So:

- a cell missing *some* of its realizations comes out **fully populated but
  quietly averaged over fewer years** — indistinguishable from a complete cell;
- a cell missing *all* of them either **crashes** on an empty concatenation, or,
  without that, emits a **row of zeros** for a stress-test case that never ran.

All three are the exact distortion the fail-loud default exists to prevent,
reintroduced through the escape hatch that the same ruling approved.

**v2 makes completeness a property of the response-surface cell, not of the
member.** An incomplete cell is **dropped entirely** — the row is absent, not
under-averaged and not zero-filled. The output frames are sized from what
actually succeeded. An empty group raises a named error rather than a bare
pandas one. A separate record names each dropped cell, why it was dropped, and
how many realizations it was missing, and retained cells carry their count so a
consumer can check.

Dropping is the only shape a downstream consumer can detect without extra work,
which is the whole point. Two consequences are now stated rather than glossed:
the reduction is no longer "unchanged code" (it is specified work with an
owner), and its byte-identity claim holds **under full completeness** only, with
the partial path getting its own separate test.

## 4. Two concurrent runs could corrupt each other, and one crash left no way out

*(risk-6 major, repo-fit-1 blocking, repo-fit-14 minor)*

The design's lock exists for a real reason: this repository's standing policy is
one worktree per task with several sessions running at once, and Snakemake's own
lock is scoped to the *checkout*, not the project folder. Two worktrees pointed
at one project slip past it entirely.

But v1 took the lock inside the sweep — **stage three of four**. A second run
could rewrite the plan, regenerate the weather files the first run was in the
middle of reading, and rewrite the final indicator tables, all before the lock
ever came into play. The realistic case is the damaging one: a second worktree
exists *because* someone is trying an edited configuration. The result would be
torn reads recorded against the wrong member, or a member perturbed from a
half-written file that still opens. Persisting the weather files — an approved
change in this redesign — is what made this reachable; previously they were
short-lived temporaries.

Separately, a hard kill **always** leaves the lock behind, because the cleanup
code never runs. v1 then refused to clear a stale lock, and told the user "the
message names the recovery command" without the document ever naming one. So
the recovery gate for the design's headline claim — that resume is measured, not
asserted — was unexecutable, and a user killed once had no documented exit.

**v2 takes one lock for the whole workflow**, using Snakemake's
start/success/error handlers. These run in the main Snakemake process, which is
the one process alive for the entire run, so its process id is a meaningful
liveness token — unlike a lock handed between rule processes, which has no live
holder in between.

No workflow in this repository uses those handlers, so I probe-verified the
three properties this rests on rather than assuming them:

- they do not fire on a dry run, so inspecting a workflow never claims a lock;
- a refusal in the start handler aborts **before any job runs**;
- neither the success nor the error handler runs when the start handler itself
  raised — so a run that *failed* to take the lock can never release someone
  else's.

Staleness is judged on process id **plus** process creation time, because id
reuse is routine on Windows. A provably-gone holder is cleared automatically
with a log line; anything else is refused, naming a concrete recovery command
that now exists. The document carries a single three-line recovery block for the
whole crash path.

---

# Part 2 — The changes that would have failed on first contact with the repo

## 5. Three documented commands did not work

*(repo-fit-2 major, repo-fit-3 major, arch-6 major, repo-fit-8 major)*

- The sweep rule asked Snakemake for the machine's core count in a form that
  **throws when no core count is given**. That is exactly how the documented
  crash-recovery command is written, so recovery would have broken on the one
  workflow that needs it, as would any plain dry run. The repository already
  carries a guard for this hazard; v2 reuses it, and the sweep degrades to a
  single worker rather than failing.
- The sweep declared a model file as an input that **nothing in this workflow
  produces**. Marking it as "ancient" suppresses the freshness check, not the
  existence check, so this turns the continuous-integration tests red on a fresh
  checkout. The freshness signal came from elsewhere anyway; the edge is dropped.
- Three operator commands passed settings in a form the reading code path never
  looks at, so they would have silently run with defaults and reported a false
  pass — including the gate for the partial-results mode, which would have been
  testing the *opposite* behaviour. v2 specifies an explicit precedence for
  command-line overrides and threads the resolved values through.
- The orchestrator was specified as a Snakemake `script:` module while also
  spawning worker subprocesses. Snakemake runs script modules as a subprocess
  with a rewritten entry point, and the spawn mechanism re-executes that module
  in every child — so its imports would be paid once per worker, contradicting
  the design's own cost argument. v2 runs it the way the repository already runs
  its long-lived Julia child, which sidesteps the problem entirely.

## 6. Per-member logs would have vanished

*(arch-4 blocking, repo-fit-4 major, arch-11 minor)*

The log merger checks for a single flat file for a rule and **returns
immediately** if it finds one. v1 wrote both a flat log and a directory of
per-member logs under the same rule name — a combination no rule in any of the
three workflows currently has — so every per-member log would have been silently
dropped from the merged output. Worse, because dropped files are never marked as
merged, they are never cleaned up: the parts directory would grow without bound
and the documented "one log file after a clean run" property would break.

The point of pain is that per-member visibility is one of the redesign's four
stated goals. This would have defeated that goal while appearing to satisfy it.

Fix: give the rule **one shape**, by putting the orchestrator's own log *inside*
the per-member directory, where the sort order places it first and it reads as a
section header. Separately, the per-member *timing* files were dropped
altogether — the benchmark merger's totals row would have counted the sweep
twice, once as the job and once as the members that constitute it, and the
ledger already records finer timings anyway.

## 7. The test for the shakiest assumption could not fail

*(risk-3 major, risk-4 major)*

The assumption underneath the whole redesign is that running many models in one
warm process gives **identical numbers** to running each in a fresh process. If
that fails, every number the milestone produces is wrong.

v1 tested it with a whole-tree comparison against a snapshot taken before the
migration. But the migration **deliberately changes the generated weather** — new
per-realization seeds are the point of one of its steps — so that comparison is
guaranteed to show a large difference for reasons that have nothing to do with
the question. At the gate, the difference would have been attributed to the
known change and the assumption declared verified on a test structurally
incapable of discriminating.

v2 replaces it with a **controlled pair**: the same inputs, run once with one
member per process and once with all twelve in a single process, requiring exact
agreement. Nothing else varies, so a difference means session depth changed a
result. The tree comparison is kept separately, scoped to the stages that did
not change, and reported rather than gating.

The second half of the finding is stated rather than fixed, because it cannot be
fixed on the fixture: at the default settings the test case gives each process
about four members, which is the *same* depth the previous approach already
measured. Production gives hundreds. So the assumption is now marked open at
production depth, with a worker-recycling limit shipped as the pre-designed
mitigation and a named trigger for re-verification on the first real sweep.

## 8. A partial run froze permanently

*(risk-5 major)*

Once a partial sweep finished, its output file existed and nothing else had
changed — so re-running reported "nothing to be done" and **never retried the
failure**, even after the user fixed the cause. The holes were frozen until
someone manually deleted the output, a step named nowhere.

This matters because the partial mode exists precisely for runs that are
expected to be re-attempted. The likely user story was: take a first look, fix
the fault, re-run, get the same incomplete surface plus a workflow claiming it
is up to date, while the completeness record still names the hole.

v2 writes a small marker recording the incomplete set with a **fresh run id each
time**, which makes the next invocation re-enter and retry — including after a
repeated failure, which a marker keyed on the failure set alone would not. A
complete run deletes the marker, so the loop terminates. Two harmless
second-order effects are stated so an implementer does not read them as bugs.

## 9. The performance check compared the wrong things, at the wrong time

*(risk-10 major)*

Two independent problems. It **gated on total workflow time** against a measured
number that includes stages this redesign restructures — so the new approach
could win decisively on the stage it replaced and still "fail" on a total it did
not, or the reverse. And the check sat **three steps after** the old approach had
been deleted, meaning a genuine failure would require reverting five landed
steps including contract, validator and documentation rewrites. Realistically,
the floor would have been accepted rather than enforced.

v2 gates on the **stage-level** measurement, which is the like-for-like
comparison, reports the total separately as context, and moves the binding
measurement to the point where both approaches still exist in one tree — so the
comparison is same-tree and the revert is one step.

## 10. A settled decision still read as an open recommendation

*(risk-18 minor, repo-fit-13 minor)*

The precipitation-variance axis is inert: the installed generator scales
variance with the mean and ignores the value we pass. This was measured, not
assumed. The owner **deferred** doing anything about it, because activating it
would change every perturbed result and force a full re-baseline.

But the design body still recommended activating it. An implementer reading the
accepted document would reasonably take that as authority. v2 rewrites the
section to state the ruling first and plainly, removes the recommendation, and
clears the six other places where the old framing survived.

It also fixes what "deferred" would otherwise have become. Shipping an axis that
silently does nothing is the worse failure the section itself names, so the
inertness is now documented where it is *consumed*: in the output schema, in the
seam contract, and as a warning at plan-build time when someone configures a
variance range that cannot do anything. And the one change the owner did allow
is taken — turning on the generator's own warning — so the inertness appears in
the run's own logs rather than only in documentation.

## 11 and 12. Gaps in test coverage and in ownership

*(risk-16, risk-12, risk-13, risk-7, arch-9, repo-fit-5, repo-fit-7,
repo-fit-13)*

Three of the twelve enumerated failure modes had **no test at all**, including
the one this repository is most likely to hit in practice — Julia missing from
the path, which the repository's own instructions flag as a standing hazard. So
did the highest-consequence realistic failure, the silent-skip path of item 2.
v2 adds those tests and, more usefully, adds a **coverage table** mapping each
failure mode to its test with an explicit "no test, and here is why" cell, so a
future gap is visible at a glance instead of requiring a cross-read.

On ownership: several pieces of real work had no owner and no migration step.
The most consequential is a module the design assumed could be called directly
from the worker — it cannot, because it reads workflow variables at import time
with no function to call. That extraction is now its **own migration step** with
its own test, rather than sitting unnamed inside the milestone's largest step.
Five named test files that the migration invalidates are each assigned to the
step that breaks them.

---

# Part 3 — The remaining twenty

Each is one or two sentences of specification closing one finding. Grouped by
what they protect.

| # | Change | In plain terms | Finding |
|---|---|---|---|
| 13 | Write ordering and identity fields on the completeness record | The record that tells a scientist which cells are trustworthy carried nothing tying it to the run that produced the results beside it. It now carries the run id, and the write order is fixed so a kill leaves the reduction blocked rather than reading a mismatched pair | risk-8 |
| 14 | Impossible event sequences are treated as corruption | The design declared a state machine but never checked that recorded histories obeyed it, so an impossible history folded to a perfectly valid state — the cheapest available detector for the bug class rated highest-risk | arch-13 |
| 15 | File order, not timestamps, decides resume | Timestamps are recorded to the second while several member steps take milliseconds, so "the last row" read as "latest timestamp" could re-run a member that had already succeeded | risk-17 |
| 16 | The reduction verifies file digests before reading | The design paid to compute and store digests and then never spent them at the one point where corruption becomes user-visible. A member file edited after a successful sweep would have been published silently | risk-12 |
| 17 | Whole-file writes retry on a blocked replace | On Windows, replacing a file another process has open fails outright — and the design deliberately creates such a reader in the status command. This has no equivalent on Linux, so it would only ever have failed on the development machine | repo-fit-14 |
| 18 | Text encoding pinned on the worker pipes | Julia writes UTF-8; Python pipes default to the local codec. An error message containing an unusual character would fail to decode — meaning the decode breaks on exactly the message the failure path exists to carry | repo-fit-17 |
| 19 | The large grid file is digested in chunks | The existing helper reads a whole file into memory at workflow-parse time, on every invocation. Fine for the small configuration files it was written for; not fine for a real basin's grid, and invisible on the 152 KB test fixture | repo-fit-15 |
| 20 | The retention flag covers both deletion points | It was specified to suppress one of the two points where intermediates are deleted, which would have left one seam validator permanently unable to run — the exact failure the flag exists to prevent | arch-5 |
| 21 | Return-interval outputs and the user-facing target list dispositioned | A whole class of existing output products had no stated disposition in a milestone that rewrites the reduction and re-records the baseline | arch-10 |
| 22 | One record, one row population | Three sections described the same record with three different sets of rows, and a trailing summary line made a file that a naive reader cannot parse. The summary moved to a sidecar | arch-12 |
| 23 | Configuration fingerprint enumerated; key counts corrected | The fingerprint's coverage was never stated, though the whole invalidation table depends on exactly which keys it covers; and one key described as "new" is an existing contract key, which would have sent a validator extension after the wrong set | arch-14 |
| 24 | Recorded paths are rejoined before opening | Paths are recorded relative to the experiment folder while the code opens them from the repository root — a guaranteed failure on the first read of the milestone's central new data path | arch-16 |
| 25 | Compare numbers, not their string formatting | The wide output tables are string tables holding formatted numbers, so a byte-for-byte check on the new long-format view would fire as a false regression over trailing zeros | repo-fit-12 |
| 26 | The status command moves to the user-facing folder | The repository splits its three script folders by who invokes them. The one tool that compensates for lost visibility was filed where users are told *not* to look | repo-fit-9 |
| 27 | Rejecting retired configuration keys gets a mechanism | "Rejected with a named message" had no implementation anywhere in the repository and no precedent, so it would have landed as a silent ignore — the exact failure the rule was written to prevent | repo-fit-11 |
| 28 | Why one class of read can no longer be declared | The repository deliberately tightened a convention in the opposite direction once. The reason it cannot be honoured here is sound but was unstated, so it read as an oversight | repo-fit-16 |
| 29 | Two generator products keep their ruled location | A move into a scratch folder would have reversed a recorded prior ruling and hidden the record of which historical days each realization resampled. They stay in the output folder with per-realization names, which also removes the write race the move was solving | risk-11 |
| 30 | Version drift is reported, not merely reconstructible | The claim was that drift is "detectable after the fact", with no code performing the comparison — a test that can never fail, protecting a risk that would have stayed unmitigated | risk-13 |
| 31 | Leftover intermediates are swept after an interrupted run | The disk-usage guarantee holds *within* a completed member. A crash mid-member leaves the largest files in the tree with no owner, and the test sampled only clean runs, so it could not see the accumulation | risk-19 |
| 32 | A statistical claim restated to what two samples support | The test case generates two realizations. An "envelope" over two draws of a stochastic generator either passes trivially or fails spuriously, and either way it would have been recorded as a verdict on a value-changing re-baseline | risk-14 |

---

# Part 4 — Five corrections found after drafting

An advisor pass over the draft caught cases where a fix had opened a new gap.
Each is small; each would have been re-filed by a fresh reviewer.

33. **The no-op test's trigger no longer triggered anything.** The test re-runs
    after "an unrelated comment change" — but once the configuration fingerprint
    was enumerated over *parsed* values (item 23), a comment alters nothing, the
    plan is not rewritten, and the workflow reports "nothing to be done". The
    rule never re-enters, so the test could observe nothing. The injection now
    changes a worker-count setting instead, which re-enters the rule *and*
    validates that execution settings correctly do not invalidate members.
34. **The disk-usage goal was qualified in one place but not where it is
    defined.** Item 31 restated it in the detailed section; the goals list at the
    top still carried the unqualified version, which is the one a fresh reader
    meets first.
35. **The core-count guard lives inside the block a later step deletes.** Item 5
    reuses an existing guard — but it sits inside the batch-rule block that a
    later migration step removes wholesale, so deleting that block would take the
    guard with it and reintroduce the very failure item 5 closed. The step now
    says explicitly that the guard is retained and relocated.
36. **The proposed comment line in the new output file would break the tool that
    compares it.** The baseline comparator reads CSV files with no comment
    handling, so a leading annotation line would be parsed as the header row —
    and this file joins the baseline manifest. The annotation moves to the
    documentation surfaces that were already in scope.
37. **The quarantine step would have moved the lock the running workflow holds.**
    Recovery moves the whole state folder aside; the lock now lives in that
    folder, and its release handler would look for it at a path that had moved.
    The lock is excluded.

---

# Part 5 — The one thing declined

38. **A per-member time limit was asked for and is not adopted.** *(risk-7,
    major — flagged for ratification at the next gate.)*

    The finding identified a genuine hang: if the worker's error stream is left
    as an undrained pipe, the process blocks once that buffer fills — mid-run,
    with no timeout, no heartbeat, and no exit path, because the worker has not
    actually exited. The reviewer proposed two fixes: drain the stream, and add
    a generous time limit derived from observed run times.

    **The first is adopted and tested.** The error stream is redirected to the
    member's log file at spawn, never left as a pipe, and a test floods it to
    prove the sweep does not stall. That removes the only known mechanism by
    which a *healthy* worker can block forever.

    **The time limit is declined**, for two reasons. It adds a kill path to the
    newest and least-proven component in the milestone, where a wrongly-sized
    limit destroys good work — and hydrological runs legitimately take minutes.
    And a limit derived from observed run times cannot protect the early
    members, because it needs run times to exist before it can be computed, so
    it does not cover the window where a systematic problem would first appear.

    What remains uncovered is a genuinely wedged model run. It is visible in the
    orchestrator log as a member with no finish line, and recoverable by kill
    plus resume, which is a supported path. This is recorded as accepted
    residual risk with the reasoning written into it, and surfaced for the next
    gate rather than buried.
