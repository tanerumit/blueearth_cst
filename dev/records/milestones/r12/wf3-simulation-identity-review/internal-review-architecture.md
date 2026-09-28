# Internal review — architecture & internal consistency (stage 1b)

> Lens: architecture referee. Run `wf3-simulation-identity`, milestone R12.
> Reviewed: `design-v1.md` (1565 lines) against the frozen intake, the executed
> P1/P2 probes, the domain lens's findings, and the repository.
> The G1 settled framing (three stages, family-blind seam, R-1..R-4) is taken as
> ruled; no finding below asks to reverse it. Read-only review; the only file
> written is this one.

```yaml
verdict: revise
doc_version: design-v1.md
findings:
  - id: arch-1
    severity: major
    section: "5.2.1 What it is (the normative stage-2 rule); 5.3.3; 5.6; 9 GF-11"
    finding: >
      The design's load-bearing normative rule is stated three times at three
      different scopes, and its own rule table violates the strictest statement.
      `design-v1.md:340` reads "Stage 2 code MUST NOT reference any column outside
      the core", with no exception. §5.3.3 (`:472-476`) narrows it to "must not read
      the scenario table's family block ... for any purpose other than passing the
      design parameters through to the generator". GF-11 (`:1520`) narrows it again
      and differently, to "naming `rlz`, `st_id` or `scenario_family` **outside a
      `params:` passthrough**". §5.6's rule-3.12 row (`:1003`) then requires exactly
      the excepted thing: "the design-point argument becomes the row's `st_id` from
      the scenario table, passed via `params:`" — and `st_id` is a member of
      `FAMILY_COLUMNS` (`:213-217`). So `:340` as written is false of the design's
      own specification, and a reader cannot tell which of the three sentences is
      the contract. Worse, GF-11's instrument is not constructible: it is "a static
      test asserting no stage-2 module mentions a name in `FAMILY_COLUMNS`", but
      §2.2 makes "Splitting the WF3 `.smk` file" a binding non-goal (`:107-110`), so
      rules 3.11/3.12/3.14/3.15 (stage 2), the stage-1 minting call and rule 3.16
      (stage 3) all live in `run_stress_test.smk`. "No module under the stage-2
      boundary" has no referent in a single-file workflow, and the one place the
      leak actually occurs — a `params:` lambda inside rule 3.12 — is in the same
      file as everything else.
    rationale: >
      Family-blindness at the 1-to-2 seam is the whole justification for the change
      (D1, §4 `:299-302`, which states that if the resolution is wrong "the seam
      must move"). A normative rule that the design's own rule table breaks, plus a
      falsifier that cannot be built, means the property is asserted rather than
      enforced — which is the exact defect class (an unstated invariant nobody
      re-checks) that §1's four leaks are about. It also matters practically: the
      `st_id` params lambda is family-specific stage-2 code, so admitting a family
      without an `st_id` column requires editing stage 2, which Goal 1 (`:64-67`)
      forbids.
    suggested_fix: >
      Rewrite `:340` to the rule the design actually means and can gate — e.g.
      "Stage 2 rules MUST NOT branch on, filter by, or derive a path from any
      family-block column; a family-block value may travel as an opaque `params:`
      payload to a family-specific script" — and state it once, deleting the two
      divergent restatements. Then respecify GF-11's instrument against something
      that exists in a single-file workflow: an explicit per-rule declaration of
      stage membership plus an AST test over the named rule bodies, or a
      `family_payload(row)` accessor in `scenario_families.py` that is the ONLY
      permitted reader, with the static test asserting no bare `FAMILY_COLUMNS`
      name appears in a stage-2 rule body.

  - id: arch-2
    severity: major
    section: "5.1.2 Schema — normative; 5.2.3 Seam schema; 5.6 Rule-level changes"
    finding: >
      `forcing_uri` is a required column of the normative seam with no consumer
      anywhere in the design. §5.1.2 (`:271`) defines it and §5.2.3 (`:391`) says
      stage 2 uses it for "the forcing path for a supplied family" — but the same
      subsection's exhaustive list of what stage 2 derives from the seam names only
      three objects (`RUN_IDS`, `DERIVED_FROM`, `EVALUATED_IDS`, `:396-400`) and
      omits it; §5.6's rule table specifies no rule that reads it; §5.7b's WG-4
      replacement covers only "generated *ab initio* (rule 3.11) or by
      transformation (rule 3.12)" (`:1035-1039`), i.e. the two cases where
      `forcing_uri` is empty; and it appears in neither §8.1 nor §9. Concretely,
      §5.6's rule-3.11 row defines `ROOT_IDS` as "the run ids with empty
      `derived_from` **and** empty `forcing_uri`", so for a supplied family
      `ROOT_IDS` is empty, rule 3.11 has an empty output list, and every row with a
      non-empty `forcing_uri` has no producer for
      `<exp>/climate/weathergenr/output/run_<id>.nc` at all.
    rationale: >
      This is the one column that would carry the second scenario family the whole
      design exists to accommodate, and it is specified into the contract without a
      path into the DAG. Goal 1 says "admitting a second scenario family must
      require no edit to stage 2" (`:64-67`); as specified, a supplied family
      requires a new stage-2 rule, so the goal is not met by the shipped rule set.
      Either the column is doing work and needs a rule, or it is a placeholder and
      should be labelled as one — but a normative seam column that no gate exercises
      and no rule reads will be implemented as a no-op and discovered later.
    suggested_fix: >
      Either (a) specify the staging rule — a rule 3.11b `stage_supplied_forcing`
      whose input is the row's `forcing_uri` and whose output is
      `run_<run_id>.nc`, with the same `wildcard_constraints` alternation treatment
      as 3.12 so the three producers stay unambiguous, plus a GF row; or (b) mark
      `forcing_uri` explicitly as reserved-and-unconsumed in §5.1.2 and §5.2.3 (the
      same treatment `location = basin` already gets under Q11), state that a
      supplied family is not runnable in this milestone, and ship the exclusivity
      validator only. Whichever is chosen, add `forcing_uri` to §5.2.3's derived-
      object list or say why it is absent.

  - id: arch-3
    severity: major
    section: "5.8 WG-5 replacement text"
    finding: >
      §5.8 states "`validate_wg5` (per-entry schema) is untouched, since no
      per-entry field changes" (`:1082-1083`). That is false against the code.
      `validate_wg5` does not merely validate fields — it SELECTS the entries by
      key prefix and fails when there are none
      (`blueearth_cst/shared/interchange_contracts.py:554-560`):
      `entries = {k: v for k, v in cfg.items() if isinstance(k, str) and
      k.startswith("rlz_")}` followed by
      `if not entries: diffs.append(f"{label}: no 'rlz_<n>_st_<m>' entries in
      catalog")`, with the key pattern also carried in its docstring (`:525`,
      `:536-537`). Under the design's own replacement the sole entry key becomes
      `run_<run_id>` (`:1071`), so `validate_wg5` finds zero entries and reports a
      contract violation on every well-formed catalog.
    rationale: >
      The brief's highest-value defect class is a schema disagreeing with the
      contract text that pins it, and this is that in its purest form: the design
      positively asserts a validator is unaffected by a change that breaks it. It
      also propagates into §8.2's atomic commit, which lists "`interchange_contracts`
      (WG-2/4/5/6, HM-2/4/5/6b/7)" but whose §5.8 rationale tells the implementer
      that the WG-5 per-entry validator needs no edit — so the one-commit atomicity
      obligation (D7) is briefed against an incomplete target.
    suggested_fix: >
      Replace the "untouched" clause: `validate_wg5`'s entry selector and its
      no-entries diagnostic move from the `rlz_` prefix to `run_`, and its docstring
      moves with them. Per-entry FIELD validation is what is unchanged; say that
      instead.

  - id: arch-4
    severity: major
    section: "5.9 HM-7 replacement text"
    finding: >
      The HM-7 replacement enumerates what `validate_hm7` asserts and silently drops
      assertions the validator makes today. §5.9 (`:1156-1159`) says it asserts "in
      addition to the header, the vocabulary and the metric/table agreement it
      asserts today: the six `unit_index` invariants ... and each metric's emitted
      grain against its declaration", and that its `rlz_num` / `lookup` arguments
      "are replaced by `unit_index` and `scenario_table`". But the live validator
      also asserts (a) the `rlz_id` domain — `allowed = {POOLED_REALIZATION} |
      set(range(1, int(rlz_num) + 1))` (`interchange_contracts.py:947-953`), and
      (b) two-directional completeness against the lookup plus the `st_0` partition:
      every lookup `st_id` produced rows, no emitted `st_id` is unknown to the
      lookup, and the baseline token is present in the tables and absent from the
      lookup (`:995-1038`). Nothing in the replacement re-expresses (b) through the
      new join path (`unit_id` -> `unit_index.member_run_id` -> `scenario_table.st_id`
      -> `stress_test_lookup.st_id`). The `unit_index` invariants of §5.4.3 assert
      resolvability and namespace completeness, which is a different property from
      "every configured design point produced rows".
    rationale: >
      Contract-replacement text is what a re-implementer and the migration commit
      both work from. Dropping a validator's design-point completeness check
      converts a loud failure into a silently shorter results file — the same class
      of defect the design attacks elsewhere (`AGENTS.md` "no silent caps"), and it
      would be attributed to this migration rather than to the omission. §5.4.3's
      invariant 6 says a truncated reduce must be "a failure rather than a shorter
      table"; without the re-pointed lookup check that guarantee is weaker than
      today's for the stochastic family.
    suggested_fix: >
      Add to §5.9's `validate_hm7` list: the lookup-completeness pair and the `st_0`
      partition, re-expressed over the join `unit_index` -> `scenario_table` ->
      lookup, and state explicitly what replaces the `rlz_id` domain check (the
      run-id domain against the scenario table, presumably) rather than leaving it
      to be inferred from the argument swap.

  - id: arch-5
    severity: major
    section: "5.1.5 `run_historical`, without a baseline concept; 5.6 (rule 3.15); 9 GF-4"
    finding: >
      §5.1.5's mechanism for `run_historical: false` is wrong for the rule that
      actually produces the run CSVs. It argues "Because Snakemake is pull-based,
      `<runs>/output/run_<id>.csv` is simply never requested for an unevaluated row"
      and calls this "the same pull semantics `ST_START` already relies on at
      `:1247`" (`:322-330`). Rule 3.16's `expand()` at `run_stress_test.smk:1247` is
      indeed pull-based, but rule 3.15 is not: it is loop-generated per batch with
      **static** output lists sliced from `_k_members` —
      `csvs = [f"{runs_dir}/output/rlz_{rlz_ix(r)}_st_{st_ix(c)}.csv" for (r, c) in
      _members]` (`run_stress_test.smk:1226-1231`) — so any member in `_k_members` is
      an unconditional output of its batch rule. What excludes the baseline today is
      not pull semantics but `ST_START` filtering `_k_members` at `:1120`. §5.6's
      rule-3.15 row (`:1005`) says only "`_k_members` becomes a flat list of
      `run_id` strings" and never says the list is `EVALUATED_IDS`; taken literally
      with §5.5.2's "ids are minted for **every** scenario-table row" (`:833-836`),
      the unevaluated baseline re-enters the batch rule and is simulated.
    rationale: >
      This is the strongest of the majors because it ends in numbers. An
      unevaluated baseline that is nonetheless simulated adds `run_<baseline>.csv`
      to a GF-9-covered reduce, so the "output-neutral" claim would be violated on
      exactly the `run_historical: false` configuration, and the design's stated
      mechanism would not explain why. It is also a mis-citation of the repository:
      `:1247` is cited to license a claim about a rule at `:1216-1241` that works
      differently.
    suggested_fix: >
      State in §5.6's rule-3.15 row that `_k_members` is built from `EVALUATED_IDS`,
      not `RUN_IDS`, and correct §5.1.5's mechanism sentence: the exclusion is a
      filter on the batch member list, exactly as `ST_START` is today, not pull
      semantics. Extend GF-4's falsifier to assert the baseline's csv is absent from
      the *batch rule's declared outputs*, not merely absent from the job list.

  - id: arch-6
    severity: major
    section: "8.2 Sequence — one atomic rename plus a shape change (D7)"
    finding: >
      §8.2 step 1's commit inventory is incomplete against D7's own obligation
      ("every live reference updated in the same commit") and against `AGENTS.md`'s
      "grep the old spelling and fix every live reference in the same commit". Live
      references to the retired `st_id` / `rlz_id` results columns that step 1 does
      not name: `dev/reference/indicator-glossary.md`, which documents per-metric
      grain as `rlz_id = 0` (`:101-104`) and the two key columns (`:154-155`) and is
      pinned row-for-row against the code by `tests/test_indicator_glossary.py`;
      `blueearth_cst/shared/surface_axes.py`, whose `read_indicators` reads an
      indicator table with `dtype={"st_id": str}` (`:295-305`) — a function that
      cannot survive the four-column header, despite §5.9 stating `surface_axes.py`
      "stays the reference implementation" (`:1151`); `dev/scripts/check_baseline.py`,
      whose `TARGETS` is a HARDCODED list (`:237`) and whose `_indicator_key_columns`
      (`:788`) and the `st_id`-is-text note at `:771` both encode the old header;
      `dev/baseline/indicator_ref/74ed83c06b2e7e6c.csv`, a tracked reference table
      carrying the old columns; and `docs/notebooks/Climate Stress Test.ipynb`, which
      is in-repo, not an out-of-repo consumer, so C-7's "out of scope to fix"
      disposition does not cover it. The hardcoded `TARGETS` also falsifies §5.4.3's
      claim that `unit_index.csv` "becomes a baseline-fingerprinted `rule all` target
      — which is free **now**" (`:568-572`): the manifest's target set is seven
      explicitly declared paths (`dev/baseline/manifest.json`), so covering the new
      file is an edit to `check_baseline.py`, not a consequence of re-recording.
    rationale: >
      An atomic-rename plan whose inventory is short is an atomic-rename plan that
      lands broken: `tests/test_indicator_glossary.py` and `tests/test_surface_axes.py`
      fail on the same commit that is supposed to be self-consistent, and the
      implementer discovers the missing entries one gate at a time. This is
      independent of domain-5, which is about whether `check_baseline.py`'s
      comparator can execute GF-9; this finding is that the file is absent from the
      commit inventory at all, and that its `TARGETS` list is hardcoded.
    suggested_fix: >
      Extend §8.2 step 1's list with `dev/reference/indicator-glossary.md`,
      `blueearth_cst/shared/surface_axes.py` (say which functions change),
      `dev/scripts/check_baseline.py` (`TARGETS`, `_indicator_key_columns`, the
      `st_id` note), the regenerated `dev/baseline/indicator_ref/*.csv`, and
      `docs/notebooks/Climate Stress Test.ipynb`. Correct §5.4.3's "free" claim to
      "requires adding one row to `check_baseline.TARGETS`".

  - id: arch-7
    severity: major
    section: "5.5.2 One sequence, one width; 5.6 (rule 3.09); 5.5.3 the digest guard"
    finding: >
      Rule 3.09's output content acquires a dependency on stage 3 with no rerun
      trigger for it. §5.5.2 sets `W = index_width(len(runs) + len(bundles))`
      (`:800`) and states the minter "reads the grain declarations" to size the
      field (`:846-850`), so the `run_id` strings written into
      `scenario_table.csv` — and therefore the file and its digest — depend on the
      grain declarations in `shared/indicator_tables.py`. §5.6's rule-3.09 row
      (`:1000`) adds `scenario_table.csv` and the digest sidecar and adds no rerun
      trigger for the grain declarations, while the same section's own paragraph
      (`:1013-1018`) documents the live trap for exactly this shape — rule 3.09's
      config inputs are `ancient()` so `params.stress_test_cfg` is its only trigger
      (`run_stress_test.smk:882-887`). The design asks this question of rule 3.16
      (P4 / GF-6) and never of rule 3.09. The consequence compounds with §5.5.3: a
      grain-declaration edit that crosses a power of ten leaves a stale-width table
      on disk beside a new-width parse-time namespace, and the digest guard then
      refuses the run reporting a *changed scenario set* when the scenario set is
      byte-identical — a diagnosis that points the user at the wrong artifact.
      §5.5.2's bound 3 records the refusal as a benefit ("it is **loud**", `:869`)
      without noting that the message is wrong or that clearing it costs the whole
      stage-2 sweep.
    rationale: >
      The design's answer to the stale-lookup hazard (D3) is the digest, and a
      guard that fires on a change of a different kind and names the wrong cause is
      worse than a narrower guard. It also inverts the stage boundaries the design
      is drawing: a stage-3 metric edit invalidating every stage-2 output is the
      coupling the three-stage split exists to remove, and it is not stated as a
      consequence in §7.
    suggested_fix: >
      Give rule 3.09 a `params:` carrying the grain declarations (or their digest),
      matching what §5.3.4 does for rule 3.16, and add a GF row beside GF-6.
      Separately, either separate the width term from the digest term — digest the
      scenario table's family-block and edge content, not its `run_id` spelling — or
      add a distinct diagnosis for a width change so the refusal names the metric
      declaration rather than the scenario set. Add the "a new grouping invalidates
      the sweep" consequence to §7 beside C-4.

  - id: arch-8
    severity: minor
    section: "5.5.3 The stale-lookup guard; 8.3 Rollback"
    finding: >
      The documented remedy for the digest refusal does not clear the refusal.
      §5.5.3 writes the digest to `<exp>/config/.scenario_table.sha256` (`:891`) and
      tells the user the two resolutions are a new experiment or to "delete the
      experiment's run outputs deliberately" (`:896-899`); §8.3 spells that
      deletion out as "the experiment folder's `climate/`, `hydrology/` and
      `results/` subtrees" (`:1444-1446`). The sidecar lives under `config/`, which
      neither list includes, so following the documented remedy leaves the stale
      digest in place and the run still refuses at parse time. Relatedly, the digest
      is written to two places — the sidecar and `run_metadata.json` via rule 3.16b
      (`:892-895`) — with no statement of which is authoritative; only the sidecar
      is read.
    rationale: >
      A parse-time refusal whose stated remedy is incomplete is a dead end the user
      hits at exactly the moment the design intends to be maximally clear, and the
      refusal is explicitly not silenceable by a flag.
    suggested_fix: >
      Add `config/.scenario_table.sha256` to both deletion lists, or have the guard
      delete the sidecar itself when the user re-runs after clearing outputs. State
      that the sidecar is authoritative and `run_metadata.json`'s copy is a record.

  - id: arch-9
    severity: minor
    section: "5.6 (rule 3.11); 5.7b WG-4 replacement"
    finding: >
      §5.6's rule-3.11 row gives the new output as a bare list comprehension —
      "`[f\"{wg_dir}/output/run_{rid}.nc\" for rid in ROOT_IDS]`" (`:1001`) — with no
      `temp()`, while §5.7b's WG-4 replacement says "the `temp()` lifecycle ... is
      **unchanged**" (`:1043-1045`) and the live rule wraps it
      (`run_stress_test.smk:990`, `temp([...])`).
    rationale: >
      A schema-vs-pinning-text mismatch of exactly the class this review is looking
      for, and cheap to fix. If an implementer follows §5.6 literally the baseline
      realization NCs stop being temporary, which `AGENTS.md` names as the change
      that "explodes disk usage on large `RLZ_NUM x ST_NUM` runs".
    suggested_fix: Restore `temp(...)` in §5.6's rule-3.11 row.

  - id: arch-10
    severity: minor
    section: "5.9 HM-7 replacement text; 5.5.2; 7 C-7"
    finding: >
      HM-7's replacement pins `unit_id` as "Zero-padded **text** at the namespace
      width" (`:1121`) and the design requires HM-7 to be "implementable standalone"
      by out-of-repo consumers (C-7, `:1266`). But §5.5.2 makes that width a
      function of the declared bundle count in `shared/indicator_tables.py`
      (`:800`, `:846-850`) — a repository-internal, version-dependent quantity an
      out-of-repo re-implementer cannot compute. The contract therefore pins a value
      it does not define.
    rationale: >
      Minor because the practical remedy for a consumer is to read the width off
      the file, and the design already insists every id is read as text. Worth
      fixing because the sentence as written implies a derivable constant.
    suggested_fix: >
      Say instead that every `unit_id` in one results set shares one width, that the
      width is discovered from `unit_index.csv` rather than computed, and that a set
      mixing widths is malformed — the same formulation WG-2 already uses for
      `st_id`.
```

## Identifier trace

`run_id` / `unit_id`, end to end, as the brief asks. Two breaks and one
mis-citation fall out of it; the rest holds.

1. **§5.1.2 `:266`** — minted in the scenario table as "text, zero-padded, width
   `W`", unique, "the **only** thing that appears in a stage-2 filename". Companion
   core columns `derived_from`, `forcing_uri`, `evaluated` (`:269-274`).
2. **§5.2.3 `:388-400`** — the seam view carries all four; stage 2 derives
   `RUN_IDS`, `DERIVED_FROM`, `EVALUATED_IDS`. **Break 1:** `forcing_uri` is in
   the seam table and absent from the derived-object list, and is never mentioned
   again in any rule, migration row or falsifier (arch-2). The alternation
   constraint is `"|".join(DERIVED_FROM)` — keys, i.e. derived ids — which agrees
   with GF-1's falsifier text at `:1477` ("the constraint's alternation set equals
   `DERIVED_FROM`'s keys"). Consistent.
3. **§5.3.2 `:432-441`** — six artifact paths, each `run_<run_id>`, one token one
   spelling. Agrees with §5.8's catalog entry key `run_<run_id>` (`:1071`) and with
   §5.7b's WG-4/WG-6 replacements (`:1035-1049`).
4. **§5.6 `:1000-1008`** — 3.09 writes the table; 3.11 enumerates `ROOT_IDS`; 3.12
   constrains on `DERIVED_FROM` and takes `st_id` via `params:` (**arch-1**);
   3.14 wildcards `{run_id}` at width `W`; 3.15's `_k_members` becomes "a flat list
   of `run_id` strings" (**break 2 / arch-5** — silent on `EVALUATED_IDS`, and the
   batch rule's outputs are static, so the §5.1.5 pull-semantics justification does
   not reach it); 3.16 addresses runs through `RUN_CSV_BY_ID` keyed by `run_id`
   (§5.3.4 `:490-501`).
5. **§5.4.2 `:521-537`** — the run's `run_id` reappears as `unit_id` in
   `metric, location, unit_id, value`, same value space and width per §5.5.1
   (`:775-779`). **§5.4.3 `:582-590`** — `unit_index.csv` is
   `unit_id, grain, member_run_id`, with a run unit's `member_run_id` equal to its
   `unit_id` (invariant 4, `:606-607`). The three column names are mutually
   consistent, and the long shape supports both join directions as claimed.
6. **§5.9 `:1104-1128`** — HM-7 pins the same four columns in the same order,
   `unit_id` as zero-padded text "at the namespace width" (**arch-10**), and adds
   the two consumer rules (join-before-group, resolve-or-fail). The header text
   matches §5.4.2 exactly — no drift. What does drift is the validator list, which
   drops assertions the live `validate_hm7` makes (**arch-4**).
7. **§8.1 `:1394-1404`** — rows 1-8 map every `rlz_<r>_st_<m>` path onto
   `run_<run_id>`, and the column-label line maps `st_id, rlz_id -> unit_id`. Row 5
   correctly notes the catalog **entry key** moves with the filename. Complete for
   paths; incomplete for the surrounding machinery (**arch-6**), and silent on
   `forcing_uri`.
8. **§9 `:1477-1524`** — GF-1 (alternation), GF-4 (`evaluated`, **arch-5**),
   GF-10 (`unit_id` resolves), GF-11 (stage-2 blindness, **arch-1**). No GF row
   exercises `forcing_uri`, and none exercises rule 3.09's rerun trigger
   (**arch-7**).

Net: the *column names and header orders* are internally consistent everywhere —
`run_id` -> `unit_id` -> `member_run_id` never drifts in spelling, order or type,
and the four-column header is identical in §5.4.2, §5.9 and §8.1. What breaks is at
the edges: one core column with no consumer, one rule whose mechanism is mis-cited,
and a validator/inventory surface described more optimistically than the code
supports.

## Scope-gap completeness (intake §"Eight gaps")

- **Gaps 1, 2, 3 — closed in normative text.** The three schemas are written with
  types, nullability, ordering and refusal conditions (§5.1.2, §5.2.3, §5.3.2); the
  id's form, width, sequence and guard are settled in §5.5.1-§5.5.3; and §5.1.4
  answers "written by what" with a pure function plus a recording rule, bound by
  P1's measured cases. These are implementable as written.
- **Gap 4 — closed in structure, and under revision.** The grain declaration record
  (§5.4.1) and the unit index (§5.4.3) are specified; the Class-C row is being
  corrected under R-2 and is not re-filed here.
- **Gap 5 — deferred, and the deferral is real rather than nominal.** §5.3.5's two
  conditions (no reserved baseline id; the hardcoded `0` at
  `export_wflow_results.py:362` made indirect) are the right pair, and §6 A5/A8
  reject the two mechanisms that would have foreclosed it. This is the design's
  cleanest gap.
- **Gap 6 — mechanism specified, value not.** Outside this lens; domain-3/-4 hold it.
- **Gap 7 — closed in structure, defective in content.** The clause count is
  corrected from three to nine (§5.7b), which is the right move, but two of the
  three substantive replacements are wrong or short: WG-5's asserts a validator is
  untouched that breaks (arch-3), and HM-7's drops live assertions (arch-4). The six
  one-line path substitutions are fine.
- **Gap 8 — closed in structure, incomplete as an engineering object.** The
  supersession mechanism is right (a new ADR under `dev/decisions/`, next free
  number **0009** — confirmed, `dev/decisions/` runs 0001-0008 plus `index.md`), the
  sealed record is correctly left unedited, the migration-note path
  `dev/milestones/r12/migration_scenario-identity.md` matches `naming.md` §7's
  mandated `migration_<topic>.md` form and the nine existing notes, and §5.10's
  reason-by-reason supersession of C24/C28 with C25 explicitly retained is
  well-built. What is not closed is the commit inventory (arch-6) and rule 3.09's
  rerun trigger (arch-7).

Sentences that read as normative but do not constrain an implementer:
`:340` (arch-1), §5.2.3's `forcing_uri` row (arch-2), §5.8's "validate_wg5 is
untouched" (arch-3), §5.4.3's "free **now**" (arch-6).

## What I checked and did not file

- **Repo homes.** `blueearth_cst/shared/scenario_index.py` and
  `scenario_families.py` are correctly placed: both are imported by Snakemake
  `script:` modules and by the Snakefile at parse time, which is exactly what
  `blueearth_cst/` is for under `AGENTS.md` § Repo Map. **Nothing in the design
  requires importing `dev/` from a run path** — `semantic_tree_diff.py` and
  `check_baseline.py` stay inspection-only, and the design edits them from the
  outside rather than calling into them from a rule.
- **Rule numbering.** §5.6 keeps every rule number and inserts none, honouring
  `naming.md` §8b and the `3.13`-is-not-reused precedent at
  `run_stress_test.smk:1058-1061`. `3.16b` is used, not `3.17`, consistently.
- **Wildcard vocabulary.** `run_id` is a new wildcard and `naming.md` §4 requires
  the vocabulary table to be updated in the same commit; §8.2 step 1 does name
  `naming.md` §4 + §7. Covered.
- **Column-name pair.** The `run_id` / `unit_id` split (§5.5.1) is argued as a type
  declaration and is internally consistent with the seam contract and with
  invariant 4; A1 records the single-name alternative with a real defeater. Sound.
- **§5.5.4 `member_hash`.** The separation of a freshness digest from a join handle,
  and the decision to take the idea at table grain only, is correct and does not
  foreclose the execution-model milestone. Nothing to add.
- **`derived_from` acyclicity and exclusivity** (§5.1.2) are checkable predicates
  stated at the right place (parse time, in the minter), and the placement matches
  the existing `refuse_out_of_domain_multipliers` precedent.
- **The two pre-existing defects the driver flagged** (E13's WG-2/WG-4
  mis-attribution; HM-7's seven-pinned-vs-five-asserted) — the design reports both
  accurately in §5.7b and §5.9, and its `run_`-token replacement for WG-4 is
  correct and complete on the naming-pattern clause. Not re-filed.
- **`ruleorder` / reserved-range alternatives** (§6 A4, A5): the rejections match
  what P2 measured and what W3 forbids. No disagreement.
- **Rollback shape** (§8.3): one commit, one revert, plus restoring the pre-change
  manifest — correct as far as it goes; the one gap is the deletion list, filed as
  arch-8. The "a half-renamed tree is the one state neither scheme can read"
  reasoning is right and I would not change it.
- **Domain-lens overlap avoided.** arch-6 is the commit-inventory and hardcoded
  `TARGETS:237` claim, NOT domain-5's comparator-cannot-execute claim; arch-5 is the
  static-batch-output mechanism under `evaluated`, NOT domain-6's
  reference-unit-must-be-evaluated precondition.
