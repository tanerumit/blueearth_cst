Task Brief — P1c: the per-variable registry

### Context

Canonical ruleset: `AGENTS.md`. Design: `config-shape-design.md` §5.5, §7.3,
D-10.6. Program: `config-shape-master-brief.md` (v4).

**This phase did not exist until 2026-08-26.** P1b found that three register
rows all depend on one thing no phase builds, and the owner ruled a new phase
rather than widening P1b. The finding, in one sentence: `C-57` calls the short
form of `variables:` *"registry-resolved"*, and there is no registry.

- `variable_spec.parse` (`blueearth_cst/projections/variable_spec.py:54`)
  requires `source`, `canonical`, `units` and `change` on EVERY variable and
  raises when any is missing. There is no lookup table behind it, so a bare
  `precip:` resolves to nothing.
- `C-64`'s destination — D-10.6's *"an attribute of one ENTITY → that entity's
  registry"* — is that same absent registry.
- `C-66` therefore cannot land either, and this is the row that would do harm
  if forced. `relative_change:` is ALREADY refused by `RETIRED_KEYS`, so on a
  v2 config `_relative_cfg` is `{}` and the shipped defaults stand. That is
  survivable for `precip` (`DEFAULT_MIN_REFERENCE = {"precip": 0.1}`) and NOT
  survivable for anything else: `resolve_thresholds` raises `ThresholdError`
  for a `change: relative` variable with no shipped default, and with
  `relative_change:` retired there is no longer any way to supply one. A
  configurable value becomes an unfixable error.

**Three registries exist today and none is the one this needs.** Whether they
unify is Gate 1's question, not an assumption this brief makes:

| what | where | carries |
|---|---|---|
| `CLIMATE_VARS` | `climate_analysis/climate_figures.py:83` | `label`, `unit`, `how`, `style` for `precip`/`temp`/`pet` — WF0's figures |
| `DEFAULT_MIN_REFERENCE` | `projections/dry_month.py:32` | `{"precip": 0.1}` — `C-64`'s content |
| `VariableSpec` fields | `projections/variable_spec.py:40` | `source`/`canonical`/`units`/`change`, declared per-config today |

`C-49` (move `CLIMATE_VARS` out of Python) is a SEPARATE row that the design
says *"pairs with `C-57`"* and is otherwise unaffected. It is not in this
phase's Required changes; Gate 1 decides whether it should be.

### Goal

A per-variable registry exists, `variables:` accepts the short form against it,
and `relative_change:` dissolves without removing anyone's ability to configure
a threshold.

### Non-goals

- **Rewriting any config file.** P3 ships the rewriter, P4 runs it. Fill in
  `tests/data/v2/project_config_v2_probe_analyze_projections.yml` instead,
  which P1b owns and left on the LONG form deliberately.
- The guard, the freeze, `CONFIG_PROJECTION` — P2.
- `C-49` unless Gate 1 rules it in.
- The `snake_config_` → `project_config_` rename — P5.
- Reopening `C-48`, withdrawn from R14 by D-7.10 and boarded as `t2608242212`.

### Allowed scope

**Permitted**
- `blueearth_cst/projections/**` (`variable_spec.py`, `dry_month.py` above all)
- `analyze_projections.smk`
- `tests/**`, including `tests/data/v2/**`
- wherever Gate 1 rules the registry lives, if that is a new file

**Approval-gated** — released by Gate 1, not by this brief
- `config/advanced_settings.yml` + `_ADVANCED_SETTINGS_SCHEMA` in
  `snake_utils.py`, for `C-65` only. A coupled edit: the schema is closed, so
  the file and the schema move in ONE commit or they drift silently. P1b did
  exactly this for `C-54` and it is the pattern to copy.
- `blueearth_cst/climate_analysis/climate_figures.py`, only if Gate 1 rules
  `CLIMATE_VARS` into the same registry.

**Forbidden**
- `config/defaults/**`, `config/catalogs/**` (`K1`, an AGENTS.md hard
  constraint — if you find yourself editing these, stop)
- `test_case/*.yml`, `config/templates/**` — P4 migrates those WITH the
  rewriter, and its falsifier is *"any difference is a hand-edit"*
- `scripts/**`

**Scope counts, measured 2026-08-26 at `31e9493b`, and STALE the moment P1c
starts.** Re-measure. The command:

```bash
grep -rnE '\b(min_reference|min_denominator|relative_change|max_flagged_months|CLIMATE_VARS|DEFAULT_MIN_REFERENCE)\b' \
  --include='*.py' --include='*.smk' blueearth_cst/ ./*.smk
```

At the time of writing: `relative_change` 3 sites (`analyze_projections.smk:315`,
`RETIRED_KEYS`, `dry_month.py`'s error text), `min_reference` 4, `CLIMATE_VARS`
8, all in `climate_figures.py`. These are SMALL numbers and that is the point —
the work here is design, not sites. P1b's own brief understated `C-57` as *"one
read site: `analyze_projections.smk:139`"*, which was true of the read and false
about the work behind it. Do not let a small count read as a small task.

### Required changes (checklist)

0. **Gate 1 first.** Items 1–6 all assume its answers.
1. **The registry.** One entry per known variable, carrying at minimum what
   `VariableSpec` requires (`source`, `canonical` ∈ `{rate, state}`, `units`,
   `change` ∈ `{relative, absolute}`) plus `min_reference` (`C-64`).
2. **`C-57`: the short form.** `variables: {precip:, temp:}` — a bare key, null
   value — resolves every field from the registry. The LONG form must keep
   working: no `RETIRED_KEYS` row covers `variables`, P1b's fixture uses it, and
   a variable outside the registry has nowhere else to be declared.
3. **A variable named in `variables:` but absent from the registry** must refuse
   at parse time naming the variable and both remedies (add it to the registry,
   or declare it long-form). Match `variable_spec.parse`'s existing house style:
   refuse and name the key, never guess.
4. **`C-64`: `min_reference` moves** out of `DEFAULT_MIN_REFERENCE` into the
   registry, per variable. `resolve_thresholds` reads it from there.
5. **`C-65`: `max_flagged_months`** → `advanced_settings.constraints`, beside
   `min_historical_years`. It is a `constraints:` entry, not `defaults:`,
   because D-10.6 classes it a hard limit a project may not relax — so unlike
   `C-54` there is no overriding key to name in its comment (D-10.7).
6. **`C-66`: `relative_change:` dissolves.** Only after 4 and 5, and only once
   a `change: relative` variable outside the shipped defaults is configurable
   again. `analyze_projections.smk:315–320` is the read to remove.

**Settle the `min_denominator` / `min_reference` naming, and say which won.**
The design (D-7.5, D-10.6) and the `RETIRED_KEYS` refusal both say
`min_denominator`; the code has always read `min_reference`
(`analyze_projections.smk:317`, `dry_month.py`). One of the two is wrong, this
is the phase that owns both surfaces, and P1b deliberately did not pick. A user
following the refusal message today is told to set a key nothing reads.

### Commit plan

`C-65` carries a correctness property that the others do not: the closed schema
means the YAML and `_ADVANCED_SETTINGS_SCHEMA` must land together or
`load_advanced_settings` refuses on the next run.

| subject | paths | invariant it preserves |
|---|---|---|
| the registry + `C-57` short form | registry file, `variable_spec.py`, fixture, tests | long form still parses; short form resolves |
| `C-64` — `min_reference` into the registry | `dry_month.py`, registry, tests | every previously-configurable threshold is still configurable |
| `C-65` — `max_flagged_months` | `advanced_settings.yml` **and** `_ADVANCED_SETTINGS_SCHEMA`, same commit | the two never disagree |
| `C-66` — dissolve `relative_change:` | `analyze_projections.smk`, tests | lands LAST; before it, the replacement must exist |

### Validation

- **Rung 1, per edit:** only the tests covering the module you changed —
  `tests/test_variable_spec.py`, `tests/test_dry_month.py`,
  `tests/test_advanced_settings.py` as applicable.
- **Rung 2, new behaviour:** the short form and its refusal, both as tests.
- **Rung 3, per commit:** `pytest tests/test_cli.py`, `pixi run lint`,
  `pixi run format-check`.
- **Rung 4, per phase:** `pixi run test-fast`, reconciled against
  `tests/data/r14_expected_red.txt`. **73 entries at `31e9493b`, all P4-owed.**
  P1b shrank it 83 → 73 and the gate fails on a STALE entry by design, so if
  your work turns any of them green, remove them in the same commit.
- **Rung 5, once at phase end:** `pixi run test-full` — `variable_spec.py` and
  `dry_month.py` are read by rule 2.06 and `snake_utils.py` is in `shared/`.
- Do NOT run `check_baseline.py` or a real workflow. Gate 5 costs, batched by
  the master brief deliberately.
- Redirect every gate to a FILE and read the tail; never pipe through `tail`.

**Falsifiers.** Each names the observation that would disprove the claim:

1. **"the short form resolves from the registry"** — a fixture using
   `precip:` (bare) and one using the long form with the same values must
   produce an EQUAL `VariableSpec` map. Assert the parsed structure, not that
   parsing succeeded; a short form silently resolving to a default would pass
   any smoke test.
2. **"no capability was lost"** — this is the phase's central risk and the one
   nothing else catches. Declare a `change: relative` variable that is NOT
   `precip` (so no shipped default applies), give it a threshold through the
   NEW surface, and dry-run WF2. It must build a DAG. Before this phase that
   configuration is impossible to express; if it is still impossible after,
   `C-66` has removed a capability rather than moved it.
3. **"`max_flagged_months` is still reachable"** — set it in
   `advanced_settings.constraints` to a non-default value and observe it reach
   rule 2.06's `max_flagged_months` param (`analyze_projections.smk:1145`).
   A regrouped key that no longer arrives is silent: the default is a plausible
   number and nothing raises.
4. **"the two halves of `C-65` agree"** — `load_advanced_settings` on the
   shipped file must not raise. The closed schema is the falsifier; it fires
   only if both halves landed.

### Acceptance criteria

- All four entry points still dry-run clean against `tests/data/v2/` — P1b's
  deliverable, which this phase must not regress.
- A relative variable outside the shipped defaults is configurable end to end.
- `advanced_settings.yml` and `_ADVANCED_SETTINGS_SCHEMA` agree, in one commit.
- `relative_change:` has no reader left, and its `RETIRED_KEYS` refusal names a
  destination that exists.
- `tests/data/r14_expected_red.txt` is reduced to only what P4 still owes.

**Rollback:** if Gate 1 cannot settle the registry's home, land items 1–5 and
STOP before `C-66`. Every row except `C-66` is independently useful, and a
half-dissolved `relative_change:` is the one state worse than not starting.

### Output requirements

State which rung caught what. **A rung that failed red and was fixed is the
informative record**; a log of terminal passes says nothing about which gate
earned its cost. If every gate is green first time, say so plainly rather than
presenting it as evidence of correctness.

**Results delta.** `C-64` and `C-65` are value-preserving on every shipped
config and a changed number is a defect, not a row landing — unlike P1b's
`C-69`. Report any moved indicator value with its cause.

### Task constraints

1. `get_config` contract preserved (`K5`): raise on missing required, return
   the default for optional.
2. `workflow.configfiles[0]` still forwarded as `config_path` (`K6`).
3. Do not touch `config/defaults/**` for any reason (`K1`).
4. `K3`: commit on the branch and stop. Nothing merges to `main` until the
   whole R14 bundle is green together.
5. The scope rule P1b settled and this phase inherits: rename config key READS
   and the strings that name a key back to the user; leave locals, derived
   paths, `params:` names and rule input names alone. The precedent is
   `build_model.smk:106`, where P1 reads `climate.window` into a local still
   called `historical_window`. The phase-end sweep is a grep for the QUOTED
   key, never the bare token.

### Human gates

1. **Gate 1 — BEFORE any implementation, and it releases the phase.** Three
   decisions the design does not make, and item 0 blocks on all three:
   a. **Where the registry lives** — a Python module beside `variable_spec.py`,
      or a YAML file under `config/`. `C-49` wants `CLIMATE_VARS` out of
      Python, which argues for YAML; `K1` puts `config/defaults/**` out of
      reach, which constrains where such a file could go.
   b. **Whether it is ONE registry or two.** `CLIMATE_VARS` (WF0 figures:
      `label`/`unit`/`how`/`style`) and the projections spec
      (`source`/`canonical`/`units`/`change`/`min_reference`) describe the same
      three variables with two vocabularies that overlap on `unit`/`units`.
      Unifying pulls `C-49` into this phase; not unifying leaves two records of
      one entity, which is the coupling S5 exists to prevent.
   c. **`min_denominator` or `min_reference`** — the design says one, the code
      the other, and both surfaces are in this phase's scope.
2. **Gate 2 — before `C-66`.** Demonstrate falsifier 2 (a non-`precip`
   relative variable configured through the new surface, WF2 dry-running
   clean) BEFORE removing the `relative_change:` reader. This gate exists
   because the removal is irreversible in the sense that matters: once the key
   is gone, the capability is only as good as what replaced it.

---

*Added 2026-08-26 by owner ruling on P1b's finding that `C-57`, `C-64` and
`C-66` share one absent dependency. P1b landed at `31e9493b`; the measurement
that prompted this phase is board item `t2608251900`, which closes when P1c
lands and not before.*
