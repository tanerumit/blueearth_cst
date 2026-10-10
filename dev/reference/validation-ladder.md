# Validation ladder — tiering, configs, and CI

The ladder table lives in `AGENTS.md` § Validation ladder. This file holds what does not fit there: how the tiers are drawn, which config a run takes, and how to read CI.

## Planning and reusing verification

For every new or revised task design, map each acceptance claim to a check and its input case before
scheduling runs. Reference the live ladder instead of copying a fixed list of gate commands into the
design. Record the tested commit, command, result, environment, input/config identity and output root in
the existing task evidence. A command's successful exit does not discharge claims it never checked.

- A passing `test-full` satisfies `test-fast` on the same candidate and environment. Do not schedule
  both as final gates. A fast run before full is optional early feedback, not another acceptance duty.
- When all-five `test-e2e` is owed, use its fresh rapid output root for affected-workflow inventory,
  caption, visual and numerical checks. Do not also require a standalone fresh rapid run with the same
  inputs and behavior. A development smoke run remains useful for diagnosis.
- Keep additional cases only for distinct claims: single-model availability, optional products,
  P0/lab parity, baseline numerical checks and synthetic edge cases. State the coverage added by each.
  An execution pass does not replace a numerical oracle or visual inspection.
- Complete synchronization and executable edits before final gates. Reuse earlier passes only after
  comparing the tested candidate with the final candidate. Exact tree equivalence permits reuse;
  otherwise classify every changed path, including test-read documentation and transitive inputs.
  Recheck the affected coverage. Environment or input changes invalidate dependent evidence.
- At landing, an executable `task-land --verify` may verify recorded passing evidence and candidate
  equivalence instead of rerunning expensive gates. It must fail for missing evidence, failed/skipped
  required checks, or unclassified changes. After an equivalent merge, prove tree equality and ancestry;
  do not repeat gates. Push retains the CI and delta checks in `AGENTS.md`.

Use a compact table in task designs:

| Claim | Check | Input case / output root | Extra coverage or reuse |
|---|---|---|---|
| Workflow execution | Applicable live-ladder gate | Fresh rapid root | Supplies shared outputs |
| Product completeness | Inventory/caption checks | Same fresh root | No second execution |
| Numerical equivalence | Independent oracle | Same inputs or named reference | Distinct scientific claim |
| Conditional behavior | Focused test or execution | Named alternate case | State what rapid misses |

Completed design and review records describe the gates actually used. Their historical command lists
do not prescribe future work; new tasks use this maintained guidance and the live `AGENTS.md` ladder.

## Pytest temporary directories

Bare `pytest` and Pixi test tasks load the test-directory plugin from `tests/conftest.py`.
Each invocation creates `.tmp/pytest/run-<unique-id>/` in its own checkout; xdist places worker
directories beneath that run. The reusable cache lives in `.tmp/pytest/cache/`. Concurrent runs
never clear one another's default fixture directories. This covers `tmp_path`, `tmpdir` and
`tmp_path_factory`, not application calls to Python's `tempfile` module.

On Windows, the plugin creates these directories with inherited workspace ACLs. Python's `0700`
directory mode installs a user/admin-only ACL that denies the restricted sandbox token access;
moving that directory alone does not fix the failure. POSIX retains pytest's private permissions.
The adapter uses pytest's internal factory integration; verify the fixture test with `-n 2` after
pytest upgrades. Existing inaccessible temporary directories are left untouched.

Default run directories remain available for debugging; the usual three-run retention count does
not prune these unique roots. Review `.tmp/pytest/run-*` after finishing a task and remove only its
completed runs, after verifying their resolved paths remain inside this checkout's `.tmp/pytest`
and contain no links. Never clean an active run or delete the shared parent during testing.
`--basetemp <path>` remains an explicit override with pytest's destructive semantics: pytest clears
that exact directory before use. Give concurrent invocations different paths. Tests that require a
path outside the checkout must explicitly choose one; ordinary fixtures now live inside it.

## Tiering

`test-fast` deselects the `workflow_contract` and `process_isolation` markers. Those tests each spawn a fresh Python process and build a Snakemake DAG, so they cost around fifty times what an ordinary test costs: they are roughly 2% of the suite and the large majority of its runtime. Count them with
`pytest tests/ -m "workflow_contract or process_isolation" --collect-only -q` rather than trusting a number written here — it drifts every time a rule gains a contract test.

When the fast gate is owed, run the whole cheap tier rather than hand-picking relevant files. A passing
full suite covers that tier too; do not rerun fast merely to satisfy a second gate label.

`test-fast` runs its workers in parallel (`-n auto --dist loadfile`). Keep `loadfile`: it puts every test in a file on one worker, which is what contains module-level state — a test that stubs a library process-globally stays confined to its own file. `--dist load` distributes per test and would break that. The floor is the per-worker import cost, so adding cores past a point buys nothing.

`test-contract` stays serial. Those tests share a `project_dir` and take `.snakemake` locks, so parallelising them needs each group proved independent first.

**`test-fast` is the local gate, including before a push.** CI runs the unmarked `pytest tests/` on ubuntu and windows from the push itself, so a local `test-full` re-proves on one platform what CI is about to check on two, for roughly ten times the wall-clock of the cheap tier. What it buys is knowing before the push rather than a quarter of an hour after it — worth paying only when a bad push is expensive to undo.

**A push gates the unpushed delta, not the session.** `origin/main` passed `test-fast` before it was pushed and CI ran on it, so `origin/main..main` is the only untested surface. That is why the push row skips work in two cases. The first is a merge-then-push: `task-land --verify` already ran `test-fast` on the candidate and proved `main` has the same tree. Board-closure commits after it add only exempt paths, so a second run re-tests content already covered: the `8508645b` push differed from its tested candidate `1cb444a9` by one `dev/tasks/` note. The second is a delta of push-exempt paths, where the ruff hook is enough. Both shortcuts assume `origin/main` is green: a red or unread CI run voids them. The exempt list in `AGENTS.md` was drawn from the test tree on 2026-10-05: `dev/scripts/` and `dev/records/` are imported or read by tests, `test_activation_links.py` resolves every link under `dev/reference/`, and `config/templates/` and `docs/notebooks/` are read directly. Re-derive it by grepping `tests/` before widening it. A label-based rule would have been wrong the same day: `74ad4310`, a "conform `dev/`" chore landed after the `8508645b` push, also changed `.github/workflows/ci.yml`, `README.md` and `test_case/project_config_baseline_linux.yml`.

Run `test-full` at batch landing when the combined diff changed shared runtime/configuration contracts or a `script:` signature, and before a milestone seal. Individual tasks use focused checks and separate commits; do not repeat the full gate per task. Those are the cases where meeting a failure on two platforms at once costs more than the wait.

Between merges and the next push, a `workflow_contract` regression can sit on local `main` across several branches, so bisect across all of them. Reading the CI run after each push is what bounds that window. `ci.yml` cancels an in-flight run when the same ref is pushed again, so after quick successive pushes the latest run is the one to read; it covers the whole tree.

State gate costs as orders of magnitude, never in seconds. The marker names and the test count are durable; the clock is not.

`.testing-policy.yml` pins `scope: rapid`, and `auto_push: false` keeps the push a deliberate decision.

## Recording gates and verifying landing

Use `dev/scripts/verify_landing.py` instead of writing a task-specific landing verifier. Its `record`
command executes one explicit gate, captures a fresh log and records the committed tree, Python
executable/version/platform, lock-file identity and named input-file hashes. Run it on a clean
candidate after committing executable changes. Evidence and logs belong in project scratch; retain
only needed evidence in the existing task home before scratch cleanup.

```powershell
pixi run python dev/scripts/verify_landing.py record --evidence .tmp/scratchpad/gates.json --gate test-fast --log .tmp/scratchpad/fast.log -- pixi run test-fast
pixi run python dev/scripts/verify_landing.py verify --evidence .tmp/scratchpad/gates.json --require-gate test-fast
```

Use the verify command as `task-land --verify`; it runs no recorded gate commands. Repeat
`--require-gate` for every required gate and `--input` during recording for external config/input files
whose identity matters. A passing `test-full` satisfies a required `test-fast`. Required execution or
numerical gates remain separate names. Recording another gate must preserve candidate, environment
and input identities; use a new evidence file after a meaningful change.

The helper rejects failed/skipped required gates, missing or altered logs, changed named inputs,
changed recorded environment and unclassified tree differences. It measures Python and lock-file
identity, not every installed binary, upstream service or dataset: name additional input/version
files with `--input` and invalidate evidence if unrecorded dependencies change. Hashing a catalog file
does not hash the data it points to. Select required gates from the live ladder before verification;
the helper does not infer blast radius or schedule coverage.

Only after reviewing each changed path may `--allow-path exact/path.md` permit an intervening
Markdown change. Do not allow test-read documentation without rechecking the affected coverage.
Code changes require fresh evidence. No wildcard exclusions are supported.

A zero exit records command success, not scientific acceptance or proof that every required test ran.
Inspect the log for required skips and use `--skipped` when a required check did not execute; never
reuse that gate as passed. Keep visual acceptance and numerical difference classification in the task
record. Human attestation remains necessary for those claims.

## Choosing execution coverage

Use one final software gate: fast normally, full when the live ladder escalates it. For Python edits,
run scoped lint/format checks before each commit and repository-wide lint/format once before final
batch verification. A later Python edit invalidates the relevant final check; a commit or gate label
alone does not. Focused tests remain the development loop.

All-five execution is required for shared runtime/configuration, orchestration, cross-workflow
interfaces, releases and milestone seals. Classify by behavior and callers, not merely directory:
shared plotting changes that affect only terminal figures remain render/inspection work. A shared
runtime helper or configuration change affecting several workflows takes the all-five gate.

For behavior confined to one workflow, search callers and output consumers, then execute that workflow
and the consumers affected by the changed contract with rapid inputs. State the coverage and omitted
workflows in the task evidence. Preserve owned wrappers: WF3 uses a WF3-only project configuration with
`run_workflows.py`; WF4 uses `simulate_system.py` or the all-workflow runner. For figure-only changes,
render and inspect affected figures. Changes to calculations still require numerical acceptance.

This reduces routine integration coverage; the all-five release and milestone gates retain the whole
pipeline check. Escalate a confined change when focused verification exposes wider breakage.

## The end-to-end run (`test-e2e`)

`pixi run test-e2e` is the automated all-five execution check:
through `scripts/run_workflows.py`, on the rapid config, in a fresh temporary
project root. It needs what CI cannot provide (the data mirror, juliaup Julia,
`weathergenr`, network for WF2), so it is a local gate, and the ladder in
`AGENTS.md` says when it is owed: a batch that changes what a workflow runs, a
release, a milestone seal.

It writes nowhere under `test_case/`, so it cannot disturb the baseline tree, and
nothing an earlier run left behind can make it pass. It skips by name when a
prerequisite is missing; a skip is no evidence, so read the reason (`-rs` is on).

Until 2026-10-04 (t2610041227) this layer was three per-workflow smoke tests
behind the same flag, and nothing scheduled them, so they drifted until none
could test anything: two pointed at pre-R9 paths, one force-rebuilt the standing
baseline tree, and one drove WF3 with bare Snakemake. An opt-in test with no
trigger decays silently; the ladder row is its trigger.

## Which config to run

Default to `project_config_rapid.yml`. Reach for `project_config_baseline.yml` only when the run's numbers are the point.

| Config | `project_dir` | Run it for |
|---|---|---|
| `project_config_rapid.yml` | `test_case/test_rapid` | anything you want to watch EXECUTE — a rule you edited, a DAG check, a WF3 smoke run, a figure render |
| `project_config_baseline.yml` | `test_case/test_local` | recording or checking `dev/baseline/manifest.json`, `tree-check`, a milestone seal, any number you will quote |
| `project_config_wf2_fast.yml` | `test_case/test_dev` | WF2 code iteration only — 2 series, and it drops `st_0` |

**Rapid's advantage is the GRID, not the years.** Both configs now simulate nine years (2046–2054) and generate the same ~44-year series — `t2608222155` moved the baseline off 17 years around 2078 on 2026-09-07. What is left is 10 members against 14: rapid's 2 × 2 grid plus `st_0` against baseline's 2 × 3.

This paragraph claimed "~2.6× less wflow time and ~1.7× less weather generation" until that item MEASURED it, and both halves were wrong. Per-member wflow cost is about `16 s + 0.59 s × simulated years`, so a 17-year member spent about 10 s simulating and about 16 s starting up — the window was worth ~18%, not 50%, and the measured whole-workflow gap was about 1.2×. Weather generation went the other way entirely: rapid's `3.10_generate_weather_realizations` took 45.8 s against baseline's 29.0 s. **The cost here is process startup**, not simulated years: the first member of a batch costs about 80 s more than the rest (Julia JIT plus the cold SBM path), which at three batches plus wf1's standalone run is roughly 320 s — a quarter of the run — spent starting Julia.

To change the generated-series length, change the END of `simulation_window` rather than its start: `compute_nr_years` anchors the series at the end of `climate.window`, so it spans that year → `simulation_window.end` (plus a two-year pad). (`C-67` folded the former `horizontime_climate` + `run_length`/2 into that one declared year.) Whatever you set must stay inside a `future_windows` entry in the analyze_projections file — the alignment is computed independently of both keys, so a missed edit misaligns silently.

Rapid is cheap, not narrow. It gets `st_0`, which is what the two class-C month indicators derive from — and since `C-69` every config does, so this is no longer a way a config can quietly give up 2 of 11 `q` metrics — and it keeps two CMIP6 models, since a one-model config never runs the ensemble reduction. A config that gives up coverage must say which, as `wf2_fast` does.

Record the baseline from `project_config_baseline.yml` and nothing else; never point `check_baseline.py` at the rapid tree.

`check` exits **0** (targets match), **1** (the tree differs) or **2** (*nothing
was compared* -- an empty scope, or a fixture it cannot resolve). Treat 2 as "no
evidence", never as a pass: `--workflow generate_scenarios` declares no
non-figure target, so it reaches 2 by construction.

**The baseline manifest is BEHIND the baseline config, on purpose (`t2608222155`).** On 2026-09-07 the baseline set moved to a nine-year `simulation_window` (2046-2054) and the matching `mid` horizon; `dev/baseline/manifest.json` was deliberately NOT re-recorded, because the saving is 4-8% and a re-record costs a full run that repays after 10 to 25 gates.

**The standing tree is not an R12 migration reference.** It still contains the pre-2026-09-07 run and its matching manifest. Re-execution changes the configured years and projection horizon; R12 also changes scenario/metric paths, keys and ownership. Use the separately captured fresh P0 reference and GF-9 crosswalk for R12 acceptance. Do not interpret agreement between the old standing tree and its old manifest as evidence about the current configuration, or re-record it before scientific acceptance.

## Read the CI run after you push

Install the pre-push hook once per clone — cloning does not install it:

```bash
git config core.hooksPath .githooks     # runs the two ruff checks, ~2 s
```

Read the run regardless. The hook cannot see platform-specific failures, and a green local suite is no evidence about the ubuntu leg — the only place linux-64 is exercised.

`gh` resolves to `upstream` (`Deltares/blueearth_cst`) in this clone, not `origin` (`tanerumit/blueearth_cst`, where CI runs), so a bare `gh run list` queries Deltares, exits 0 and prints nothing. Point it at origin once per clone:

```bash
gh repo set-default tanerumit/blueearth_cst   # writes remote.origin.gh-resolved
```

In a script that must not depend on local config, pass `--repo tanerumit/blueearth_cst` explicitly, or use the API:

```bash
# the latest run, whatever branch it was on
gh api "repos/tanerumit/blueearth_cst/actions/runs?per_page=1" \
  --jq '.workflow_runs[0] | "\(.head_sha[0:7]) \(.status) \(.conclusion)"'

# which STEP failed, per leg — separates a lint failure from a suite failure
gh api "repos/tanerumit/blueearth_cst/actions/runs/<id>/jobs" \
  --jq '.jobs[] | "\(.name) -> \(.conclusion): " +
        ([.steps[] | select(.conclusion=="failure") | .name] | join(", "))'
```

Do not filter by `head_sha=<short sha>`: the parameter needs the full 40-character value and silently matches nothing otherwise.

### Module-level test stubs and collection order

Tests that install heavy-dependency stubs with `sys.modules.setdefault` at
module import time can silently inherit a real module or an earlier test's
stub, depending on collection order. Prefer patching the imported source
module's bindings in a fixture and restore them per test. Do not stub `dask`
with `SimpleNamespace`: pandas may lazily import it and inspect `dask.__spec__`
during collection. Keep the real pixi-installed package, or mock the specific
call site. The live examples are documented in
`tests/test_extract_historical_climate.py` and `tests/test_prepare_climate_data_catalog.py`.
