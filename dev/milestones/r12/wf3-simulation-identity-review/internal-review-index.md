# Internal review index — `design-v1.md`

Driver-authored aggregation over three lenses. **Grouping only.** Every original
finding ID, severity and text stays owned by its own review file; nothing here is
deleted, merged away, or re-graded. Where two lenses filed the same defect at
different severities, both severities stand and the divergence is recorded in
§ Conflicts — the author dispositions each ID at *its own* filed severity.

| lens | file | verdict | blocking | major | minor |
|---|---|---|---|---|---|
| Scientific & methodological soundness (1b, Fable) | `internal-review-domain.md` | revise | 1 | 6 | 3 |
| Architecture & internal consistency | `internal-review-architecture.md` | revise | 0 | 7 | 3 |
| Risk & assumptions | `internal-review-risk.md` | revise | 0 | 6 | 5 |
| **total** | | | **1** | **19** | **11** |

**31 findings. All must be dispositioned in `ledger.md` before the external
round**, including the four already ruled at G1.

## Already ruled at G1 — carried to the revision as accepted

Not open questions; the author implements them.

| ID | Ruling |
|---|---|
| `domain-1` (blocking) | **R-2** — Class C becomes `grain: run` + required `reference`. Accepted; results file gains rows, HM-7 and the baseline move |
| `domain-2` | **R-3** — the paired-sampling property gets a declared family-registry field |
| `domain-3` | **R-4** — `min_blocks` becomes a blocks-per-return-period ratio; picking the ratio is a milestone precondition |
| — | **R-1** — the Class-C month is selected in advance, shared across realizations; different calendar months are never pooled |

`domain-4` (no falsifier for `min_blocks`) is not separately ruled but is
consumed by R-4: a ratio the milestone must pick is a claim that needs a
falsifier, so R-4 does not discharge it.

## Groups — one defect, more than one lens

Independent arrival is the signal here. Two lenses reaching the same defect from
different directions is worth more than either alone, and the author should read
both texts before fixing.

### G-A — `forcing_uri` is a normative column with no implementation
`risk-2` (major) · `arch-2` (major)

Both filed independently, at the same severity, against the same subsections
(§5.1.2 `:271`, §5.2.3 `:391`, §5.6). Arch frames it as *no consumer anywhere in
the design*; risk frames it as *the design contradicting itself* — the seam
declares the column required and the exhaustive rule list never reads it, with no
producer, no migration row and no gate. Same defect, two framings; fix once.

### G-B — the WG-5 replacement is wrong in two independent ways
`arch-3` (major) · `risk-4` (major)

Different halves of §5.8, neither a duplicate of the other:
- `arch-3` — *"`validate_wg5` is untouched"* (`:1082-1083`) is false against the
  code: the validator **selects** entries by `k.startswith("rlz_")` and errors
  when there are none (`interchange_contracts.py:554-560`), so it fails on every
  catalog under a `run_<id>` key.
- `risk-4` — the replacement's cross-artifact invariant is unsatisfiable under a
  shipped configuration.

Fixing `arch-3` alone leaves a contract that cannot hold; fixing `risk-4` alone
leaves a validator that fails on contact. Both, or neither.

### G-C — the atomic migration commit is under-inventoried, and "atomic" is two ideas
`arch-6` (major) · `risk-11` (minor)

`arch-6` names live references the inventory omits (`indicator-glossary.md`,
`surface_axes.py`, `check_baseline.py`, the notebook, the tracked `indicator_ref`
CSV). `risk-11` says "one atomic commit" conflates **reference atomicity**
(`naming.md` §7 — no state where a live document names a dead path) with
something else, so the design over-constrains in one direction while
under-delivering in the other. **Severity divergence — see § Conflicts.**

### G-D — rule 3.09 acquires a stage-3 dependency with a half-working rerun trigger
`arch-7` (major) · `risk-8` (minor)

`arch-7`: the minter reads grain declarations to size `W`, so 3.09's output
content now depends on stage 3, with no rerun trigger — and afterwards the digest
guard misreports the cause. `risk-8`: the `params:` trigger the design does claim
covers only half the change space, because `bundle_by` is "a named function, not a
column", so what travels through `params:` is a name, not the function's
behaviour. Same mechanism, two failure modes. **Severity divergence — see
§ Conflicts.**

### G-E — the stale-lookup guard: built without reference to the one already here, and its remedy does not work
`risk-1` (major) · `arch-8` (minor)

`risk-1` is the more consequential and is close to a framing finding: the repo
**already has** a guard for this — `experiment.yml` records the resolved
`workflows.run_stress_test` section and `check_not_frozen`
(`write_experiment_config.py:191-239`) refuses any change once results exist —
and `realizations_num` and the perturbation grid are both inside that section.
The design analyses the stale-lookup hazard without citing it and then builds a
new guard in a shape that repository explicitly rejected. `arch-8` adds that the
documented remedy for the digest refusal does not clear the refusal.
**Severity divergence — see § Conflicts.**

### G-F — HM-7's replacement text is incomplete in three directions
`arch-4` (major) · `arch-10` (minor) · `risk-10` (minor)

`arch-4`: it silently drops assertions `validate_hm7` makes today (the
lookup-completeness and `rlz_id`-domain checks). `arch-10`: it pins `unit_id` at
"the namespace width" while §5.5.2 makes that width a function of the declared
bundle count, so an out-of-repo consumer cannot implement HM-7 standalone as C-7
requires. `risk-10`: for HM-2, HM-4, HM-5 and HM-6b the design supplies *an
instruction* rather than replacement text, against the intake's own success
criterion "normative text, not sketch".

## Singletons — one lens, no overlap

| ID | Sev | One line |
|---|---|---|
| `domain-5` | major | **GF-9 has no instrument.** `check_baseline.py:786-797,861-874` keys rows on every non-value column and structurally fails on a column-set change, so "no number moves" cannot be checked. R-2 sharpens this — the results file now changes column set *and* row count |
| `domain-6` | major | `reference` unit vs `evaluated` under `run_historical: false`, plus a live silent drop of two metrics at `export_wflow_results.py:362` |
| `domain-7` | major | No fit uncertainty is carried for the pooled GEV; W2's four columns leave no slot for it |
| `domain-8..10` | minor ×3 | See the domain file; `domain-10` is the E18 paper-schema point, which `risk-3` reaches independently |
| `arch-1` | major | **The load-bearing family-blindness rule is stated three times at three scopes, and the design's own rule table violates the strictest.** `:340` admits no exception; §5.6's rule-3.12 row requires `st_id` read and passed as `params:`; §5.3.3 and GF-11 each state a *different* exception. GF-11's instrument has no referent, because §2.2 makes splitting the `.smk` a binding non-goal, so there is no "stage-2 module" to test |
| `arch-5` | major | §5.1.5/GF-4's pull-semantics argument for `evaluated` does not apply to rule 3.15, whose batch outputs are **static Python lists** — consistent with intake E2, which the design does not connect to it |
| `arch-9` | minor | §5.6's rule-3.11 output has no `temp()`, while §5.7b says the `temp()` lifecycle is unchanged |
| `risk-3` | major | **The design's highest-consequence unmeasured claim is gated only *after* the migration's point of no cheap return**, though a cheap pre-commit measurement exists now. See § Gate return |
| `risk-5` | major | `st_id` is **empty** on the baseline row (§5.1.2, "not zero") and `bundle_by = same_design_point` is "equal `st_id`, any `rlz`" — the design never says whether empty is a valid grouping key, and it has to be |
| `risk-6` | major | **A3's rejection is deference, not argument** — "W4 rules against it… and the design does not need it". Risk's claim: *W4 is not a ruling*; it sits under the intake's explicitly provisional working-direction heading. See § Gate return |
| `risk-7`, `risk-9` | minor ×2 | Run-id minting order is undefined; the epistemic label taxonomy is not applied to its own definition (≈12 claims labelled `[measured — read the function]`) |

## Conflicts

The index's valuable half. Neither reading is resolved by the driver.

### C-1 — Severity divergence ×3, all on the same axis

| Defect | Filed `major` by | Filed `minor` by |
|---|---|---|
| Migration atomicity (G-C) | `arch-6` | `risk-11` |
| 3.09's stage-3 dependency (G-D) | `arch-7` | `risk-8` |
| Stale-lookup guard (G-E) | `risk-1` | `arch-8` |

Not random. In each case the lens that owns the *territory* graded higher: the
architecture lens on the migration and the rule graph, the risk lens on the
guard's framing. Each ID is dispositioned at **its own** filed severity — the
no-re-grade rule already forbids harmonising them, and this table is where that
is made visible rather than silently preserved.

### C-2 — Corroboration, recorded because it is evidence

The risk lens states it **independently re-derived `domain-1` (Class C's grain)
and `domain-5` (GF-9's comparator) and confirmed both against the code**, then
declined to re-file them. Two lenses on different models reaching the same
conclusion from different prompts is the strongest evidence the panel produced —
and it is invisible in a finding count, because the corroboration was correctly
*not* filed as a finding. Recorded here so it is not lost.

### C-3 — What authority does W4 carry? (unresolved, and it decides a design question)

`risk-6` asserts *"W4 is not a ruling"* — it sits under the intake's
`## Working direction — initial, NOT settled` heading, whose own text says *"these
are not definite decisions… We shall solidify along the way."* The design rejects
alternative A3 (two id sequences) partly by deference to it.

The driver does not resolve this. **Both readings are defensible on the intake's
own text**, and they lead to different work:

- *W4 as direction* — the design's rejection of A3 stands, but must be re-argued
  on merits rather than on deference.
- *W4 as open* — A3 is live, and the identity scheme is back in play.

Note the design also **already departed from W4 once**, deliberately and with
reasons (two column *names* over one sequence, §5.5.1, recorded as such). So the
draft does not treat W4 as binding either — which makes the deference in A3's
rejection internally inconsistent regardless of which reading wins.

## Gate return — recommended before the revision is dispatched

`stage-contracts.md` § Gate return from the panel: *"When the panel's findings
admit resolutions that differ in scope, constraints, or the selected alternative,
return to G1 before dispatching the revision"* — cheaper than letting the author
pick and bouncing at G2 with a spent revision.

**Two findings qualify. Neither is a defect the author can simply fix.**

1. **`risk-6` / C-3 — W4's authority.** Resolutions differ in the *selected
   alternative*: one keeps a single sequence, the other reopens A3. The author
   cannot settle what an owner's provisional direction obliges.

2. **`risk-3` — when the design's central claim gets measured.** The claim is
   E18/D1: that a supplied or GCM-derived scenario set is not expressible as
   `(rlz, st)` and *is* expressible in the proposed schema. The intake marks E18
   **HYPOTHESIS — asserted, no artifact exists**; `domain-10` reaches it from the
   method side and proposes a one-page candidate-family schema as the settling
   measurement. Risk's addition is the *timing*: as written the claim is gated only
   after the migration's point of no cheap return, while the measurement is cheap
   **now**. Whether the milestone acquires that as a precondition is scope — the
   same shape of decision as R-4, which the owner has already taken once.

Everything else on this page is ordinary revision work.
