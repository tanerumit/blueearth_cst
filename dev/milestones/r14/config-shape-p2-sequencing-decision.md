# R14 — P2's blocking edge is P4, not P1b

**Status: RESOLVED 2026-08-28 — option 1, by execution rather than by memo.**
P3 landed, Gate 3 passed, P4 landed and is green on both CI legs, and P2 has
not started. That IS the reordering this note recommends, so the ruling is
recorded rather than taken: the owner drove `P3 -> Gate 3 -> P4` and the
sequence the dependency graph implied is the sequence that ran.

The blocking condition is discharged. Verified 2026-08-28 at `b3ebcbc3`:
every `test_case/*.yml` now carries `schema_version: 2` and
`test_case/test_rapid` is a real project, so P2's three rung-2 falsifiers can
each be run as stated. **One consequence for whoever runs them: the WF1
snapshot in that tree is still the PRE-migration v1 document**
(`config/runs/snake_config_build_model.yml`, a copy of the old project file),
so WF1 has to be re-run before any falsifier means anything. A guard refusal
against a stale v1 snapshot is not evidence about the guard.

## The finding

The master brief (v3, §Sequencing) says P1b unblocks P2, and gives the reason:

> **P1b before P2**, because P2's three rung-2 falsifiers each say *"build a
> model … run WF3"* and WF3 can run against nothing until the T2 readers move —
> a v1 config hits P1's `schema_version` refusal, a v2 config hits
> `KeyError: 'stress_test'`.

That sentence names **two** refusals and P1b removes only the second one. The
first — `_check_schema_version` refusing every config that carries no
`schema_version` — is untouched by P1b and is cleared by **P4**, which migrates
the shipped configs with P3's rewriter.

So the conclusion drawn from the sentence does not follow from it. P1b was
NECESSARY for P2 and is not SUFFICIENT.

## Why it bites

P2's rung 2 is three falsifiers, and every one of them needs a project that can
actually be built and run:

- *"build a model, edit `climate.selected`, run WF3. It must REFUSE."*
- *"build a model, set `workflows.analyze_projections.enabled: false`, run WF3.
  It must PASS."*
- *"run WF3 to completion, change `compute.batch_size`, re-run. No
  frozen-experiment refusal."*

**No config in the tree can do that.** Verified 2026-08-27 at `b7612e6e`:

```bash
grep -l 'schema_version' test_case/*.yml    # → no matches
```

Every `test_case/*.yml` is v1 and refused at parse time. The only v2 configs are
`tests/data/v2/project_config_v2_probe*.yml`, which point at
`project_dir: tests/test_project` with the fixture catalog and no built model —
enough to prove a DAG builds, which is what P1b used them for, and not enough to
build a model or run WF3 to completion.

P2's own Allowed scope forbids the obvious workaround: `test_case/*.yml` is
P4's, migrated BY the rewriter, and P4's falsifier is *"any difference is a
hand-edit"*.

## Options

1. **Reorder to P3 → Gate 3 → P4 → P2.** *(Recommended.)* The dependency that
   actually exists, made explicit. No edge is violated: the brief states
   `P3 → P4`, `P5 after P4`, `P6 last`, and **no** edge out of P2 at all, so P2
   is free to move later. P2 and P4 touch disjoint paths (P2: the four `*.smk`
   `CONFIG_PROJECTION` tuples and two `experiment/` modules; P4: `test_case/`,
   `config/templates/`). Cost: P2's two small commits wait behind P3 and P4,
   which are the two largest phases. Gate 3 already sits between P3 and P4, so
   the owner keeps a checkpoint either way.

2. **Give P2 a narrow exemption to hand-migrate ONE `test_case/` set.** Cost:
   collides head-on with P4's falsifier. P4 would then be verifying a rewriter
   against a tree one of whose sets was hand-edited, and "any difference is a
   hand-edit" stops being checkable for that set. If this is chosen, the
   exemption must name the set and P4's brief must record that the set is
   excluded from its falsifier.

3. **Split P2: land the code now, defer its rung 2 to after P4.** Cost: P2's
   acceptance criteria say all three falsifiers behave as stated, so this ships
   a phase that cannot be accepted when it lands, and the deferred validation
   needs an owner somewhere. It is option 1 with extra steps and a gap in the
   record, unless the deferred rung is explicitly boarded.

4. **Build a v2 project fixture with real data for P2's use.** Cost: a new
   fixture is a new maintenance surface and a second answer to "what does a
   project look like", which is what `test_case/` already answers. Also has to
   come from somewhere — hand-written, which is option 2 wearing a hat.

## Recommendation

**Option 1.** It is the only one that changes nothing except the order, and the
order it proposes is the one the dependency graph already implies. The other
three all pay in weakened validation somewhere else to buy P2 an earlier slot
it has no reason to need — nothing downstream of P2 is waiting for it.

## What this does not change

- P1c stays where it is: it blocks Gate 5, not P2 or P4.
- P3 can start immediately under any option, and is unaffected by the ruling.
- `K3` is untouched: the bundle still merges as one green whole.

## The general lesson, for the phases still unwritten

This is the **third** unowned or mis-sequenced dependency R14 has produced —
after P1b (the T2 readers no phase claimed) and P1c (the registry three rows
assume). All three share a shape: a brief states a dependency in prose, the
prose contains a compound condition, and only one clause of it gets discharged.

The check that would have caught all three is mechanical and cheap: for each
phase, **take its rung-2 falsifiers and ask what must already exist for the
command to run at all.** P2's falsifiers say "build a model" — the question
"which config?" answers itself immediately, and answers it wrong under the
current order.
