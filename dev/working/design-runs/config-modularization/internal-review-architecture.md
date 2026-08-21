verdict: revise
doc_version: design-v1.md
findings:
  - id: arch-1
    severity: major
    section: "8.2 D-8.2 — Where composition happens"
    finding: >-
      §8.2's call signature and §8.3's derivation rule contradict each other, and
      the Snakefile ordering §8.2 asserts cannot hold as written. §8.2 shows
      `compose_config(config, config_path, entry="build_model")` — three arguments,
      none of which carries a projection — while §8.3 says `R(W)` is computed "from
      the same `CONFIG_PROJECTION` / `guarded_sections` declarations the Snakefile
      already maintains — passed in, not duplicated". There is no channel to pass
      them. Worse, §8.2 requires composition to run "before any other module-level
      code", but `run_stress_test.smk:41` reads `config["workflows"]["run_stress_test"]`
      while `guarded_sections` is not constructed until `:332` and `CONFIG_PROJECTION`
      until `:355-366` — roughly 300 lines below the point where composition must
      already have happened.
    rationale: >-
      `R(entry)` is what decides which T2 files must exist for a run to parse at all,
      so an implementer facing this gap must invent the mechanism: either restate the
      workflow list inside the loader — which §8.3 forbids by name as the drift failure
      mode `run_stress_test.smk:355-361` exists to prevent — or restructure the four
      Snakefiles in a way the design does not specify and does not budget in §15.5.
    suggested_fix: >-
      Give `compose_config` an explicit `declared_sections` parameter, and state in
      D-8.2 that `guarded_sections` / `CONFIG_PROJECTION` are hoisted above the compose
      call. Both are config-independent literals, so the hoist is mechanical; say so,
      and show the real call in the §8.2 snippet.
  - id: arch-2
    severity: major
    section: "12. Downstream consumers"
    finding: >-
      The consumer inventory is incomplete. Two documented, user-runnable commands
      index `config["workflows"][<name>]` from a config file they load themselves and
      are not mentioned anywhere in the design: `scripts/plot_workflow_dag.py:116`
      reads `workflows.run_stress_test.experiment_name`, and
      `dev/scripts/prune_series_cache.py:56` reads
      `workflows.analyze_projections.{clim_project,models,scenarios,members}`.
      Both are named in AGENTS.md's Key Commands and both take a `--config`/`--configfile`
      that is T1 after the split.
    rationale: >-
      `plot_workflow_dag.py` degrades SILENTLY: `experiment` resolves to `None`, the
      `if experiment:` branch is skipped, and every WF3 DAG render loses the experiment
      id from its filename — the exact scheme its own docstring (`:101-112`) and AGENTS.md
      both promise. `prune_series_cache.py` raises `KeyError: 'clim_project'` at
      `expected_keys`, breaking a `--delete`-capable maintenance tool. Neither failure
      is covered by any gate in §16, whose grep sweep names docs, tests and
      `snake_config_*.yml` references but not `["workflows"]` indexing under `scripts/`
      and `dev/scripts/`.
    suggested_fix: >-
      Add both to §12 with a stated decision (compose in the tool, or read the T2 path
      and load it), add `dev/scripts/prune_climate_store.py` as a verified no-op — it
      reads only `shared` and `project` (`:62-64,:99`) — and extend §16's sweep to
      `["workflows"]` indexing outside the Snakefiles.
  - id: arch-3
    severity: major
    section: "12.2 `scripts/suggest_experiment_name.py` (E4) — edits the WF3 T2 file"
    finding: >-
      §12.2 specifies two of the command's three config reads. It covers `_plan_edit`'s
      splice and the verification reload, but not the already-set refusal at
      `suggest_experiment_name.py:283-294`, which reads
      `doc["workflows"]["run_stress_test"]["experiment_name"]` from the T1 document
      loaded at the top of `main`.
    rationale: >-
      After the split that path is a closed two-key stanza, so `existing` is always
      `None`, the refusal never fires, and the command will happily allocate and splice
      a second `experiment_name` over one a user has already pinned in the T2 file —
      minting an orphan `experiments/<id>/` and silently redirecting the experiment.
      This is a wrong-behavior path in the one command whose entire contract is
      "refusing to overwrite".
    suggested_fix: >-
      Name all three reads in §12.2 and state that the refusal read moves to the T2
      document's top-level key, resolved before the name is allocated (the existing
      nothing-is-reserved ordering at `:296-300`).
  - id: arch-4
    severity: major
    section: "10.5 D-10.5 — `file_sha256(config_path)`: the one mechanism whose meaning changes"
    finding: >-
      `configuration_inputs_sha256` is computed on TWO independent code paths, and
      D-10.5 extends only one. Each Snakefile builds its own `CONFIG_REFERENCES` and
      computes `CONFIGURATION_INPUTS_DIGEST` at parse time
      (`build_model.smk:181-203`, `run_stress_test.smk:368-383`, and the wf0/wf2
      equivalents); `copy_config_files.py:457` independently recomputes the digest from
      the `referenced_inputs` it builds inside `__main__`. D-10.5 registers T2 files
      only in `other_config_files` / `reference_roles`.
    rationale: >-
      The two are equal today by parallel construction — `_reference_identity`
      (`provenance.py:563-596`) reduces both entry shapes to `sha256:<hash>` — and the
      Snakefile-side value is what every journal line carries
      (`run_stress_test.smk:1329`, and the three siblings). Register T2 bytes on one
      side only and `run_record.yml`'s `configuration_inputs_sha256` stops matching
      `journal.jsonl`'s for the same run, in the very digest §10.5 points readers at
      ("the digest `_RUNS_README` already tells readers to compare runs with"). It also
      leaves the parse-time params trigger blind to a T2 edit, which is the same class
      of gap D-10.3 invokes F7 against.
    suggested_fix: >-
      State that each Snakefile's `CONFIG_REFERENCES` gains
      `("workflow_config_<name>", path)` for every entry in `WORKFLOW_CONFIG_PATHS`,
      alongside the `copy_config_files` registration, and derive both from the same dict.
  - id: arch-5
    severity: major
    section: "9. Shared-seam enforcement (S4) — D-9.1"
    finding: >-
      The scope of the closed-stanza check is never fixed. §7.1 states the closure as a
      property of "each `workflows.<name>` block"; §8.4's error table phrases it as "any
      key of `workflows.<name>`"; §8.3 says workflows outside `R(entry)` are "not loaded
      at all" but their stanza "must still be present and well-formed", without saying
      what well-formed means or who checks it. Nothing in the four Snakefiles reads
      `enabled` today — the only validator is `run_workflows.py:282-314`, which a direct
      `snakemake -s` invocation never runs.
    rationale: >-
      The two readings give opposite outcomes for a half-migrated config. If closure is
      checked only for `R(entry)`, a project that split `build_model` and left the other
      three inline runs WF1 clean — which is precisely the "half-split configs become
      legal" defect §15.1 uses to reject the dual-mode loader, arriving through this
      design's own door. If closure is checked for all four, then
      `tests/test_cli.py:110-131` changes meaning: it currently asserts that a WF1
      dry-run succeeds with `workflows.analyze_climate` popped entirely, and pins job
      counts across the pair. The design must say which, because an existing test's
      expectation turns on it.
    suggested_fix: >-
      Rule explicitly: validate the closed stanza for all four workflows, require
      `config_path` only for `R(entry)`, and record the consequence for
      `tests/test_cli.py:110-131` in §16.
  - id: arch-6
    severity: major
    section: "10.4 D-10.4 — `reporting:` lives in the WF3 T2 file, hoisted"
    finding: >-
      T1's TOP level is never closed — only its `workflows.<name>` stanzas are — so a
      config that keeps `reporting:` at T1 top level while correctly splitting its
      workflow sections passes every check in §9 and §8.4. The design does not say what
      the loader does when the hoist target `config["reporting"]` is already occupied by
      a T1 key: overwrite, merge, or refuse.
    rationale: >-
      This also falsifies D-15.2's completeness claim. §15.2 asserts the closed stanza
      IS the migration detector — "No separate detector, no version key" — but a config
      whose only unmigrated element is a top-level `reporting:` produces no extra key
      under any `workflows.<name>`, so nothing fires and the project runs with an
      undefined precedence between two records of the same section.
    suggested_fix: >-
      Either close T1's top level to `{project, shared, workflows}` (which makes the
      detector genuinely complete and D-9.2's `"project"/"shared"/"workflows"` rejection
      set symmetric), or state the hoist-collision behavior explicitly as a refusal.
  - id: arch-7
    severity: major
    section: "10.3 D-10.3 — T2 files become declared rule inputs"
    finding: >-
      The stated rationale is wrong for one of the two rules it rests on. §10.3 argues
      that `prepare_spatial_maps` (1.06) and `prepare_stress_test_grid` (3.09) "have no
      such params, which is why the input declaration is the mechanism rather than a
      belt-and-braces addition". But rule 3.09 declares `config = ancient(config_path)`
      (`run_stress_test.smk:836`) and has NO `params:` block at all
      (`run_stress_test.smk:833-855`). An `ancient()` input is by construction not a
      rerun trigger — that is the whole meaning of the flag — so
      `config_workflows = ancient(WF_CONFIG_PATHS)` buys an existence edge and nothing
      else. The F7 analogy at `run_stress_test.smk:862-872` does not transfer: F7 was a
      plain params-only read promoted to a plain declared input.
    rationale: >-
      As written, the design claims a protection at 3.09 that its own mechanism cannot
      provide, which will read to an implementer as "3.09 is covered" when it is not.
      What actually re-fires 3.09 on a stress-test edit is (a) the experiment freeze
      forcing a new experiment name and therefore a new `exp_dir`, and (b) — newly, and
      only because of D-10.6 — `stress_test_cfg` arriving as a param. The design frames
      D-10.6 as removing a disk read; it is also the thing that makes 3.09's rerun
      trigger real, and that should be stated where the guarantee is claimed.
    suggested_fix: >-
      Correct the §10.3 note: 1.06's plain input is a trigger, 3.09's `ancient()` input
      is an existence edge, and 3.09's actual trigger arrives via D-10.6's params. Keep
      the declaration for both — just stop attributing the wrong property to it.
  - id: arch-8
    severity: major
    section: "8.3 D-8.3 — Which T2 files are required"
    finding: >-
      `R(wf3)` makes the `analyze_projections` T2 FILE a hard requirement of every WF3
      run — a `ValueError` at parse under §8.4, and, once D-10.3 lands, an
      `ancient()`-flagged rule input of 3.09 and a plain input of 3.02, i.e. a
      `MissingInputException` surface too. That collides with a standing invariant the
      design cites but never reconciles: `run_stress_test.smk:385-392` and
      `check_project_consistency.py:39-42,:174-182` both record that the wf2 artifact is
      deliberately a params path rather than a mandatory input "because the projections
      overlay is optional per the CST method and must not be force-required", with an
      absent wf2 snapshot logged unchecked and PASSING.
    rationale: >-
      Today the WF2 obligation is "keep a stanza in a file you already have". After the
      split it becomes "author and keep a separate file on disk for a workflow you never
      run". That is a real tightening of an explicitly protected optionality, and it
      directly contradicts §8.3's own headline benefit and §18's "a project that never
      runs WF0 needs no WF0 file at all" — which is true for WF0 and false for WF2.
      §15.4 step 3 states the requirement but does not flag it as the invariant change
      it is.
    suggested_fix: >-
      Either admit an absent-but-declared T2 file as `{}` for a workflow in `R(entry)`
      that is not the entry itself — matching the empty-file rule already in §8.4 and
      the guard's absent-snapshot tolerance — or state plainly in §18 that the overlay's
      config file becomes mandatory even when the overlay is not run, and why that is
      acceptable.
  - id: arch-9
    severity: major
    section: "7.4 D-7.4 — Filenames, derived mechanically from the workflow key"
    finding: >-
      The table recommends `<project>/config/<name>.yml` as a real project's T2 location.
      Read as `<project_dir>/config/` — the natural reading in this repo, where
      `project_dir` IS the project — that puts a hand-authored SOURCE file inside the bin
      `copy_config_files.py:60-93` documents as "Everything here is written by the run.
      Editing any of it changes nothing", and inside the tree
      `dev/scripts/semantic_tree_diff.py:338-390` enumerates leaf by leaf. It also
      contradicts §15.3, whose migration script defaults to `<t1_dir>/<t1_stem>_<name>.yml`
      — beside T1, not under `project_dir`.
    rationale: >-
      A T2 file under `<project_dir>/config/` is an undeclared path, so
      `pixi run tree-check` fails — while §16 predicts that gate "unchanged" and reads
      any new file under `project_dir` as evidence that D-11.2 leaked a copy. The design
      would then have manufactured its own false positive on the gate it nominated to
      detect a leak.
    suggested_fix: >-
      Recommend the same location the migration script produces (beside T1), and state
      explicitly that a T2 file must NOT live under `project_dir`, for the same
      source-versus-record reason §11.1 gives for comment loss.
  - id: arch-10
    severity: major
    section: "11.2 D-11.2 — T2 files are recorded, not copied"
    finding: >-
      "The registration reuses `other_config_files` / `reference_roles` unchanged; only
      the destination is `None`" is not implementable against the code it targets.
      `_snapshot_references` (`copy_config_files.py:258-306ff`) sorts on
      `(str(dest_dir), str(config_file))` and then builds `Path(dest_dir)` unconditionally
      in the copy branch — a `None` destination is a `TypeError`, not a record-only mode.
      A new branch is required, and with it a decision the design does not make: what
      `recoverable` is for an untracked, project-authored T2 file.
    rationale: >-
      For a tracked file `_tracked_blob` already yields record-only behavior, so the new
      path exists solely for the untracked project case — where the honest answer is
      `recoverable: false, archived_path: null, sha256: <hash>`. That triple is a FOURTH
      entry shape, and it is indistinguishable from the existing pathless-identifier
      shape (`:277-287`) except by whether `sha256` is null. Any reader that treats
      `recoverable=false and archived_path=null` as "logical identifier, nothing on disk"
      — which is what that combination means today — will misread it.
    suggested_fix: >-
      Specify the record-only branch explicitly (a role set, or a sentinel destination),
      and state the entry shape including `recoverable`, with one sentence on how it is
      distinguished from a pathless identifier.
  - id: arch-11
    severity: major
    section: "13. Advanced settings — interior organization (S3)"
    finding: >-
      D-13.1 moves `batch_disk_headroom_fraction` from `defaults:` to
      `defaults.run_stress_test:`. `effective_config_document`
      (`provenance.py:220-262`) folds the whole `advanced_settings` mapping into the
      digested document UNPROJECTED, so that move changes `effective_config_digest` for
      all four entry points — including the seeds §16's digest-equality property test
      compares.
    rationale: >-
      §10.2 asserts both digests are "unchanged *by construction*, not by inspection",
      and §16 nominates a permanent property test that pre-split and post-split digests
      are equal. Both statements are true of the composition change and false of the
      milestone as scoped, because commit 6 of §15.5 moves the key. The test as worded
      would fail unless it pins `ADVANCED_SETTINGS` identically on both sides — a
      qualification the design never states. §13.3's own standard ("it would change what
      an explicit `null` does ... under a refactor that claims output neutrality") is the
      reason to apply the same scrutiny here.
    suggested_fix: >-
      Say that the digest-equality test holds `advanced_settings` fixed, and either move
      D-13.1 out of this milestone or record the digest shift as a named, accepted
      consequence beside the three snapshot targets in §16.
  - id: arch-12
    severity: major
    section: "8.2 D-8.2 — Where composition happens"
    finding: >-
      The design never states that composition must REBIND the Snakefile's module-level
      `config` name, as opposed to binding the composed mapping to any other name. It
      matters because `check_project_consistency.py:225` takes its live config from
      `sm.config`, not from the Snakefile's local — and `sm.config` resolves through
      `workflow.config` → `self.globals["config"]`
      (`snakemake/workflow.py:1728-1729`), which is the same dict the Snakefile's
      globals are exec'd into (`workflow.py:1612`). The §8.2 snippet happens to rebind,
      so the mechanism works; nothing says it must.
    rationale: >-
      §10 claims to enumerate "the four things that are not in-memory reads" and treats
      everything else as safe by D-8.1. `sm.config` is a fifth access path with a
      different binding, and §7.1 Q1 already flags anxiety about the `config_path` name
      colliding — exactly the pressure that produces a `composed = compose_config(...)`
      refactor. If that happens, the drift guard compares `{enabled, config_path}`
      against the snapshot's full `workflows.build_model` and every WF3 run fails at
      rule 3.01, after WF1 and WF2 have already run, with a message that blames project
      drift rather than the binding.
    suggested_fix: >-
      Add one line to D-8.2: composition rebinds the Snakefile-global `config`, because
      `snakemake.config` in `script:` rules is that binding; name
      `check_project_consistency.py:225` as the consumer that depends on it.
  - id: arch-13
    severity: minor
    section: "13. Advanced settings — D-13.3"
    finding: >-
      D-13.3 states that "Both override mechanisms are preserved exactly, and neither is
      unified", and then the closing paragraph introduces a third: a workflow-scoped knob
      set as an optional key in that workflow's T2 file that "overrides the namespaced
      default". Nothing specifies which function reads it, its precedence against
      `shared:`, or what an explicit `null` does — the very question D-13.3's own table
      exists to answer for the other two.
    suggested_fix: >-
      Specify the third path with the same table row (call-site default vs resolver
      substitution, and the `null` behavior), or defer S5's `batch_size` example to the
      implementation brief and say so.
  - id: arch-14
    severity: minor
    section: "12.4 `simulation_window ⊂ historical_window` (E8) — now genuinely cross-file"
    finding: >-
      §12.4 asserts the function's "signature, body, error messages and
      passthrough-when-absent behavior are unchanged", then requires that "the messages
      gain the resolved file paths — one line each, no logic change".
      `resolve_simulation_window(shared_cfg, model_cfg)` (`snake_utils.py:1322`) receives
      two mappings and nothing else, so it cannot name a file without a signature change.
    suggested_fix: >-
      State the intended signature change (two optional source-path arguments, defaulting
      to `None` so the existing message shape survives when they are absent), and note the
      message-shape tests in `tests/` accordingly.
  - id: arch-15
    severity: minor
    section: "6.2 New premises verified for this design — N1"
    finding: >-
      N1 says `config_path` is a declared input "in five rules" and then lists six
      (`analyze_climate.smk:344`, `build_model.smk:467`, `build_model.smk:535`,
      `analyze_projections.smk:836`, `run_stress_test.smk:621`, `run_stress_test.smk:836`).
      §10.3 says six. The list itself is correct and complete — a grep of `config_path`
      across the four Snakefiles returns exactly those six `input:` sites plus one param
      (`run_stress_test.smk:888`), four `file_sha256` calls and three `run_header` uses.
    suggested_fix: Change "five" to "six".
  - id: arch-16
    severity: minor
    section: "10.4 D-10.4 — `reporting:` lives in the WF3 T2 file, hoisted"
    finding: >-
      `reporting:` appears in no shipped config: all four `test_case/snake_config_*.yml`
      have exactly `['project','shared','workflows']` at top level, and the template
      carries it only as a commented-out block
      (`config/templates/snake_config.template.yml:210`). So §15.3's round-trip
      acceptance gate — "for each shipped seed and for the template" — cannot exercise
      the splitter's reporting-move branch, and a text splitter faces a commented `#reporting:`
      block that it will leave in T1 as documentation for a key that now belongs elsewhere.
      §16's new unit test does cover the loader-side hoist.
    suggested_fix: >-
      Add a synthetic fixture carrying `reporting:` to the round-trip gate, and say what
      the splitter does with the commented template block.
  - id: arch-17
    severity: minor
    section: "10.1 D-10.1 — What the merged workflow section contains"
    finding: >-
      "byte-identical for an unchanged experiment" is stronger than the mechanism
      supports. `write_experiment_config.py:154` dumps with `sort_keys=False`, so
      `experiment.yml`'s bytes follow insertion order, and D-10.1 fixes `enabled` first
      by construction. It happens to be first in all four seeds and the template, so the
      claim holds there; a project config that places `enabled` elsewhere in the block
      yields different bytes after migration.
    rationale: >-
      Harmless in effect — `check_not_frozen` compares parsed mappings and
      `_frozen_differences` is key-based, and `experiment.yml` is a rule OUTPUT only
      (`run_stress_test.smk:556,:773`, never an input), so at worst rule 3.07 rewrites
      itself once. Worth correcting because §15.4 step 4 leans on "unaffected".
    suggested_fix: >-
      Restate as "value-identical, and byte-identical whenever `enabled` was the block's
      first key", with the `sort_keys=False` citation.
  - id: arch-18
    severity: minor
    section: "10.6 D-10.6 — Two disk re-reads must be redirected"
    finding: >-
      D-10.6 addresses `prepare_cst_parameters.py:250-251`'s `lookup_fn` fallback but not
      the branch that reaches it: `__main__`'s `prep_cst_parameters(config_fn=sys.argv[1])`
      (`:289`). If the function stops taking a config path and takes `stress_test_cfg`
      instead, that branch cannot be constructed at all.
    suggested_fix: >-
      Say whether the direct-invocation branch is retired, or kept via a dual signature
      that composes from a T1 path.
  - id: arch-19
    severity: major
    section: "16. Validation plan"
    finding: >-
      `tests/conftest.py:138-145` is an unlisted consumer, and it sits in the one test
      layer §16's gates cannot report on. The `model_build_config` fixture calls
      `get_config(config["workflows"]["build_model"], "model_build_config", optional=False)`
      against a raw `yaml.safe_load` of the seed config (`conftest.py:113-118`) with no
      composition anywhere in the fixture chain. After the split that section is
      `{enabled, config_path}`, so the fixture raises
      `ValueError: Argument model_build_config not found in config` at setup for every
      test that requests it.
    rationale: >-
      AGENTS.md names this fixture layer as the one that skips rather than fails outside
      the primary checkout — 15 of 31 skips measured 2026-08-07 — and records R9 leaving
      22 stale-path failures there that every branch-runnable gate missed. §16 nominates
      `test-fast` and `test-full`, both of which a session runs from a slot, and a
      stale-spelling sweep that says "docs and tests" without naming this layer. So the
      design's own gate table cannot see the consumer its central shape change breaks.
    suggested_fix: >-
      Add `tests/conftest.py` to §12 with a stated decision (compose in the fixture, or
      read the T2 path), and add a §16 row requiring the fixture layer to be exercised
      from the primary checkout — the same "run it where it can fail" posture the
      `check_baseline` row already takes.
  - id: arch-20
    severity: major
    section: "16. Validation plan"
    finding: >-
      `tests/test_snapshot_config_rules.py` asserts Snakefile SOURCE TEXT that both
      arch-1's fix and D-10.3 will move, and the design names neither the module nor the
      obligation. `:122-126` pins the exact literals
      `CONFIG_PROJECTION = ("project", "shared", "workflows.build_model")` and the wf2
      equivalent; `:129-141` pins that `run_stress_test.smk` contains
      `CONFIG_PROJECTION = tuple(sorted(` and `for section in guarded_sections`;
      `:178-193` pins the `snapshot_config` rule block's params contents via `_rule_block`.
    rationale: >-
      Hoisting `guarded_sections` / `CONFIG_PROJECTION` above the compose call (arch-1)
      and adding `config_workflows` to five `snapshot_config` blocks (D-10.3) both land
      inside what these tests read. They are cheap to keep green, but they are a
      source-text contract nobody budgeted: §15.5's commit 3 bundles the loader wiring
      and the rule-input additions into "one commit" without listing the test module that
      commit necessarily edits.
    suggested_fix: >-
      Name `tests/test_snapshot_config_rules.py` in §15.5 commit 3 and in §16's sweep row,
      and state that the derivation assertion at `:129-141` must survive the hoist.
  - id: arch-21
    severity: major
    section: "16. Validation plan"
    finding: >-
      §16 treats `semantic_tree_diff.py` as shape-only — "plus `semantic_tree_diff.py` if
      the tree shape moved" — and D-11.1 correctly observes that no path moves. But
      `compare_copied_config` (`dev/scripts/semantic_tree_diff.py:887-906`) adjudicates
      CONTENT: it parses both snapshots, applies the directional path map to the reference
      side, and requires deep structural equality, with its own docstring stating that
      "an unmapped path, a changed non-path value, a missing/extra key -- FAILs".
    rationale: >-
      D-11.1 removes three of four `workflows.*` sections from each composed snapshot, so
      a pre-change reference tree compared against a post-change live tree produces
      missing-key diffs on all three config snapshots — a FAIL with no expected-result
      line anywhere in §16. The design is admirably precise that `check_baseline` must
      show "exactly three targets differ"; the sibling gate gets no prediction at all, so
      an operator at the milestone seal has to decide ad hoc whether to believe it — the
      "gate result you have to decide whether to believe" failure AGENTS.md names twice.
    suggested_fix: >-
      Give `semantic_tree_diff` a §16 row with the same falsifiable shape: the three
      copied-config comparisons are expected to FAIL on removed `workflows.*` keys and on
      nothing else, and every other file must compare clean.

---

## Appendix — evidence, and what checked out

Reviewed against the worktree `C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2`
on 2026-08-20. Everything below was read or executed; nothing is carried from the
intake unverified.

### Decision-ID cross-reference trace

Every cross-reference in D-7.1 … D-15.3 resolves to an existing target, and the
composition is coherent except at the four seams the findings name:
D-8.2 ↔ D-8.3 (arch-1), D-9.1 ↔ §8.3's "well-formed" (arch-5), D-10.4 ↔ T1's open
top level (arch-6), D-10.2/§16 ↔ D-13.1 (arch-11). The spine — D-8.1 → D-10.1 →
D-10.2 → D-11.1 — holds: I could not construct a case where a merged-dict reader
sees a different value than it sees today.

### Premises that verified clean

- **N1's six input sites.** `grep -n config_path` over the four Snakefiles returns
  exactly six `input:` sites (`analyze_climate.smk:344`, `build_model.smk:467`,
  `build_model.smk:535`, `analyze_projections.smk:836`, `run_stress_test.smk:621`,
  `run_stress_test.smk:836`), one param (`run_stress_test.smk:888`), four
  `file_sha256` calls and three `run_header` uses. The declaration list in §10.3 is
  complete. Only the word "five" in N1 is wrong (arch-15).
- **`ancient()` on a list is legal.** `snakemake/io/__init__.py:972-982` —
  `flag()` recurses over any non-`not_iterable` value, so
  `ancient(WF_CONFIG_PATHS)` yields a list of flagged `AnnotatedString`s. D-10.3
  is implementable as written.
- **N5 and §16's enumeration.** `dev/baseline/manifest.json` holds exactly 7
  targets: 3 `type: yaml` config snapshots, 2 `type: csv` CMIP6 change-factor
  tables, 1 `type: indicator`, 1 `type: discharge`. `run_metadata.json` is indeed
  absent. The "exactly three targets move" prediction stands on the manifest as
  recorded — subject to arch-11, which moves no target but does move the digest the
  §16 property test compares.
- **D-7.4's tracking claim, re-demonstrated.**
  `git check-ignore -q test_case/snake_config_rapid_build_model.yml` → exit 1 (not
  ignored), same as `test_case/snake_config_rapid.yml`; `test_case/my_seed.yml` →
  exit 0; `test_case/workflows/build_model.yml` → exit 0. Both halves of §7.4,
  including the rejection of a `test_case/workflows/` subdirectory, are correct.
- **D-10.1's freeze reasoning.** `write_experiment_config.py:63-110` is a key-union
  diff over `set(was) | set(now)`, with an unregistered absent key counting as
  changed. Dropping `enabled` or adding `config_path` would refuse every already-run
  experiment, exactly as stated. `experiment_cfg = my_cfg` at
  `run_stress_test.smk:771` confirms the recorded section is the merged one.
- **D-11.1's guard consequence.** `check_project_consistency.py:180-181` sets
  `_WF1_GUARDED = ("project", ("shared","basin"), ("workflows","build_model"))` and
  `_WF2_GUARDED = (("workflows","analyze_projections"),)`; the composed snapshot of
  each entry point carries its own `R(entry)`, so every guarded path is found in the
  snapshot of the workflow that owns it. N6 is accurate.
- **The first post-migration WF3 run with an armed freeze** is safe for a reason the
  design under-sells: a pre-migration wf1 snapshot is the whole config, hence a
  strict superset of what the guard reads, so it passes before WF1 is ever re-run;
  and once WF1 does re-run, the composed snapshot still carries `project`,
  `shared` and `workflows.build_model`. §15.4 step 5's claim holds.
- **§12.1 on the wrapper.** `_enabled_flags` (`run_workflows.py:282-314`) needs each
  of `WORKFLOW_ORDER`'s four names to map to a `dict` carrying a bool `enabled`;
  `{enabled, config_path}` satisfies both. No `.smk` file reads `enabled` at all —
  `grep -n enabled *.smk` returns nothing — so the wrapper is genuinely the only
  validator, which strengthens §12.1's argument and is also why arch-5 matters.

### The two disk re-reads (D-10.6)

Both confirmed verbatim: `prepare_weagen_config.py:89-90`
(`read_yml(snake_config_path)` → `yml_snake["workflows"]["run_stress_test"]`, used at
`:101` for `realizations_num` and `:126-131` for the two transient flags) and
`prepare_cst_parameters.py:162-165` (`open(config_fn)` →
`yml["workflows"]["run_stress_test"]["stress_test"]`). The params redirect is the
right call and, per arch-7, does more than the design claims: it converts rule 3.09
from a rule with no rerun trigger at all into one whose stress-test settings are a
params trigger. Worth stating as a benefit rather than leaving it implicit.

### On the naming section (§14)

No defect found in the recommendation's reasoning. Row 15 of §14.4 — a rename moves
a dozen manifest target KEYS and so destroys §16's falsifier — is correct against
`dev/baseline/manifest.json`, whose keys are literal project-relative paths
including `config/runs/snake_config_build_model.yml`. The independence claim in
§14.3 ("nothing else in §§7–13 depends on the names") also holds: the loader takes
`R(entry)` from Snakefile declarations and `SHARED_SEAM_KEYS` names `shared:` keys.
The one qualification is arch-1 — until the derivation channel is specified, the
claim that the loader never hard-codes a workflow list is an intention rather than a
mechanism.

### What I could not check

- Whether `run_record.yml`'s and `journal.jsonl`'s `configuration_inputs_sha256`
  are equal today for a real run (arch-4 argues they must be, from
  `_reference_identity`'s uniform `sha256:` reduction, but I did not execute a run to
  confirm). If they already differ, arch-4's severity drops to minor and the finding
  becomes "say which of the two paths is authoritative".
- The CST-API backend's config construction, which §15.1 names as part of the
  broken population. Out of this repo, correctly.
