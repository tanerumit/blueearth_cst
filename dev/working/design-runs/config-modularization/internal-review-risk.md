verdict: revise
doc_version: design-v1.md
findings:
  - id: risk-1
    severity: blocking
    section: "## 12. Downstream consumers"
    finding: >-
      The downstream-consumer inventory is incomplete. Three tools read a raw
      `yaml.safe_load` of the T1 config and index `config["workflows"][<name>]`
      without ever calling `compose_config`, and none of them is named anywhere
      in the design: `dev/scripts/snapshot_project_tree.py:77-88` (the
      `pixi run tree-check` gate), `dev/scripts/prune_series_cache.py:55-69`,
      and `scripts/plot_workflow_dag.py:116`. After the split those sections
      hold only `{enabled, config_path}`. `prune_series_cache` fails hard
      (`my["clim_project"]` -> KeyError). The other two fail SILENTLY, because
      they read through `.get(key, default)`: `snapshot_project_tree`
      substitutes `experiment_name="experiment"` and `clim_project="cmip6"`,
      and `plot_workflow_dag` drops the experiment id from the render filename
      that AGENTS.md documents as
      `logs/dag/<project_name>_wf3_<experiment>_dag.png`.
    rationale: >-
      The silence is the damage, and it is self-masking. `pixi run tree-check`
      is pinned to `test_case/snake_config_baseline.yml` (`pixi.toml:185`),
      whose values are `experiment_name: experiment` (line 61) and
      `clim_project: cmip6` (line 40) -- EXACTLY the two fallback defaults. So
      the repo's own gate keeps passing while every project whose experiment is
      not literally named `experiment` gets its entire `experiments/<name>/`
      subtree reported as undeclared. And §16 lists `pixi run tree-check` with
      expected result "unchanged", so the validation plan actively certifies a
      tool this design breaks. This is the "nothing fails, so nobody looks"
      class AGENTS.md records twice (the vendored-console marker, the ten-day
      CI outage), arriving through a declared gate.
    suggested_fix: >-
      Add a §12 subsection enumerating every raw-T1 consumer and its decision.
      Verified-safe today: `prune_climate_store.py:62,99`,
      `prune_config_snapshots.py:196`, `region_bbox.py:105`,
      `scaffold_project_tree.py:82` (all read `project`/`shared` only).
      Broken: the three above. The cheapest fix is to make `compose_config`
      importable and callable outside Snakemake (it is already specified as a
      pure function of a parsed mapping plus a path) and have all three call
      it; `R(entry)` for these tools is "whatever section I index".
  - id: risk-2
    severity: major
    section: "### 10.5 D-10.5 — `file_sha256(config_path)`: the one mechanism whose meaning changes"
    finding: >-
      T2 bytes are routed into the RECORD-time reference set only. §10.5
      registers each T2 file in `copy_config_files.__main__`'s
      `other_config_files` / `reference_roles`, which feeds
      `_snapshot_references` -> `run_record.referenced_inputs` ->
      `run_record.configuration_inputs_sha256`
      (`copy_config_files.py:457-459`). It does NOT add them to each
      Snakefile's parse-time `CONFIG_REFERENCES`
      (`analyze_climate.smk:122`, `build_model.smk:181-197`,
      `analyze_projections.smk:59`, `run_stress_test.smk:368`), which is what
      feeds `referenced_inputs_for_digest` -> the module-level
      `CONFIGURATION_INPUTS_DIGEST` threaded through rule x.01's params and
      written on every journal line.
    rationale: >-
      Two observable consequences. (a) The same run emits two values of a
      field with one name: `run_record.yml`'s `configuration_inputs_sha256`
      would include the T2 bytes and the `journal.jsonl` line's would not.
      They coincide today because `_reference_identity`
      (`provenance.py:563-591`) reduces both sides to `sha256:<hash>` over the
      same file set; adding a member to one side only breaks that. (b) The
      parse-time digest exists precisely so an in-place edit to a referenced
      file RE-FIRES the recording rule (`build_model.smk:190-192`: "Hashed at
      parse time so the digest below moves when one is edited IN PLACE -- the
      recorded hash alone would move without re-firing anything"). Leaving T2
      out reproduces exactly the defect that comment records, for the newly
      most-edited config file in the repo.
    suggested_fix: >-
      Add `("workflow_config_<name>", path)` for every entry in
      `WORKFLOW_CONFIG_PATHS` to `CONFIG_REFERENCES` in all four Snakefiles,
      in the same commit as D-10.3, and state that the two reference sets must
      stay identical.
  - id: risk-3
    severity: major
    section: "## 9. Shared-seam enforcement (S4)"
    finding: >-
      D-9.3 (cross-T2 multi-declaration) is scoped to "all T2 files in
      `R(entry)`". Per §8.3's own table, `R(analyze_climate)`,
      `R(build_model)` and `R(analyze_projections)` are singletons, so for
      three of the four entry points the check has exactly one file to look at
      and can never fire. Only WF3 loads more than one, and it loads three of
      the four. The pairs `analyze_climate`x`build_model`,
      `analyze_climate`x`analyze_projections` and
      `build_model`x`analyze_projections` are unreachable by any entry point.
    rationale: >-
      D-9.3 is the design's answer to the one failure D-9.1 and D-9.2 cannot
      see -- "a genuinely new cross-workflow key, invented after this design
      lands, that nobody thought to add to `SHARED_SEAM_KEYS`. Its first
      symptom is being written twice, and this check turns that symptom into a
      parse-time failure." For the three unreachable pairs that claim is
      false: the duplicate is written twice, nothing fires, and the two copies
      agree until someone edits one -- which is the invisible drift the
      milestone exists to end. This is a hole in decision criterion 1, the
      design's central claim, not a peripheral one. (Checked: the four current
      `workflows.<name>` sections share no top-level key name across all
      shipped seeds and the template, so nothing breaks at migration; the hole
      is prospective.)
    suggested_fix: >-
      Run D-9.3 over every T2 file that RESOLVES, not only over `R(entry)` --
      the T1 stanzas are all present and well-formed by D-9.1, so the paths
      are known; skip an unresolvable one with a note rather than failing. Or
      state the limit explicitly in §9's "Coverage, honestly" paragraph, which
      currently reads as though D-9.3 is global.
  - id: risk-4
    severity: major
    section: "### 10.4 D-10.4 — `reporting:` lives in the WF3 T2 file, hoisted"
    finding: >-
      `HOISTED_SECTIONS = {"run_stress_test": ("reporting",)}` names one
      owner, but `REJECTED_IN_T2` (D-9.2) does not contain `reporting`. A
      `reporting:` block written at the top level of `build_model.yml` (or
      `analyze_climate.yml`, or `analyze_projections.yml`) is therefore
      accepted and, by D-10.1's `{"enabled": ..., **<T2 body>}` merge, lands
      inside `config["workflows"]["build_model"]`. D-9.3 cannot see it unless
      it appears in two files at once. The design also never states what
      happens when `reporting:` is present in T1 AND in the WF3 T2 file.
    rationale: >-
      `workflows.build_model` is one of the four sections in
      `guarded_sections` (`run_stress_test.smk:332-335`) and is inside WF3's
      derived `CONFIG_PROJECTION` (`:355-361`). So a caption edit in the wrong
      file silently enters `guarded_sections_digest`,
      `effective_config_digest` and the wf1 snapshot the drift guard compares
      against -- producing a "your model was built under different settings"
      refusal from rule 3.01 for a change to a figure caption. That is
      precisely the outcome §10.4 says hoisting exists to prevent ("nesting
      `reporting:` inside the workflow section would silently revoke it"),
      reintroduced through the unguarded direction.
    suggested_fix: >-
      Derive the rejection set from the hoist map: every name in
      `HOISTED_SECTIONS.values()` is rejected in every T2 file except its
      declared owner's. Separately, define a `reporting:` present in both T1
      and the owning T2 as a parse-time error rather than a silent precedence
      rule.
  - id: risk-5
    severity: major
    section: "### 7.4 D-7.4 — Filenames, derived mechanically from the workflow key"
    finding: >-
      The stated mitigation for the 4-to-20 file-count cost -- "point several
      T1 files at one shared T2 wherever they then agree" (§7.4, restated in
      §18) -- is unsafe for the WF3 T2 file and is nowhere bounded. §12.2 makes
      `suggest_experiment_name.py` splice `experiment_name` into the WF3 T2
      file in place. `experiment_name` is per-project by nature (`rapid` sets
      `experiment_rapid`, `baseline` sets `experiment`), so a T2 shared across
      two T1 files makes naming one project's experiment silently re-point the
      other's. §8.4's duplicate-`config_path` refusal catches only two
      workflows inside ONE T1; nothing at parse time can see two T1 files
      pointing at one T2.
    rationale: >-
      Observable: after `python scripts/suggest_experiment_name.py
      test_case/snake_config_rapid.yml --name X` against a shared WF3 T2, a
      baseline run writes to `experiments/X/` and the baseline manifest target
      `test_case/test_local/experiments/experiment/config/snake_config_run_stress_test.yml`
      goes missing -- so `check_baseline.py check`, the §16 falsifier, reports
      a missing target rather than a drift, on a change nobody made to the
      baseline config. More generally, sharing a T2 converts "two variants
      that drift invisibly" into "two variants that change together
      invisibly", which is a different failure, not the absence of one.
    suggested_fix: >-
      Rule sharing IN for `analyze_projections` / `analyze_climate` /
      `build_model` T2 files and OUT for the WF3 T2 file, or lift
      `experiment_name` back into T1's `run_stress_test` stanza as a third
      permitted key (which then costs a D-9.1 exception and a re-check of
      D-10.1's freeze argument, since `experiment_name` is inside the frozen
      section). Either way §18 must not book "share the T2s" as the mitigation
      without the constraint.
  - id: risk-6
    severity: major
    section: "### 15.3 D-15.3 — `scripts/split_project_config.py`, report-only by default"
    finding: >-
      Two unexamined failure modes in the text splitter. (a) YAML anchors,
      aliases and merge keys are not mentioned. An anchor defined in `shared:`
      or in one workflow section and aliased inside another becomes an
      undefined alias once the sections are written to separate files --
      `yaml.safe_load` then raises `ComposerError` on the T2 file; a `<<:`
      merge that resolves differently after the split changes VALUES silently.
      A `|` or `>` block scalar inside a workflow section is a second silent
      corruption path: dedent-by-four strips four spaces from the scalar's
      CONTENT, changing the string value with no structural symptom.
      (b) The acceptance gate `compose_config(split(x)) == yaml.safe_load(x)`
      is specified only "for each shipped seed and for the template" -- i.e.
      for five files the implementer controls, none of which contains an
      anchor or a block scalar. A user's own config, which is the only file
      `--write` actually rewrites, gets no verification at all.
    rationale: >-
      §18's residual-risk table books the splitter risk as "mangles a comment
      block", severity medium. Mangling a comment is cosmetic; mangling a
      VALUE is not. A value changed by a dedent or a broken alias produces a
      config that parses and runs: for WF1/WF2 it silently produces different
      numbers under an unchanged-looking config, and only WF3 fails loudly
      (via the freeze). The design's own G3 output-neutrality claim is what is
      at stake, and the gate it names cannot reach the files that matter.
    suggested_fix: >-
      Make `--write` run the same round-trip assertion against the user's own
      file before touching anything and refuse to write on mismatch (the
      report-only default already computes everything needed). Refuse outright
      when the source document contains `&`/`*`/`<<:` or a block scalar inside
      a workflow section, naming the construct -- that is a short check and
      turns an unbounded class into a stated non-support.
  - id: risk-7
    severity: major
    section: "### 10.3 D-10.3 — T2 files become declared rule inputs"
    finding: >-
      The stated mechanism does not hold for rule 3.09. §10.3 argues
      "`prepare_spatial_maps` (1.06) and `prepare_stress_test_grid` (3.09)
      have no such params, which is why the input declaration is the mechanism
      rather than a belt-and-braces addition" -- but 3.09 declares
      `config = ancient(config_path)` (`run_stress_test.smk:836`), and the
      table's own "Adds" column keeps that qualification
      (`config_workflows = ancient(WF_CONFIG_PATHS)`). An `ancient()` input is
      by definition excluded from change detection, so the declaration creates
      no rerun trigger there.
    rationale: >-
      The retrigger for 3.09 actually arrives from a different decision --
      §10.6's choice to hand `prepare_cst_parameters` its `stress_test_cfg` as
      a PARAM, which Snakemake's params rerun-trigger does see (the same
      mechanism `run_stress_test.smk:325-327` relies on for the guard). The
      design never connects the two, so an implementer who descopes §10.6, or
      implements it as "hand the module the T2 path", gets exactly the F7
      defect §10.3 is written against: a user edits `run_stress_test.yml`, the
      stress-test grid values change, and rule 3.09 stays satisfied with a
      stale `stress_test_lookup.csv`.
    suggested_fix: >-
      Correct the sentence, and state the dependency explicitly: for 3.09 the
      change detector is the resolved-section param from D-10.6, and D-10.3
      and D-10.6 must land together (§15.5 step 3 already bundles them -- say
      why).
  - id: risk-8
    severity: major
    section: "## 16. Validation plan"
    finding: >-
      The migration's only cross-cutting gate is a "stale-spelling grep
      sweep" over docs and tests. A grep for spellings cannot see a test that
      CONSTRUCTS the pre-split config shape as a Python dict literal, and
      `tests/` does that in nine modules (23 occurrences of `"workflows":`),
      including `tests/test_snapshot_project_tree.py`,
      `tests/test_plot_workflow_dag.py`,
      `tests/test_prepare_cst_parameters.py` and
      `tests/test_prepare_weagen_config.py` -- the four modules whose input
      shape this design changes.
    rationale: >-
      Those fixtures keep asserting the pre-split behaviour and keep passing,
      which is exactly why risk-1's breakage has no gate: the tool changes
      meaning, its test still builds the old shape, and the suite stays green.
      AGENTS.md records this failure verbatim ("R9 moved the tree and left 22
      such failures, three of them behind an `os.path.exists` guard that
      turned a wrong path into a silent skip"), and notes that tree-shape
      gates "do not read the code that reads the tree, so they cannot
      substitute". §16 has no gate that reads the code that reads the config.
    suggested_fix: >-
      Replace the spelling sweep with an explicit inventory step: grep
      `tests/` for `"workflows"` dict literals and for `["workflows"]`
      indexing, list each hit with a decision (migrate the fixture / migrate
      the module / no change), and make that list an acceptance item rather
      than a sweep.
  - id: risk-16
    severity: major
    section: "### 15.4 Mechanical steps for an existing project"
    finding: >-
      Migration silently re-runs the pipeline, and the design books the cost
      nowhere. Step 4 says "Nothing under `project_dir` needs hand-migration",
      which is true and reads as "nothing re-runs". But migration rewrites
      T1's bytes, and T1 is a NON-ancient declared input of
      `prepare_spatial_maps` (`build_model.smk:535`), so the first
      post-migration WF1 run re-executes rule 1.06 and everything downstream
      of it. That cascade then reaches WF3 through the design's own step 5:
      WF1 rewrites its snapshot with composed content -> `wf1_snapshot_digest`
      moves -> rule 3.01 re-fires (step 5 says so) -> 3.01 rewrites
      `.project_consistency_ok`, which rules 3.09 and 3.10 declare BARE, not
      `ancient()` (`run_stress_test.smk:837, 858`;
      `check_project_consistency.py:195-199` names the two consumer classes
      explicitly, "the four per-experiment roots (fresh sentinel)" versus the
      `ancient()` one) -> 3.10 feeds 3.11 -> the realization and stress-test
      cascade runs.
    rationale: >-
      Driven through `scripts/run_workflows.py`, which is the documented way
      to run the pipeline, migrating a project with a completed experiment
      re-runs the entire stress test to produce identical results. That is a
      real, unbudgeted cost against G5's "mechanical, bounded migration" and
      is absent from §18's Negative list, which books only the file count, the
      lost comments, the clean break, the two-file reading cost and the
      three-target baseline re-record. §15.4 step 5 supplies the evidence for
      the second half of the chain and treats the re-fire as benign because it
      "passes" -- passing is not the same as being free.
    suggested_fix: >-
      State the cascade in §15.4 and in `docs/migration-config-tiers.md`
      (first post-migration run rebuilds from rule 1.06 down and re-runs the
      experiment, producing identical outputs), add it to §18's Negative list,
      and say whether a `--touch`-style shortcut is acceptable for a project
      whose composed values are provably unchanged -- which the splitter's
      round-trip gate can prove per project.
  - id: risk-9
    severity: minor
    section: "### 8.2 D-8.2 — Where composition happens"
    finding: >-
      §10's premise is that everything outside "a file's bytes, a DAG edge, a
      disk re-read" is safe by the composition invariant, and §10.6 names two
      disk re-readers as the complete set of bypasses. There is a third kind
      of bypass it does not name: `check_project_consistency.py:225` receives
      `live_cfg=sm.config`, i.e. Snakemake's `workflow.config`, not the
      Snakefile-local name `config`.
    rationale: >-
      It is safe as specified -- `workflow.config` returns
      `self.globals["config"]` (`snakemake/workflow.py:1728-1729`) and the
      Snakefile is exec'd into `self.globals` (`:1612`), so rebinding
      `config = compose_config(...)` does reach every `script:` module. But
      the design nowhere states that this is why D-8.2's rebinding is
      sufficient, and the property is a Snakemake implementation detail. An
      implementer who binds the result to any other name hands rule 3.01 an
      un-composed T1 with no `workflows.build_model`, and the guard refuses
      every experiment in the project.
    suggested_fix: >-
      Add `sm.config` to §10's inventory, state the invariant
      (`compose_config`'s result must be bound to the global name `config`, or
      the mapping must be updated in place), and add a
      `tests/test_config_composition.py` case asserting the composed shape is
      visible through `workflow.config`.
  - id: risk-10
    severity: minor
    section: "### 11.1 D-11.1 — The snapshot becomes a composed document, not a byte copy"
    finding: >-
      The snapshot inventory undercounts. There are FOUR
      `config/runs/snake_config_<workflow>.yml` snapshots, not three:
      `analyze_climate.smk:329,357` writes
      `{project_dir}/config/runs/snake_config_analyze_climate.yml`. N5, §1,
      §11.1 ("The three snapshots stop being byte-identical") and the
      `_RUNS_README` rewrite all speak of three, which is the count of
      BASELINE TARGETS, not the count of files the change affects.
    rationale: >-
      §16's "exactly three targets differ" prediction is unaffected (verified:
      `dev/baseline/manifest.json` has exactly 7 targets, three of them the
      `type: yaml` snapshots N5 names; the wf0 snapshot is not among them).
      But the `_RUNS_README` string edit and the migration document both
      describe the bin's contents, and a bin that holds four files described
      as three is the kind of stale reference AGENTS.md's
      keep-references-current rule targets.
    suggested_fix: >-
      Say "four snapshots, three of which are baseline targets" wherever the
      count appears, and confirm the wf0 composed snapshot (whose `workflows`
      map holds only `analyze_climate`, and for three of the four seeds only
      `{enabled: true}`) is intended.
  - id: risk-11
    severity: minor
    section: "### 10.6 D-10.6 — Two disk re-reads must be redirected"
    finding: >-
      The absence claim about `prepare_cst_parameters`'s non-Snakemake path is
      refuted. §10.6 says only the `lookup_fn` default at `:250-251` is taken
      outside Snakemake and "it needs no change". The same `else` branch
      (`prepare_cst_parameters.py:279`,
      `prep_cst_parameters(config_fn=sys.argv[1])`) reaches `:162-165`, which
      indexes `yml["workflows"]["run_stress_test"]["stress_test"]` -- a path
      that after the split exists in no single file a user would pass.
    rationale: >-
      Under D-10.6 the Snakemake branch stops passing a config path at all, so
      the CLI branch is left reading a config shape nothing produces. It fails
      with a KeyError on the first direct invocation after migration. Small
      blast radius (a dev convenience path), but the design asserts an absence
      it did not check, and §16 has no gate that runs the module outside
      Snakemake.
    suggested_fix: >-
      Either point the CLI branch at the WF3 T2 file (top-level `stress_test`)
      or delete the branch; state which.
  - id: risk-12
    severity: minor
    section: "### 11.2 D-11.2 — T2 files are recorded, not copied"
    finding: >-
      "The registration reuses `other_config_files` / `reference_roles`
      unchanged; only the destination is `None`" is not achievable unchanged.
      `_snapshot_references` (`copy_config_files.py:305`) executes
      `destination_dir = Path(dest_dir)` for any reference whose
      `_tracked_blob` is None -- which a project-authored T2 file living
      outside the checkout always is -- so a `None` destination raises
      `TypeError` there.
    rationale: >-
      A record-only branch is a real code change in the reference machinery,
      not a call-site change, which matters for §15.5's commit sequencing
      (step 4) and for the "touches nothing else" claim. The resulting entry
      also carries `recoverable: false`, `archived_path: null`,
      `git_blob: null` -- a referenced input the record can neither reproduce
      nor point at, which is a first for this schema.
    suggested_fix: >-
      Specify the branch explicitly, and have the record say WHY the file is
      unarchived (its content is inlined in the composed snapshot beside it)
      -- in `_RUNS_README`, not only in this design.
  - id: risk-13
    severity: minor
    section: "## 1. Problem statement"
    finding: >-
      `reporting:` does not exist in any shipped artifact. All four
      `test_case/snake_config_*.yml` and
      `config/templates/snake_config.template.yml` have top-level keys exactly
      `['project', 'shared', 'workflows']`; the only occurrence anywhere is a
      COMMENTED example block at
      `config/templates/snake_config.template.yml:210` (`#reporting:`). §1
      describes the current file as carrying "a top-level `reporting:`", and
      §10.4's "Today `reporting:`'s bytes live inside the single config file
      ... so a caption edit already dirties a WF1 rule" describes a config
      nobody has.
    rationale: >-
      Two consequences. `pytest tests/test_cli.py` and the D-15.3 round-trip
      gate run only against the seeds and the template, so `HOISTED_SECTIONS`
      ships exercised by nothing but its own unit test -- and it is a
      permanent special case in the loader. And the splitter's stated
      transform ("move a top-level `reporting:` block into the
      `run_stress_test` T2 file") will not match `#reporting:`, so the
      template's guidance block is stranded in T1 pointing users at a
      placement the loader no longer honours.
    suggested_fix: >-
      Correct §1 and §10.4's factual framing; add a seed or template fixture
      that actually declares `reporting:` so the hoist is covered by
      `test_cli`; and state what the splitter does with the commented block
      (move it, or rewrite it into the WF3 T2 template).
  - id: risk-14
    severity: minor
    section: "## 18. Consequences and risks"
    finding: >-
      Three of the four shipped seeds and the template declare
      `analyze_climate: {enabled: ...}` and nothing else. Their wf0 T2 body is
      therefore `{}` -- content-free files that exist only to be pointed at,
      permitted by §8.4's "file is empty / parses to `None` -> accepted as
      `{}`" rule.
    rationale: >-
      §18 books the 4-to-20 growth as an accepted cost whose mitigation is
      prospective reconciliation. Four of those files are empty by
      construction, not by incidental divergence, so reconciliation cannot
      reduce them. This is measurable now and belongs in the honest accounting
      rather than being discovered at implementation.
    suggested_fix: >-
      Allow a `config_path` to be omitted (not merely dangling) for a workflow
      whose body would be empty, treating absence as `{}` for a workflow in
      `R(entry)` -- or state the four empty files as part of the cost.
  - id: risk-15
    severity: minor
    section: "### 15.4 Mechanical steps for an existing project"
    finding: >-
      Step 3 instructs users to "leave their `config_path` pointing at a path
      that does not exist" for workflows they never run, while §12.1 keeps the
      wrapper reading T1 only and Q4 defers a `config_path` preflight out of
      scope.
    rationale: >-
      `run_workflows.py` invokes workflows in fixed order and stops on the
      first nonzero exit. A dangling `config_path` on an enabled workflow is
      therefore discovered at Snakefile parse time DURING the sequence, after
      earlier workflows have already run -- a class of failure
      `_check_wf1_leaves` exists to move to the front. The clean break (§15.1)
      makes this the expected first-run state for every migrated project,
      which is the moment the preflight is worth most.
    suggested_fix: >-
      Either resolve Q4 in favour of the preflight for this milestone, or have
      step 3 recommend deleting the whole stanza's `config_path` key rather
      than leaving a dangling one (which requires §7.1 to state plainly that
      `config_path` may be absent for a workflow outside `R(entry)`).
  - id: risk-17
    severity: minor
    section: "### 8.1 D-8.1 — The composition invariant"
    finding: >-
      Snakemake `--config key=value` passthrough is never considered.
      `scripts/plot_workflow_dag.py:50` documents `-- --config foo=bar` as a
      supported passthrough and `scripts/run_workflows.py:46,1061-1069`
      sanitizes and records passthrough `--config` overrides. Those are merged
      into the config mapping before the Snakefile body executes, hence before
      `compose_config`.
    rationale: >-
      Under D-9.1's closed stanza, any override that writes a workflow setting
      into `workflows.<name>` becomes a parse-time REJECTION rather than an
      override, and an override of the whole `workflows` key silently replaces
      the stanzas the loader then validates. Neither behaviour is stated, and
      the migration error message (§15.2) would name a key the user passed on
      the command line as though it were in their file.
    suggested_fix: >-
      One paragraph in §8 stating that CLI overrides are applied to T1 before
      composition and are subject to D-9.1, and that a workflow setting must
      be overridden by editing the T2 file. Adjust the §15.2 error text so a
      CLI-supplied key is not attributed to the config file.
  - id: risk-18
    severity: minor
    section: "### 8.4 D-8.4 — Path resolution"
    finding: >-
      The duplicate-`config_path` refusal in §8.4's failure table does not say
      what is compared. If it compares the raw string, two spellings of one
      file evade it -- `config/workflows/build_model.yml` versus
      `./config/workflows/build_model.yml`, a trailing-separator variant, a
      symlink, or a case-only difference on Windows.
    rationale: >-
      The check's own stated rationale is that "Two workflows sharing one
      settings file would silently give each the other's keys, and the seam
      rule (§9) would then have nothing to test against" -- and D-9.3 cannot
      substitute, because with one file on disk there is only one file to
      compare. The repo has already paid for this exact bug class one layer
      down: `copy_config_files.py:317-325` compares destinations with
      `os.path.normcase(os.path.abspath(...))` rather than `resolve()`, with a
      comment explaining that case-only differences "would collide on a re-run
      and silently overwrite on a fresh one -- the same file lost, but only
      sometimes".
    suggested_fix: >-
      Specify the comparison key as `os.path.normcase(os.path.abspath(...))`
      of the resolved path, citing that precedent, and add a
      `test_config_composition.py` case for a case-only and a `./`-prefixed
      duplicate.

# Appendix — evidence, and what checked out

Read or executed in `C:\Users\taner\workspace\.worktrees\blueearth_cst\session-2`
on 2026-08-20. Nothing below is carried from the intake unverified.

## Framing note

`revise`, not `reject`. Every finding above is fixable **inside** the G1
framing: path-referenced composition survives, Candidate A survives, the clean
break survives. Nothing here argues for CLI multi-configfile merge, for a
dual-mode loader, or for a rename. The design's central mechanism — D-8.1's
composition invariant, and the corollary that the two in-memory digests and the
experiment freeze are unchanged by construction — is **correct as argued**, and
I re-derived it rather than taking it on trust. The findings cluster exactly on
the boundary the design itself identifies as the hard part: the things that are
*not* in-memory reads. It found four such places; this review found three more
(risk-1, risk-2, risk-9).

## What checks out (verified, not assumed)

- **D-10.1 / the experiment freeze.** `build_experiment_config`
  (`write_experiment_config.py:47-52`) records
  `{"experiment_name", "run_stress_test": dict(experiment_cfg)}`, and rule 3.07
  passes `experiment_cfg = my_cfg` (`run_stress_test.smk:771`) — the whole
  section, `enabled` included. `_frozen_differences` (`:63-110`) is a key-union
  diff over `set(was) | set(now)`. So merging `enabled` back and keeping
  `config_path` out is exactly right, and **no already-run experiment is
  refused by migration**, provided the splitter preserves values (risk-6).
- **§16's target enumeration.** `dev/baseline/manifest.json['targets']` is a
  dict of exactly **7** entries: the three `type: yaml` snapshots N5 names, two
  `type: csv` CMIP6 change-factor tables, one `type: indicator`
  `q_indicators.csv`, one `type: discharge` `run_default/output.csv`.
  `experiments/<exp>/results/run_metadata.json` is indeed **not** a target. The
  "exactly three" prediction stands (subject to risk-2, which moves a digest
  inside a record rather than a target).
- **§8.3's `R(entry)` rule is genuinely enforced.** `provenance.project_config`
  (`provenance.py:201-217`) raises `KeyError` naming the missing path when a
  projection path is absent, so a WF3 run with no `build_model` T2 file fails
  loudly at parse. Note the *softer* half the design cites first:
  `run_stress_test.smk:537-540` reads `wflow_outvars` through
  `.get(...) or {}` with `optional=True`, so that read alone would have
  degraded silently to `DEFAULT_WFLOW_OUTVARS`. The hard refusal comes from the
  projection, not from the `wflow_outvars` read.
- **Cyclic references are structurally impossible**, so the brief's cycle
  question is closed by D-9.2 rather than needing a check: `workflows` is in
  `REJECTED_IN_T2`, so a T2 file cannot reference further T2 files. There is
  exactly one level of indirection by construction.
- **D-8.2's rebinding reaches `script:` modules.** `workflow.config` returns
  `self.globals["config"]` (`snakemake/workflow.py:1728-1729`) and the
  Snakefile is exec'd into `self.globals` (`:1612`). See risk-9 for the caveat.
- **D-9.2 / D-9.3 fire on nothing today.** Across all four seeds and the
  template, the four `workflows.<name>` sections share **no** top-level key
  name, and no workflow key collides with a `shared:` key (`shared` is exactly
  `basin`, `historical_window`, `clim_historical` in every one). Migration will
  not trip either check on shipped material.
- **N7's divergence claim**, independently reproduced: the four seeds' sections
  differ pairwise, and `analyze_climate` is `{enabled}`-only in three of them
  (which is risk-14).
- **N2 / N8, the two disk re-reads**, verbatim: `prepare_weagen_config.py:89-90`
  (`read_yml(snake_config_path)` → `yml_snake["workflows"]["run_stress_test"]`,
  used at `:103` for `realizations_num`) and
  `prepare_cst_parameters.py:162-165` (`open(config_fn)` →
  `yml["workflows"]["run_stress_test"]["stress_test"]`). The params redirect is
  the right call — see risk-7 and risk-11 for the two things it leaves open.
- **`allocate.py` reads nothing.** A grep for `yaml|open(|config` over
  `blueearth_cst/experiment/allocate.py` returns one docstring line, so E6's
  "nothing in `allocate.py` hashes config" extends to "nothing there reads it
  either" — `resolve_default_experiment_name` is not a fourth raw-T1 consumer.

## Evidence details by finding

**risk-1.** `dev/scripts/snapshot_project_tree.py:77-88`:

```python
experiment = workflows.get("run_stress_test", {})
projections = workflows.get("analyze_projections", {})
return {
    "experiment_name": experiment.get("experiment_name", "experiment"),
    ...
    "clim_project": projections.get("clim_project", "cmip6"),
}
```

`test_case/snake_config_baseline.yml:61` is `experiment_name: experiment` and
`:40` is `clim_project: cmip6`; `pixi.toml:185` pins `tree-check` to that
config. `dev/scripts/prune_series_cache.py:56-69` indexes `my["clim_project"]`,
`my["models"]`, `my["scenarios"]`, `my["members"]` with no fallback.
`scripts/plot_workflow_dag.py:116` uses a `.get()` chain, and its own docstring
says "A WF3 config carrying no experiment name yields the plain `_wf3_` stem" —
which after the split becomes the *only* outcome.

Verified-safe raw-T1 readers, for the §12 inventory:
`dev/scripts/prune_climate_store.py:62,99`,
`dev/scripts/prune_config_snapshots.py:196`, `dev/scripts/region_bbox.py:105`,
`dev/scripts/scaffold_project_tree.py:82` — all read `project`/`shared` only.

**risk-2.** Parse-time set: `build_model.smk:181-197` (`model_build_config`,
`waterbodies_config`, catalogs, `output_locations`, `observations_timeseries`)
→ `referenced_inputs_for_digest` (`provenance.py:599-627`) →
`CONFIGURATION_INPUTS_DIGEST` (`:198-203`) → rule 1.01's params
(`build_model.smk:484`) and every journal line (`:1302`). Record-time set:
`copy_config_files.py:539-577` → `_snapshot_references` →
`_write_run_record`'s `configuration_inputs_sha256` (`:457-459`). The two agree
today because `_reference_identity` (`provenance.py:563-591`) prefers `sha256`
over `git_blob` for every descriptor that has one — a deliberate deviation its
docstring explains. I did not execute a run to confirm the equality
empirically; if the two already differ, risk-2 becomes "say which of the two is
authoritative" and the missing parse-time retrigger stands on its own.

**risk-4.** `guarded_sections = ("project", "shared.basin",
"workflows.build_model", "workflows.analyze_projections")`
(`run_stress_test.smk:332-335`); `CONFIG_PROJECTION` is derived from it
(`:355-361`); `guarded_sections_digest` (`:340-352`) hashes
`config.get("workflows", {}).get("build_model")`. Anything merged into that
section is run identity.

**risk-6.** `compare_project_consistency`
(`check_project_consistency.py:150-184`) compares VALUES, not bytes, so a
mis-split that preserves shape but changes a value is invisible to the snapshot
machinery and surfaces only as different numbers (WF1/WF2) or as a freeze
refusal (WF3).

**risk-16.** Chain, each link cited: T1 bytes change → `build_model.smk:535`
(`prepare_spatial_maps`, non-`ancient`) re-runs and cascades → WF1 rewrites
`config/runs/snake_config_build_model.yml` with composed content →
`wf1_snapshot_digest = file_digest_or_absent(wf1_snapshot_path)`
(`run_stress_test.smk:392-394`) moves → rule 3.01 re-fires (design §15.4 step 5
says so) → the fresh `.project_consistency_ok` sentinel is a BARE input of 3.09
(`run_stress_test.smk:837`) and 3.10 (`:858`), the split
`check_project_consistency.py:195-199` states explicitly → 3.10's
`weathergen_config.yml` feeds 3.11 → realizations regenerate.

**risk-8.** `grep -c '"workflows":' tests/` → 23 occurrences in 9 modules:
`test_check_project_consistency.py`, `test_experiment_allocation.py`,
`test_plot_workflow_dag.py` (9), `test_prepare_cst_parameters.py`,
`test_prepare_weagen_config.py`, `test_semantic_tree_diff.py` (4),
`test_shared_provenance.py` (4), `test_snapshot_project_tree.py`,
`test_suggest_experiment_name.py`.

**risk-13.** `yaml.safe_load` over all four `test_case/snake_config_*.yml` and
`config/templates/snake_config.template.yml` returns top-level
`['project', 'shared', 'workflows']` in every case; `grep -n reporting` over the
same set matches only `config/templates/snake_config.template.yml:210` →
`#reporting:`.

## Open questions (§19), briefly

- **Q1** (`config_path` spelling) — no risk either way. If risk-15 is resolved
  by allowing the key's absence, the name matters even less.
- **Q2** (declared cross-section reads as a checked contract) — risk-3 raises
  its value: with D-9.3 unable to fire for three of four entry points,
  `guarded_sections` carries more enforcement weight than §9's "Coverage,
  honestly" paragraph credits it with.
- **Q4** (wrapper preflight) — see risk-15. Deferring it is defensible in
  general and weakest exactly at the migration, which is when every project has
  four brand-new path references that have never been resolved once.

## What I could not judge

- Whether `dev/tasks/` already carries a board note or watch-item covering any
  of the raw-T1 consumers in risk-1 — the brief barred the run directory's
  other files and I did not sweep `dev/tasks/`. No cross-check against a ledger
  or the other lenses was possible.
- Whether the CST-API backend constructs `workflows.<name>` sections in a shape
  risk-4 or risk-17 would affect. §15.1 rules it out of scope by standing
  policy, which I accept; I note only that "the population this breaks is small
  and known" is an assertion about a repository this review cannot see.
