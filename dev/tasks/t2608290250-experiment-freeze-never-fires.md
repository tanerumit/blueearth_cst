---
title: The experiment freeze never fires through rule 3.07
type: todo-item
status: backlog
effort: 2
area: experiment provenance
origin: R14
queue: 1
created: 2026-08-29
updated: 2026-08-29
---

> [!note] Overview
> **What** — `check_not_frozen` returns early on every real run, so an
> already-run experiment's configuration is NOT settled and never has been.
> Snakemake removes rule 3.07's declared output before the job executes, so the
> recorded `experiment.yml` the check reads is gone by the time it looks.
> **Why** — The mechanism exists to stop a config edit silently redefining what
> existing results mean. It is fully implemented, fully tested, and inert.
> **Effort** — The comparator is correct and needs no change; what needs
> deciding is how the record survives its own rule.

## The evidence

Found 2026-08-29 while running R14 P2's third rung-2 falsifier, which needed a
frozen experiment to be meaningful. The falsifier passed, and so did its
control, which is what exposed this: **a change to `n_realizations` was accepted
after a complete WF3 run.**

Directly, on the same files, the freeze works:

```text
marker ok: True
diffs: ['n_realizations']
FROZEN, names: ['n_realizations']
```

Through the rule, it does not. A temporary probe in the `__main__` harness,
added and reverted in the same session:

```text
02:49:06 - probe - PROBE prev_exists=False marker=True
```

`prev_exists` is `Path(sm.output.experiment_config).is_file()` evaluated as the
first statement of the script. The file exists on disk before the invocation and
is absent when the script starts, so Snakemake removed it as a declared output
of the job it was about to run. `check_not_frozen` then takes its first branch:

```python
if not out_path.is_file() or not has_run_successfully(run_marker):
    return
```

The removal is not in the Snakemake log because `profiles/default/config.yaml`
sets `quiet: reason`.

## Why no test caught it

Every test calls `write_experiment_config` or `check_not_frozen` directly, with
a recorded file the test itself wrote and did not delete. That is a faithful
test of the comparator and says nothing about the rule, because the deletion
happens in Snakemake, one layer above anything the unit tests reach. The tests
are not wrong; they are testing the half that works.

The same shape as R14 P2's other fixture defect, and worth stating as one
lesson: **a mechanism whose input is produced by the harness cannot be verified
by a test that stages that input itself.**

## What it does NOT change

`C-79` is unaffected. It removes `compute:` from what the freeze compares, which
stays correct whenever the freeze is repaired, and its behaviour is pinned by
tests at the comparator level. This note is why P2's third falsifier is recorded
as *vacuous at rule level*: nothing freezes there, so "batch_size did not
freeze" is not evidence about `compute:` specifically.

## Options, none chosen

1. **Read the record from a path that is not this rule's output.** A sidecar the
   rule writes beside `experiment.yml` and reads back next time. Cheapest, and
   it splits one fact across two files.
2. **Stop declaring `experiment.yml` as an output.** It becomes a rule-managed
   artifact Snakemake does not track, which loses the DAG edge that makes
   downstream rules wait for it.
3. **Move the check off the rule.** Freeze at WF3 parse time, beside the other
   refusals, reading the record before any job runs. Fits where R14 put the rest
   of the loud-refusal logic; changes when the user sees the error.

Option 3 looks closest to the intent, but the choice needs the person who owns
the experiment-structure design (`dev/milestones/p31/`), not the person who
tripped over it.

## The brief

`dev/working/2026-08-29_experiment-freeze/freeze-repair.task.md`. Gate 1 rules
the record's home; the falsifier is two WF3 runs, and it has to go through
Snakemake — a unit test cannot see this defect, which is how it survived.

## Links