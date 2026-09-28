# R13 — config tiers: what the migration actually did

Implementation record for the split landed 2026-08-21. The normative contract is
`config-tiers-design.md`; the argument behind it is `config-tiers-review-record.md`.
This file records what happened when the design met the tree, and is where a
later reader should look before assuming the design describes the outcome.

## What was migrated

Six configs, split with `scripts/split_project_config.py` and applied by hand:

| Source | Files after |
|---|---|
| `test_case/snake_config_rapid.yml` | + wf0, wf1, wf2, wf3 |
| `test_case/snake_config_baseline.yml` | + wf1, wf2, wf3 |
| `test_case/snake_config_baseline_linux.yml` | + wf1, wf2, wf3 |
| `test_case/snake_config_wf2_fast.yml` | + wf1, wf2, wf3 |
| `config/templates/snake_config.template.yml` | + wf1, wf2, wf3 |
| `tests/snake_config_fixture.yml` | + wf1, wf2, wf3 |

The fixture went first inside the commit. `test_cli.py` cannot run until it is a
valid project file, so migrating it after the seeds would have made every
intermediate failure read as a wiring bug.

Every one of the 16 new seed files is tracked with **no `.gitignore` change** —
`!test_case/snake_config_*.yml` reaches them, as the design predicted.

## Decisions taken during implementation

### No T2 sharing (design §7.4 left this to the implementer)

The design rules sharing IN for the wf0/wf1/wf2 files wherever variants agree,
and OUT permanently for the WF3 file. Measured: **no two variants agree**, so
nothing is shared. The wf1 bodies differ by which outputs each seed asks Wflow
for, and `wf2_fast` carries a comment stating that its discharge-only choice is
deliberate. Reconciling them would have moved `effective_config_digest` for the
baseline seed — in the milestone whose falsifier has to attribute exactly three
moved targets.

The WF3 exclusion stands permanently and is a rule a reviewer enforces, not a
check: nothing at parse time can see two project files pointing at one workflow
file, and `suggest_experiment_name.py` splices `experiment_name` in place.

### The template keeps its own T2 naming

The splitter's mechanical rule would give `snake_config.template_build_model.yml`;
the design specifies `snake_config.<name>.template.yml`. Renamed by hand, along
with the commented `#reporting:` block, which was moved into the WF3 template as
the design requires. The splitter is a user-facing migration tool and was not
taught a repo artifact's naming convention.

## Two things the design did not anticipate

Both were caught by the design's own machinery, which is the point worth
recording.

### The splitter would happily split an already-split config

The body of a migrated stanza is its `config_path`, so a second pass writes
*that key* into a new workflow file and repoints the stanza at it. The round
trip then **passes** — the result composes back to the same document — so
D-15.4b could not catch it. Fixed by recognising the migrated shape up front,
using the same closed-stanza test the loader uses as its migration detector.

Found because the shipped configs are the splitter's own regression corpus, and
after migration there was nothing pre-split left to run it on.

### The D-9.6 scan turned red on a file the inventory predates

`scripts/split_project_config.py` did not exist when the design's cross-workflow
read inventory was swept, and its already-split detector reaches the `workflows`
mapping. Classified explicitly as an ownerless stanza-level read rather than
waved through. The scan forcing a reviewed classification for a new read on an
ownerless surface is exactly the behaviour D-9.6 specifies.

## The pre-split corpus

`tests/data/presplit/` holds the four seeds and the template frozen in their
pre-split shape. They are the only real-world specimens the repository has of
the shape the splitter exists to convert — hand-written comments at three indent
levels, nested blocks, CRLF endings, four genuinely different variants — and
after the tree migrated, nothing else could exercise the tool at all.

They also make the digest-equality property test possible:
`effective_config_digest` and `guarded_sections_digest` computed from each
pre-split file equal those computed from its composed successor, for every entry
point. That is D-10.2 in executable form and it is what lets §16.3's falsifier
be read as evidence rather than hope.

**They are frozen.** A change to a live seed does not belong here, and a failure
against them is a break in the splitter.

## Where the implementation stopped, and why

Commits 1–5 and the docs half of commit 7 are landed. What remains — the
split-phase baseline re-record, the hoist (commit 8), and the hoist-phase
re-record (commit 9) — is blocked on something a task lane cannot supply.

§16.5(b) requires the falsifier pass to run **from the primary checkout**. A
worktree's `test_case/test_local` is seeded from the primary and inherits its
fixture *age*, so a baseline recorded from a lane is a gate that looks
informative and is not. Commit 8 is code-and-tests only and is otherwise ready,
but D-9.7's ordering forbids landing it first: the whole reason the hoist is
inside R13 rather than deferred is that split-only neutrality gets validated
while `CROSS_WORKFLOW_READS` is still populated. Landing the hoist before the
split-phase falsifier collapses two digest shifts into one unattributable event
— exactly the collision the ordering dissolves.

### What the branch is verified to, in this lane

| Gate | Result |
|---|---|
| `pixi run test-full -rs` | **3043 passed, 9 skipped, 1 xfailed** (420 s), one process |
| `pixi run test-fast` | 2973 passed |
| `pixi run test-contract` | 70 passed |
| `pixi run tree-check` | MAP CLEAN, 224 paths, 0 unmapped |
| `pixi run lint` / `format-check` | clean |

**The skip count was read, not predicted** (§16.5 clause 5). Six of the nine
skips are the fixture-dependent layer itself: five `temp() artifact absent;
capture via --notemp` cases in `test_interchange_contracts.py` plus its
`weathergen_config.yml predates the weathergenr 2.0.0 upgrade` case. So this
green is **not evidence about the composed snapshot** — the only tests that read
a real snapshot are among the ones that skipped. That is the situation §16.5(b)
is written against, stated here rather than left for a reader to infer from a
count.

### One correction to commit a457157's message

That commit says the `tree-check` pin "still points at a config whose values
equal the tool's own fallbacks, so the gate cannot yet fail". §16.5(a) does not
ask for the pin to move. Its two changes are (i) `snapshot_project_tree.py`
composes and (ii) `tests/test_snapshot_project_tree.py` carries a case whose
`experiment_name` is not `experiment`. Both landed in that same commit — its
fixture uses `my_experiment` — so §16.5(a) is discharged and `pixi.toml:185` is
correct as it stands. The gate is green *because the tool composes*, which is
what the design asks for.

## Deviations from the design's commit table

- **Commit 6 does not exist.** D-13.4 removed the advanced-settings namespacing
  it carried; no advanced-settings key moves in R13.
- **`tests/test_snapshot_project_tree.py` moved from commit 4 to commit 5**, with
  the tool it tests. The design's own rule is that a move must not leave the tree
  un-runnable between commits, and splitting a tool from its test does exactly
  that.
- **The digest-equality property test landed in commit 3**, not commit 1: it
  needs composed seeds to compare against, which do not exist until the
  migration. The design's §16.1 names the test but §15.7 assigns it no commit.
