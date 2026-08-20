verdict: revise
doc_version: design-v1.md
findings:
  - id: repofit-1
    severity: blocking
    section: "15.5 Commit sequencing"
    finding: >-
      The clean break (D-15.1) bricks the gate the design leans on hardest.
      `tests/snake_config_fixture.yml` is a tracked, inline-shaped config
      (`workflows.build_model.model_build_config` at
      tests/snake_config_fixture.yml:34-36) that `tests/test_cli.py:18` loads as
      `config_fn` — and §16 names `pytest tests/test_cli.py` as THE gate for
      every composition error, every seam refusal, and the whole §8.3
      required/optional matrix. Under D-15.1 that fixture fails at parse time on
      its first extra key, so the gate cannot run until the fixture is split, and
      §15.5 never names it. 23 test modules reference the fixture
      (`snake_config_fixture` / `config_fn` / `CONFIG_FN` / `CONFIG =`), and the
      cost is not only the file count: the load-bearing idiom in the suite is
      `safe_load(fixture)` → mutate `cfg["workflows"][name][...]` → `safe_dump`
      to `tmp_path` → run Snakemake against it (`tests/test_cli.py:60-73`,
      repeated in `test_climate_store_contract.py`, `test_guard_invalidation.py`,
      `test_cross_workflow_inputs.py`, `test_climate_store_freshness.py`,
      `test_plot_climate_source.py`, `test_compare_climate_sources.py`). Every
      one of those becomes a two-file mutation that must also write T2 files into
      `tmp_path` and point `config_path` at them.
    rationale: >-
      The design's own primary gate is unrunnable at the commit where the loader
      is wired in (§15.5 step 3), and the migration effort estimate is missing
      its largest single item — a fixture rework across ~23 modules plus a
      conftest-level helper that does not exist today.
    suggested_fix: >-
      Add `tests/snake_config_fixture.yml` (and its T2 siblings) to §15.5 step 3
      explicitly, and add a §12 subsection for the test-fixture surface: either a
      conftest helper that composes a temp T1+T2 pair from one mutated mapping,
      or a `compose_config`-aware `write_config(tmp_path, cfg)` shared by every
      site that currently does `safe_dump(cfg)` into `tmp_path`. Name it in the
      §16 gate table as a prerequisite for `test_cli`.
  - id: repofit-2
    severity: blocking
    section: "15.3 D-15.3 — `scripts/split_project_config.py`, report-only by default"
    finding: >-
      §15.3 and §8.4 contradict each other for the case the migration exists to
      serve. §15.3 defaults the splitter's output to `<t1_dir>/<t1_stem>_<name>.yml`
      and justifies it as "the layout least likely to break a relative path" —
      a justification that is only true under T1-relative resolution, which §8.4
      explicitly rejects in favour of CWD-relative ("the repo root under `pixi
      run`"). AGENTS.md places a production `project_dir` — and with it the
      project's own config, since "every shipped `--configfile` target lives
      beside the project it writes into … which is how a real project is laid out
      too" — OUTSIDE the repository tree. So for a real project the splitter
      writes a T2 file beside T1 in a directory that is not under the CWD, and
      the design never states what `config_path` value it emits: an absolute path
      (correct but non-portable, and it would then differ from every worked
      example), or a relative path that resolves against the repo root and
      therefore does not exist.
    rationale: >-
      The primary migration path for existing out-of-tree projects is
      unimplementable as specified: the splitter cannot write a `config_path`
      that both resolves and matches the design's own examples. The defect is
      invisible in every worked example because `<t1_dir>` for all four shipped
      seeds is `test_case/`, which IS under the repo root, so §8.4 and §15.3
      coincide for the seeds and for `test_cli`.
    suggested_fix: >-
      Decide explicitly and state it in both §8.4 and §15.3: either (a) the
      splitter emits an absolute `config_path` for any T1 outside the CWD and a
      CWD-relative one otherwise, with a worked out-of-tree example; or (b)
      revisit §8.4 to resolve `config_path` against the T1 FILE (which N4's
      consistency argument does not actually cover, since no existing key
      references a sibling of the config file). Whichever is chosen, add an
      out-of-tree T1 case to `tests/test_config_composition.py`'s path-resolution
      matrix in §16.
  - id: repofit-3
    severity: blocking
    section: "7.4 D-7.4 — Filenames, derived mechanically from the workflow key"
    finding: >-
      The seed-T2 filename pattern satisfies the `.gitignore` tracking glob by
      landing inside the SAME glob shape a test already uses to discover shipped
      configs, and the two cannot both be satisfied.
      `tests/test_prepare_cst_parameters.py:364-378` parametrizes over
      `sorted(glob.glob(REPO_ROOT / "test_case" / "snake_config_*.yml"))` plus
      `config/templates/snake_config.template.yml`, then indexes
      `cfg["workflows"]["run_stress_test"]["stress_test"]`. After D-7.4 it breaks
      in three independent ways: (i) the glob picks up up to 16 new T2 files,
      none of which has a `workflows` key → `KeyError: 'workflows'`; (ii) the
      four T1 files no longer carry `stress_test` under
      `workflows.run_stress_test` → `KeyError`; (iii) the explicitly-passed
      template at :367 breaks the same way as (ii). I verified the glob
      collision directly: `git check-ignore -q
      test_case/snake_config_rapid_build_model.yml` exits 1 (tracked, as the
      design demonstrates) — and `glob("test_case/snake_config_*.yml")` matches
      the same name.
    rationale: >-
      A shipped-config guard (V23's "the refusal must not fire on anything we
      ship") goes red on both legs of CI, and the failure mode is a bare KeyError
      rather than a refusal, so it reads as a defect in the guard rather than in
      the config layout. The design cites E9's check-ignore demonstration as
      settling the filename question; it settles only half of it.
    suggested_fix: >-
      Name `tests/test_prepare_cst_parameters.py:364-378` in §16's stale-spelling
      sweep and in §15.5 step 3, and give it a discovery rule that distinguishes
      T1 from T2 — the cleanest is to keep discovery on `snake_config_*.yml` but
      select `_, _, stress = ...` from the composed document via
      `compose_config`, which is also a better test than reading raw YAML. While
      there, note in §7.4 that `test_case/snake_config_baseline_build_model.yml`
      (a seed T2 source) and `config/runs/snake_config_build_model.yml` (a
      composed project record) now differ by one path segment, so a bare
      `snake_config_build_model` grep conflates two file classes with opposite
      meanings.
  - id: repofit-4
    severity: major
    section: "12.2 `scripts/suggest_experiment_name.py` (E4) — edits the WF3 T2 file"
    finding: >-
      §12.2 says "the plan's depth handling changes". The actual behaviour is
      worse and silent. A T2 file has no `workflows:` key at all, so
      `_find(0, -1, "workflows")` (suggest_experiment_name.py:112) returns
      `None` and `_plan_edit` takes the append-whole-path-at-EOF branch
      (:113-128), writing `workflows:\n  run_stress_test:\n    experiment_name:
      <name>` into the T2 file. The verifier that is supposed to catch exactly
      this — `_write_experiment_name` at :214-218 — builds its expectation as
      `expected.setdefault("workflows", {}).setdefault("run_stress_test",
      {})["experiment_name"] = name`, so the bogus nested write reloads to
      exactly `expected` and PASSES. The command reports success while the
      composed config has no `experiment_name` and WF3 silently falls back to the
      dated default. Beyond the two consequences §12.2 lists, the rewrite also
      retires the second append branch (:132-141), the `_block_end` helper, the
      flow-style `ValueError` at :93-96, and the `after_comment` comment-run
      anchoring at :148-163 (which keys on a comment inside the
      `run_stress_test:` block). The error string at :222 ("Set
      workflows.run_stress_test.experiment_name: …") and the `config` argument
      help at :229 also name the nested path, and
      `tests/test_suggest_experiment_name.py` carries 8 `["workflows"]`
      references — none of them named in the design.
    rationale: >-
      An implementer who reads §12.2 as "adjust indentation" ships a command that
      silently writes the wrong shape and self-verifies green — the exact
      "nothing fails, so nobody looks" failure class AGENTS.md records for the
      vendored console marker and the unread CI run.
    suggested_fix: >-
      Restate §12.2 as "`_plan_edit` plans a TOP-LEVEL key; the parent-block
      creation branches and the flow-style guard are retired", state explicitly
      that the verifier's `setdefault` chain must be rewritten (not merely
      "checks the top-level key"), and add `tests/test_suggest_experiment_name.py`
      and the :222 error string to §15.5 step 5.
  - id: repofit-5
    severity: major
    section: "7.1 D-7.1 — T1, the project config"
    finding: >-
      The canonical T1 example points every `config_path` at
      `config/workflows/<name>.yml`. That path revives a bin AGENTS.md
      explicitly rules out ("There is **no `workflows/` bin**"), which was
      retired when the configs moved out of `config/workflows/` in R06 — a move
      `tests/test_gridded_outputs_removed.py:98-110` still carries a comment
      about ("the configs moved out of `config/workflows/` entirely and the old
      root stopped existing"). It is also inconsistent with the design's own
      §7.4 (shipped seed T2 → `test_case/snake_config_<variant>_<name>.yml`) and
      §15.3 (`<t1_dir>/<t1_stem>_<name>.yml`), and under §8.4's CWD-relative rule
      it names a path inside the TOOLBOX checkout, which is where AGENTS.md says
      project configuration must never live.
    rationale: >-
      §7.1 is the block an implementer and a user will copy. Following it creates
      a fifth `config/` bin that contradicts AGENTS.md, that the splitter does
      not produce, and that no other section of the design references.
    suggested_fix: >-
      Rewrite the §7.1 example to use the paths §7.4 and §15.3 actually specify —
      `config_path: test_case/snake_config_rapid_build_model.yml` for the seed
      shape, or `<project>/config/build_model.yml` if the example is meant to
      show a real project. Note also that `snake_utils.py:858-860`'s docstring
      already carries the stale `config/workflows/snake_config_*.yml` spelling;
      §16's grep sweep should catch it.
  - id: repofit-6
    severity: major
    section: "16. Validation plan"
    finding: >-
      Two shipped-config assertions in `tests/test_a1_acceptance.py` regex the
      RAW text of files whose content the split moves, and neither is named.
      `:119-130` reads `config/templates/snake_config.template.yml` and asserts
      `re.search(r"historical_year_range:\s*\[…\]", template)` matches;
      `:132-165` does the same against `test_case/snake_config_baseline.yml` and
      then asserts three properties of the parsed years.
      `historical_year_range` lives under `workflows.analyze_projections`, so
      after the split it is in the T2 files and BOTH regexes fail their
      `assert m, "…must declare historical_year_range"` guard. Both halves must
      be fixed together — fixing only the template leaves the seed red.
    rationale: >-
      Two more CI failures on both legs, in a module whose whole purpose is to
      pin an accepted design decision (OQ-4). A raw-text assertion against a
      shipped config is precisely the surface a file split moves, and the design
      lists no inventory of them. Major rather than blocking, unlike repofit-3:
      the fix is a mechanical redirect of two regexes to the T2 files, and no
      design-level choice has to be revisited — whereas repofit-3 is a conflict
      between two globs the design cannot satisfy at once.
    suggested_fix: >-
      Add to §16's sweep an explicit enumeration of tests that read a shipped
      config as TEXT or index `["workflows"]` out of one — at minimum
      `test_a1_acceptance.py:119-165`, `test_prepare_cst_parameters.py:364-378`,
      `test_gridded_outputs_removed.py:98-117` (survives, but its `>= 5` guard
      and its `roots` comment both need updating), and
      `test_snake_utils.py:2690-2745`. Prefer redirecting them at
      `compose_config` rather than at a second file path.
  - id: repofit-7
    severity: major
    section: "16. Validation plan"
    finding: >-
      §16 does not account for the fixture-dependent layer, which AGENTS.md names
      as "the one part of the suite that cannot fail in CI or in any worktree"
      and records as R9's 22 stale-path failures, three of them silent skips.
      D-11.1 changes the CONTENT SHAPE of `<project_dir>/config/runs/*.yml`, and
      that layer reads those files directly:
      `tests/test_interchange_contracts.py:912-916` opens
      `test_local/config/runs/snake_config_build_model.yml` and
      `:1002-1006` opens
      `test_local/experiments/experiment/config/snake_config_run_stress_test.yml`
      and indexes `snap["workflows"]["run_stress_test"]`. Both survive D-11.1 by
      construction, but neither can be EXERCISED until `test_case/test_local` has
      been re-run through WF1/WF2/WF3 to regenerate the composed snapshots — and
      in a session slot the tree is a `worktree_seed` copy, so those tests skip
      (`_fixture_present()`) rather than fail. §16's table gives no ordering
      constraint tying the fixture re-run to the gate, and none of its rows can
      detect a wrong composed-snapshot shape.
    rationale: >-
      A branch developed in a slot can pass `test-full` green while the composed
      snapshot is wrong, because the only tests that read a real snapshot skipped.
      This is the R9 precedent AGENTS.md warns about, arriving through a content
      change instead of a path change.
    suggested_fix: >-
      Add an explicit ordering row to §16: after §15.5 step 4 lands, re-run
      WF1→WF2→WF3 against `snake_config_baseline.yml` from the PRIMARY checkout
      (WF1 with `--notemp`), THEN run `test-full` there, THEN read
      `check_baseline.py check`, THEN re-record. State that a slot run of
      `test-full` is not evidence about the composed snapshot, and that the
      fixture-layer skip count must be read (`-rs`) rather than assumed.
  - id: repofit-8
    severity: minor
    section: "15. Migration plan"
    finding: >-
      `dev/reference/naming.md:205-266` requires an INTERNAL rename record at
      `dev/<milestone>/migration_<topic>.md` for every rename in its list, which
      includes "Checked-in example config keys (user-facing)" (:223) and "Test
      fixture paths read by `tests/conftest.py`, `dev/scripts/check_baseline.py`,
      or other scripts" (:225-226). Both fire here. The table at :254-262 marks
      the internal record **Required** and the user-facing guide **Optional**;
      §15 plans only the optional half (`docs/migration-config-tiers.md`).
    rationale: >-
      A required milestone artifact is missing from the plan, so the R13 seal
      would be incomplete. No runtime consequence.
    suggested_fix: >-
      Add `dev/milestones/r13/migration_config-tiers.md` to §15 and to §15.5
      step 7, carrying the old→new key-path table, the machinery to update, and
      the gate evidence. Note that naming.md's mandated `migration_<topic>.md`
      form overrides §8's kebab-case rule (:264-266).
  - id: repofit-9
    severity: minor
    section: "8. Loader semantics"
    finding: >-
      §8 puts `compose_config`, the three seam checks, `SHARED_SEAM_KEYS`,
      `HOISTED_SECTIONS`, path resolution and six error messages into
      `blueearth_cst/shared/snake_utils.py`, already 4658 lines and the single
      module AGENTS.md names in its write-set declaration rule as the seam that
      makes two otherwise-unrelated tasks non-independent ("`snake_utils.py`
      parses every Snakefile's config"). `shared/` has clear topic-module
      precedent for surfaces of this size and contract weight —
      `interchange_contracts.py` (1338), `provenance.py` (686),
      `climate_window.py` (280).
    rationale: >-
      Concentrating a new contract surface in the highest-contention file raises
      the cost of every concurrent slot for the life of the repo, for no
      cohesion gain that a sibling module would not also have.
    suggested_fix: >-
      Put it in `blueearth_cst/shared/config_composition.py` and re-export
      nothing; the Snakefiles import it directly, as they already do for
      `interchange_contracts`. §16's proposed `tests/test_config_composition.py`
      then names its module, which is the repo's dominant test-naming pattern.
  - id: repofit-10
    severity: minor
    section: "13. Advanced settings — interior organization (S3)"
    finding: >-
      Two gaps. (1) D-13.2 states the coupled-edit trio as schema + file +
      `tests/test_advanced_settings.py`. There is a FOURTH coupled consumer:
      `tests/test_batch_sizing.py:335` reads
      `ADVANCED_SETTINGS["defaults"]["batch_disk_headroom_fraction"]` and `:343`
      pins its validator's error path — and that key is the one and only entry
      D-13.1 moves. (2) §18 lists §13 as neutral, "the schema gains one nested
      level". It also changes the SHAPE of the `advanced_settings` mapping, which
      `provenance.py:262` embeds verbatim in `effective_config_document`, so
      `effective_config_sha256` moves for all four workflows, and with it
      `configuration_inputs_sha256` — the digest `_RUNS_README` tells users to
      compare runs with.
      I verified the two consequences this does NOT have: no manifested baseline
      target embeds either digest (the seven targets are three `type: yaml`
      snapshots, two `type: csv` change-factor tables compared by sha256 of their
      own bytes, one `type: indicator`, one `type: discharge`), and
      `build_experiment_config` (`write_experiment_config.py:48-52`) records only
      `experiment_name` plus the WF3 section, so the freeze is untouched. §16's
      three-target prediction survives.
    rationale: >-
      A test the trio rule does not name goes red; and a user comparing a pre-
      and post-migration run sees a `configuration_inputs_sha256` difference that
      §18 gives them no way to attribute.
    suggested_fix: >-
      Add `tests/test_batch_sizing.py:335,343` to D-13.2's coupled set. In §18,
      move §13 out of "Neutral" and state the digest movement explicitly, with
      the negative results above (no baseline target, no freeze impact) so a
      reader can tell an expected digest change from a defect.
  - id: repofit-11
    severity: minor
    section: "19. Open questions — Q1 key spelling"
    finding: >-
      Reasoned call, as requested: keep `config_path`. `dev/reference/naming.md`
      §3 (:55-61) makes `_path` mandatory for new code holding a file-path
      string, and §5 (:118-140) makes the path/object distinction the load-bearing
      one — `workflow_config` reads as a loaded mapping (`_cfg` territory,
      :126-130), which is exactly what the key is NOT. The stated objection (a
      prose collision with the Snakefile-local `config_path` variable) does not
      reach a convention: they are in different namespaces, and the proposed
      alternative `workflow_config` mirrors `model_build_config`, a
      GRANDFATHERED spelling that §3 tells new code not to imitate. Note that
      `model_build_config` was itself flagged for this class of rename
      (`naming.md:486`, `config_fn` → `config_path`).
    suggested_fix: >-
      Close Q1 as decided: `config_path`. If the prose collision matters, rename
      the Snakefile-local variable to `t1_path` in the §8.2 snippet rather than
      bending the config key.
  - id: repofit-12
    severity: blocking
    section: "11.1 D-11.1 — The snapshot becomes a composed document, not a byte copy"
    finding: >-
      A test exists whose entire purpose is to forbid what D-11.1 does, and the
      design does not name it. `tests/test_copy_config_files.py:51-67`
      (`test_content_is_copied_verbatim`) asserts
      `(cfg/"runs"/"snake_config_build_model.yml").read_text() ==
      snake.read_text()` — byte-equality between the snapshot and the source —
      with the docstring "A snapshot that mutates content would break the drift
      guard, which compares digests of these files across workflows." D-11.1
      replaces `shutil.copyfile` (N3, `copy_config_files.py:222`) with
      `yaml.safe_dump(composed, sort_keys=True)`, so this assertion fails by
      construction. It is the load-bearing test of the module §11 rewrites, and
      `tests/test_copy_config_files.py` carries ten references to
      `snake_config_build_model.yml` across ~600 lines. §15.5 step 4 lands
      D-11.1 with no test edit named anywhere.
    rationale: >-
      The commit that changes the snapshot's nature goes red on both CI legs on a
      test that encodes the OPPOSITE invariant, and the design has no answer for
      the invariant that test was written to protect. The design's own argument
      (§11.1: the guard reads sections, and `file_digest_or_absent` is
      content-agnostic — confirmed at `run_stress_test.smk:602-606`) is the right
      rebuttal to the docstring's stated rationale, but it has to be MADE, in the
      test and in the design, not left for an implementer to infer from a red
      assertion.
    suggested_fix: >-
      Add a §11.1 sub-point that retires `test_content_is_copied_verbatim` and
      replaces it with the invariant that actually holds — the snapshot
      round-trips to the composed mapping (`yaml.safe_load(snapshot) ==
      composed_config`) — carrying forward the verbatim-copy assertion for the
      catalog/template destinations at :64-67, which D-11.2 does not change. Name
      `tests/test_copy_config_files.py` in §15.5 step 4 and in §16's sweep.
      Separately: this test is the only gate in the suite that can see the
      snapshot's shape without the `test_local` fixture, which is why repofit-7
      matters — deleting it without a replacement leaves the composed snapshot
      ungated on every machine.
  - id: repofit-13
    severity: minor
    section: "12.4 `simulation_window ⊂ historical_window` (E8) — now genuinely cross-file"
    finding: >-
      §12.4 imposes an implementation obligation on an unnamed set: "The same
      applies to the message-shape tests in `tests/`." The set is two modules —
      `tests/test_resolve_simulation_window.py` and
      `tests/test_add_climate_forcing.py`, the only two in the suite that
      reference `simulation_window`. Telling an implementer to change error
      strings without naming which tests pin them is the same defect class as
      repofit-6, at smaller scale.
    suggested_fix: >-
      Name both modules in §12.4 and in §15.5 step 5.

---

## Appendix — evidence and clearances

All file:line references verified in
`C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2` on 2026-08-20.

### Premises I re-derived and that HOLD

**E9 / D-7.4 check-ignore demonstration — reproduced exactly.** `.gitignore:140-141`
is `test_case/*` + `!test_case/snake_config_*.yml`.

```
test_case/snake_config_rapid.yml                 -> exit 1  (not ignored)
test_case/snake_config_rapid_build_model.yml     -> exit 1  (not ignored)
test_case/snake_config_rapid_run_stress_test.yml -> exit 1  (not ignored)
test_case/my_seed.yml                            -> exit 0  (ignored)
```

`git ls-files test_case/` returns exactly the four seeds plus the two basin CSVs,
matching AGENTS.md. The design's tracking claim is correct — repofit-3 is about
the *other* consumer of the same glob shape, not about `.gitignore`.

**N1 — `config_path` as a declared rule input.** Confirmed at all six sites
(`analyze_climate.smk:344`, `build_model.smk:467`, `build_model.smk:535`,
`analyze_projections.smk:836`, `run_stress_test.smk:621`,
`run_stress_test.smk:836` under `ancient()`). D-10.3 rests on a true premise.

**§8.3's `R(entry)` matrix — confirmed.** `analyze_climate.smk:119`,
`build_model.smk:176` and `analyze_projections.smk:57` each declare
`CONFIG_PROJECTION = ("project", "shared", "workflows.<own>")`;
`run_stress_test.smk:332-335` declares `guarded_sections = ("project",
"shared.basin", "workflows.build_model", "workflows.analyze_projections")` and
`:362-366` derives `CONFIG_PROJECTION` from it plus
`"workflows.run_stress_test"`. §15.4 step 3's instruction to delete unused T2
files is therefore safe as written, including its WF3 carve-out.

**§12.1 — `run_workflows.py` needs no change.** `_enabled_flags`
(`run_workflows.py:282-314`) checks presence, `isinstance(workflows[name], dict)`
and `isinstance(section["enabled"], bool)`. It does **not** reject unknown keys,
so a `{enabled, config_path}` stanza passes unchanged. The design's cleanest
unchanged-by-construction claim is correct.

**§10.1's freeze argument — confirmed.**
`write_experiment_config.py:48-52` records `{"experiment_name",
"run_stress_test": dict(experiment_cfg or {})}`, and the key-union diff in
`_frozen_differences` is documented at `:63-140` with the `t2608072234`
precedent the design cites. Keeping `enabled` in and `config_path` out is the
right call.

**§16's manifest enumeration — confirmed by direct load.**
`dev/baseline/manifest.json` (`version: 3`, `project_dir: test_case/test_local`)
carries exactly seven targets; all three `type: yaml` snapshots carry
`sha256: 00ef44f7fef2b9d2be44d5c64ec9bf0d7aedadff663bdbf4748ad6e053b88381`,
reproducing N5. The two `type: csv` targets carry their own `sha256` +
`size_bytes`; `q_indicators.csv` is `type: indicator` and
`run_default/output.csv` is `type: discharge`, neither of which embeds a config
digest. The three-target prediction is sound.

**D-10.3's added rule inputs are safe from `test_snapshot_config_rules.py`.**
That module greps each rule's text block but pins only the `params:` names
(`:68-70` `effective_config`, `advanced_settings`, `run_record`), the stable
output path (`:67`), the record path (`:71`), and the projection literals
(`:126`, `:139-141`). It asserts nothing about the `input:` label set, so adding
`config_workflows = WF_CONFIG_PATHS` to all six blocks passes it unchanged. It
does pin `CONFIG_PROJECTION = {expected}` verbatim per Snakefile at `:126`, which
is a reason to leave those literals alone — as §14.3 already recommends.

**`get_config`'s contract (`snake_utils.py:595-627`) — preserved.** Present key
returned as-is including `None` (:622-623); optional absent returns the default
(:624-625); required absent raises `ValueError` (:626-627). `compose_config`
running before any other module-level code (§8.2) leaves every call site reading
the same shape, so §8.1's invariant genuinely covers it.

### Tooling and CI — clearance

Nothing in the following reads a path the design moves:

- **`.github/workflows/ci.yml`** — three steps only: `pixi run ruff check .`,
  `pixi run format-check`, `pixi run pytest tests/ -q -rs`. No config path
  appears. It does mean every test breakage in repofit-1/3/6 lands as a red CI on
  BOTH legs, and the documented expected-skip baseline (499/31/1 windows,
  498/32/1 ubuntu) will shift — worth a one-line update in the same commit.
- **`pixi.toml` tasks** — `dag-wf0`…`dag-wf3` (:169-172) and `tree-check` (:185)
  pin `--configfile test_case/snake_config_baseline.yml`; `run-workflows`
  (:195-210) deliberately pins nothing. All four T1 paths are unchanged by the
  design, and the tasks' own comment at :205-207 records that pixi executes at
  the manifest root, so a repo-root-relative `config_path` resolves correctly
  under §8.4. This is a genuine positive result for the CWD-relative rule — for
  the SEEDS. It is also why repofit-2 is invisible in every worked example.
- **`profiles/default/config.yaml`** — `quiet: [reason]` and
  `show-failed-logs: true`. No config-path coupling.
- **`scripts/run_snake_test.cmd`** — `set CFG=test_case/snake_config_baseline.yml`,
  path unchanged.

### Placement — `split_project_config.py` in `scripts/`

**Correct, but argued from the wrong precedent.** AGENTS.md's O-23 rule splits by
invocation model: `blueearth_cst/` is executed by Snakemake, `scripts/` is what a
user runs to execute the pipeline, `dev/scripts/` inspects or maintains the repo
and is never part of a run. §15.3 justifies `scripts/` as "what a user runs to
drive the pipeline" — a migration tool does not drive the pipeline, so that
sentence does not actually carry the decision. The clinching precedent, which the
design does not cite, is `scripts/suggest_experiment_name.py`: a user-facing,
one-shot config editor that is likewise not part of a run and lives in `scripts/`.
Cite that instead. The report-only-by-default / explicit-`--write` shape
correctly mirrors `dev/scripts/prune_series_cache.py` and
`prune_climate_store.py`.

### Validation ladder (§16) vs AGENTS.md — over/under-gating

Correctly gated: `test_cli.py` as the parse gate (AGENTS.md requires it when "a
rule's declared input changed", which D-10.3 does); `lint`/`format-check` before
commit; `test-fast` at the merge; `test-full` at the merge rather than only at the
push, with the right justification (the branch touches all four Snakefiles and
`shared/`); `check_baseline.py check` from the primary checkout against
`snake_config_baseline.yml` with WF1 under `--notemp`; and the deliberate refusal
to run any figure gate, which matches AGENTS.md's "figures are terminal artifacts"
rule exactly.

Not over-gated: `semantic_tree_diff.py` is correctly absent — no tree shape moves,
and D-11.2 keeps T2 files out of `<project_dir>/config/templates/`, which
`tree-check` is the right instrument to confirm.

Under-gated: repofit-7 (the fixture layer), and §16 has no row that would catch a
malformed *composed snapshot* on a machine without a fresh `test_local` run.

### Config-comment style

§11.1's "comments are lost" trade is consistent with the repo's stated policy —
the `config/runs/` bin is a record, not a source, and the source files stay the
annotated artifact. §15.3's insistence that the splitter work on TEXT rather than
`yaml.safe_dump` is the same distinction applied to the source side, and matches
`suggest_experiment_name.py`'s existing stance. No finding here; the design gets
this right and states the trade in the correct direction.
