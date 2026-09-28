# Candidate second scenario family — a paper schema, and what it does to E18

> **R-6 deliverable**, run `wf3-simulation-identity`, milestone R12. Written to
> settle **E18** before G2, per the owner's gate-return ruling. `domain-10`
> proposed this instrument from the method side; `risk-3` reached the timing
> question from the other.
>
> **This ships nothing.** No producer, no downscaling path, no config surface, no
> rule, no code. The intake's non-goal ("Building a second scenario family")
> stands and is not touched. This is a desk exercise whose only job is to
> falsify or confirm E18 cheaply, and to be checked against `design-v2.md` §5.1.2.
>
> **Verdict up front: E18 is CONFIRMED**, on the join-semantics ground of §3
> below rather than on the raggedness ground the intake argues. The design's core
> accommodates the family with **one added core column** and **one added rule**,
> both of which `design-v2.md` now names as owed rather than shipping unused.

## 1. The candidate

Two variants, because they fail `(rlz, st)` differently and a schema that only
answers the ragged one proves less than it looks.

**Variant A — `downscaled`.** Scenarios downscaled from CMIP6 series: one run per
`(gcm, ssp, horizon)`. Deliberately chosen to be **numerically factorial** —
6 GCMs × 3 SSPs × 2 horizons = 36 rows — because the weak form of E18 ("a ragged
list has no factorial") is trivially true and proves nothing about a set that
*does* factor.

**Variant B — `supplied`.** A user hands WF3 a folder of *k* daily series with
names of their own choosing: an observed drought sequence, two paleo
reconstructions, a stakeholder-authored "worst plausible" trace. Ragged by
construction; *k* is whatever the user brought.

## 2. The rows and columns such a family would have

### Variant A — `downscaled`

Universal core (`design-v2.md` §5.1.2), three columns:

| `run_id` | `derived_from` | `evaluated` |
|---|---|---|
| `01` | *(empty)* | `true` |
| `02` | *(empty)* | `true` |
| … | *(empty)* | `true` |
| `36` | *(empty)* | `true` |

Family block, registered as `FAMILY_COLUMNS["downscaled"]`:

| `scenario_family` | `gcm` | `ssp` | `horizon` | `delta_t` | `delta_p` |
|---|---|---|---|---|---|
| `downscaled` | `EC-Earth3` | `ssp245` | `2050` | `1.42` | `0.96` |
| `downscaled` | `EC-Earth3` | `ssp585` | `2050` | `1.91` | `0.93` |
| `downscaled` | `MPI-ESM1-2-HR` | `ssp245` | `2085` | `2.30` | `1.04` |
| … | … | … | … | … | … |

`delta_t` / `delta_p` are the response-surface coordinates, **supplied by
whatever produced the scenarios**, per `design-v2.md` §5.4.5. WF3 does not
compute them, which is the whole point of that ruling.

Plus the forcing location, discussed in §5:

| `forcing_uri` |
|---|
| `/data/downscaled/EC-Earth3_ssp245_2050.nc` |

### Variant B — `supplied`

Core:

| `run_id` | `derived_from` | `evaluated` |
|---|---|---|
| `1` | *(empty)* | `true` |
| `2` | *(empty)* | `true` |
| `3` | *(empty)* | `true` |
| `4` | *(empty)* | `true` |

Family block, `FAMILY_COLUMNS["supplied"]`:

| `scenario_family` | `label` | `provenance` |
|---|---|---|
| `supplied` | `obs_1983_drought` | `observed` |
| `supplied` | `paleo_recon_a` | `tree-ring` |
| `supplied` | `paleo_recon_b` | `tree-ring` |
| `supplied` | `stakeholder_worst` | `expert-elicited` |

No `delta_t` / `delta_p`: this family declares **no surface-axis columns**, which
is the case §5.4.5's family gate exists for.

## 3. Is E18 confirmed or refuted? — **CONFIRMED**

E18: *"a user-supplied or GCM-downscaled scenario set is not expressible as
`(rlz, st)`."*

**Variant B refutes nothing and confirms little.** Four ragged rows have no
factorial, so no `(rlz, st)` assignment exists that is not invented. True, and
weak — a critic answers "so pad it", and the padding argument is only about
convenience.

**Variant A is the real test, and it is where E18 holds.** Variant A *is*
6 × 3 × 2, so a reviewer can say: assign `rlz ∈ 1..6` (the GCM), `st_id ∈ 1..6`
(the SSP × horizon pair), and the composite identity expresses it. **That
assignment fails on semantics, not on arithmetic**, and it fails twice:

1. **`st_id` is a foreign key, not a free integer.** WG-2 pins
   `stress_test_lookup.csv` as the design-point table: every `st_id` names a row
   of *monthly perturbation multipliers* — twelve temperature deltas and twelve
   precipitation factors — and `validate_hm7` refuses an emitted `st_id` the
   lookup does not define (`interchange_contracts.py:1030-1038`, the
   "which the lookup does not define" diagnostic). A `(ssp245, 2050)` pair has no
   such row. Manufacturing one means computing monthly change factors from the
   GCM series inside WF3 — which is WF2's change-factor computation, and
   `AGENTS.md` § Background forbids WF3 from acquiring it (S5/S6). So the
   assignment either writes an `st_id` that resolves to nothing (a broken join
   the existing validator catches) or imports the forbidden computation.
2. **`rlz` is a common-random-numbers index, not a label.** Under R-3 the
   stochastic family's `derived_from` carries a paired-sampling property: design
   point *m* at realization *r* is perturbed from **realization *r*'s own**
   baseline draw (`run_stress_test.smk:1020`). Two rows sharing an `rlz` are two
   perturbations of one draw. Two rows sharing a GCM are two different
   downscalings, sharing a climate model rather than a random seed. Spelling a
   GCM as `rlz` asserts a pairing that does not exist, and the surface's
   interpretation depends on it.

**Verdict.** A GCM-downscaled set that *is* numerically factorial still cannot be
expressed as `(rlz, st)` without either a dangling foreign key or a false claim
about pairing. E18 is confirmed, and confirmed on a stronger ground than the
intake states it. **The intake's own argument for E18 (raggedness) is the weaker
half; the design should rest on the join-and-pairing argument instead.** That
change is made in `design-v2.md` §5.2.2 and §7.

**E19 is settled by the same exercise, in the affirmative.** Variant A's
`delta_t` / `delta_p` are family-block columns its producer computes; Variant B
declares none and is surface-gated out. `design-v2.md` §5.4.5's ruling
(coordinates are stage-1 columns, WF3 never derives them) is what makes Variant A
plottable at all, and Variant B demonstrates the gate is not decorative.

## 4. Checking it against `design-v2.md`'s scenario-table schema

### Does the core column set accommodate it without change?

**Two of three columns, yes; the third is the finding.**

| core column | Variant A | Variant B | verdict |
|---|---|---|---|
| `run_id` | minted `01`..`36` | minted `1`..`4` | **holds unchanged.** The id is a name; nothing about it is family-specific |
| `derived_from` | empty on every row | empty on every row | **holds, and evaluates to the empty set** — exactly what §5.2.2 predicts for a family that supplies all its forcing. This is the mechanism's own test and it passes |
| `evaluated` | all `true` | all `true` | **holds unchanged.** Neither family has forcing-ancestor rows, so the column is uniformly true — degenerate, not broken |

`derived_from` evaluating to empty is the load-bearing check. §5.2.2 argues the
column is family-blind because *"which rows have a forcing ancestor"* means the
same thing for every family and evaluates to the empty set for a family that
supplies its own. **Both variants confirm that**, and they expose the consequence
the design must state: with `DERIVED_FROM` empty, rule 3.12's alternation
constraint is the empty alternation, so the family is only runnable if that case
is handled — which is `design-v2.md`'s GF-2, and P2b now measures it rather than
assuming it.

### Which columns land in the family block, and does `FAMILY_COLUMNS` hold them?

Every non-core column lands in the block: `{gcm, ssp, horizon, delta_t, delta_p}`
for A, `{label, provenance}` for B, each preceded by `scenario_family`. The
registry is a `dict[str, tuple[str, ...]]`, so it holds them **mechanically**
without change.

**One defect the exercise exposes, and it is not mechanical.** A block is a *set
of columns of one CSV*. Two families in one table would need a union with blanks
— `gcm` empty on every stochastic row, `st_id` empty on every downscaled row —
which is the denormalisation defect C28 was written to contain, arriving through
the back door. **`design-v2.md` §5.1.2 now states normatively that one scenario
table carries exactly one family** (`scenario_family` has one distinct value),
and that admitting a second family concurrently is the file split the design
already says it makes cheap. Without that sentence the registry "holds" the
columns in a shape nobody would want.

### Does `derived_from` behave sensibly for a family with no baseline-derivation relation?

**The edge behaviour is right; the marking is what R-3 adds, and the exercise
shows the marking needs one more clause than R-3 states.**

- **As a DAG edge:** empty is correct and complete. No 3.12 job, no ancestor, no
  cycle. Nothing is asserted that is false.
- **As the R-3 pairing carrier:** the family registry declares
  `pairing: independent` for both variants (`paired_across_design_points` for
  `stochastic`), and stage 3 records it beside the surface, so a Variant-A
  surface is **marked unpaired** rather than silently read like a stochastic one.
  The mechanism does what R-3 asks.
- **The missing clause.** Nothing in R-3 as ruled prevents a family from
  declaring `pairing: paired_across_design_points` while its `derived_from`
  column is uniformly empty — a declaration with no evidence behind it. A
  declared pairing is only true if the edges exist. `design-v2.md` §5.1.2 now
  carries the consistency refusal: **a family declaring a paired relation whose
  `derived_from` column is empty on every row is refused at parse time.** That
  clause exists because of this exercise; nothing in the 31 findings names it.

### Does the 1→2 seam stay two-plus and family-blind, or does this family force a fifth core column?

**The seam stays family-blind. It does not stay three columns: Variant A and
Variant B both force a fourth, and it is `forcing_uri`.**

This is the exercise's second concrete result, and it settles a live finding.
`risk-2` and `arch-2` established that `forcing_uri` is normative in `design-v1`
with no producer, no consumer, no migration row and no gate — a supplied row has
nothing that writes its `run_<id>.nc`. `design-v2.md` therefore **removes it from
the core**, because a normative column no rule reads is the worst of the two
options. This artifact is what makes that removal a decision rather than a
retreat: it states exactly what admitting a second family costs.

**The cost, named:**

1. one core column, `forcing_uri` (text, nullable, a path or URI), mutually
   exclusive with `derived_from`;
2. one rule, **3.11b `stage_supplied_forcing`**, whose input is the row's
   `forcing_uri` and whose output is `<wg>/output/run_<run_id>.nc`, with the same
   data-derived alternation treatment as 3.12 so the three producers stay
   unambiguous;
3. one WG-4 clause: the producer enumeration gains the supplied case;
4. one falsifier: a fresh-project DAG build with a three-producer id partition.

**Is a `forcing_uri` column family-specific?** No — and this is why its later
addition does not break the seam. "Where this run's series comes from" means the
same thing for any family that supplies series, and it evaluates to empty for one
that generates them, which is the same test `derived_from` passes in §5.2.2. So
the fourth core column is family-blind, and the seam contract survives its
addition. What would break the seam is a `gcm` or an `ssp` column reaching stage
2, and nothing here requires that.

**Goal 1 is therefore met with an asterisk, stated plainly:** admitting a second
family requires **adding** a stage-2 rule, not **editing** one. No existing
stage-2 rule changes, no existing rule branches on a family, and rules 3.14 /
3.15 / 3.16 are untouched — they see `run_<id>.nc` and cannot tell which of three
producers wrote it. `design-v2.md` §2.1 Goal 1 is reworded to say that, because
"no edit to stage 2" as written in v1 is false of any design in which a new
forcing source needs a producer.

## 5. What this artifact changes in `design-v2.md`

Recorded so the two documents are checkable against each other.

| # | Change | Section |
|---|---|---|
| 1 | E18's argument moves from raggedness to the join-and-pairing ground of §3 | §5.2.2, §7 |
| 2 | `forcing_uri` leaves the universal core; its re-admission cost is named | §5.1.2, §5.2.3, §10 Q8 |
| 3 | One scenario table carries exactly one family; a second is a file split | §5.1.2 |
| 4 | A declared paired relation with an all-empty `derived_from` is refused | §5.1.2 |
| 5 | Goal 1 restated: admitting a family **adds** a producer rule, never edits one | §2.1 |
| 6 | The empty-alternation case moves from assumed to probed (P2b / GF-2) | §5.2.3, §9 |

## 6. What this artifact does not establish

- **Nothing about whether such a family is worth building.** That is a later
  milestone and this document takes no position on it.
- **Nothing about comparability.** Whether a Variant-A run and a stochastic run
  may share a metric name is scope gap 5 / W3, deferred, and this exercise
  deliberately does not settle it — it only confirms that the schema does not
  foreclose it, since neither variant needs a reserved baseline id.
- **Nothing measured.** This is a paper schema. Its claims about the DAG's
  behaviour under an empty `DERIVED_FROM` are the same `[argued]` claims
  `design-v2.md` carries, and P2b is what would measure them.
