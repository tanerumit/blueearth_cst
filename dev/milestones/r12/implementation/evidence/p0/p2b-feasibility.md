# P0 P2b feasibility evidence

Execution date: 2026-09-10. Source checkout before this increment: `123e91b1`.
Scope: synthetic composition of row-derived wildcard constraints and ancestor
input functions, as required by accepted design §5.2. No production WF3
behavior or numerical outputs are changed by this increment.

## Readiness recheck

- `git diff --stat 4e26c2394dd002f7dfb61b1943e002866c6ca4bf HEAD -- blueearth_cst run_stress_test.smk scripts config tests pixi.toml pyproject.toml`
  returned no differences before fixture edits.
- `git merge-base --is-ancestor main HEAD` returned 0: no source resync was needed.
- `pixi run --as-is python dev/scripts/check_env.py` passed: console scripts
  present, weathergenr 2.0.0, Julia environment containing Wflow.
- `pixi run --as-is python dev/scripts/check_baseline.py record --help` passed.
  This checks CLI availability only; it records no baseline.
- Installed versions remained Python 3.12.13, Snakemake 9.6.2, pytest 9.0.3,
  HydroMT 1.3.1 and hydromt-wflow 1.0.2.

The restricted shell cannot see the installed Pixi executable. The environment
and baseline-CLI checks used the host executable with `--as-is`; no environment
installation or lock update was requested. Full disposable command logs are in
the execution worktree's `.tmp/scratchpad/2026-09-10_2046/`.

## P2b result — pass

The [fixture](../../feasibility/p2b.smk) enumerates two roots and, except in the
no-derived case, two children in memory. Both producer rules share one output
pattern. Disjoint wildcard alternations are built from those rows; the derived
rule's input function selects the exact ancestor. The empty derived alternation
uses a never-matching expression. No `ruleorder`, private API, production import
or generated scenario-table read is used.

| State | Dry-run and execution result | Retained transcripts |
|---|---|---|
| Resolvable subtree | Exactly 5 jobs: `all`, 2 `produce_root`, 2 `transform_forcing`; each child contains its named parent's content | [dry-run](p2b-resolvable-dry-run.txt), [execute](p2b-resolvable-execute.txt) |
| Missing producer subtree | Nonzero exit with `MissingInputException` naming `transform_forcing` and `forcing/root-a.txt`; no forcing outputs written | [dry-run](p2b-missing-dry-run.txt), [execute](p2b-missing-execute.txt) |
| No derived rows | Exactly 3 jobs: `all`, 2 `produce_root`; no transform and exactly the two root outputs | [dry-run](p2b-no-derived-dry-run.txt), [execute](p2b-no-derived-execute.txt) |

The test checks complete job-count tables, verifies dry-runs create no forcing
files, and compares the complete filename/content mapping after execution.
It carries `workflow_contract`, so normal fast-suite selection excludes these
Snakemake subprocess cases.

Reproduce from the repository root in the existing Pixi environment:

```powershell
pixi run --as-is python -m pytest tests/test_r12_wf3_feasibility.py -x -q --basetemp .tmp/scratchpad/<session>/p2b
```

Use a fresh scratch directory. Pytest launches each of the following from a
separate empty case directory, with `python` being its own `sys.executable`:

```text
python -m snakemake all --snakefile <WORKTREE>/dev/milestones/r12/implementation/feasibility/p2b.smk --cores 1 --nocolor --config state=<state> --dry-run
python -m snakemake all --snakefile <WORKTREE>/dev/milestones/r12/implementation/feasibility/p2b.smk --cores 1 --nocolor --config state=<state>
```

The retained transcripts preserve all output lines; trailing whitespace is
stripped and machine/workspace identifiers are replaced with `<HOST>`,
`<WORKTREE>` and `<HOST_TEMP>`. Original transcripts
and per-invocation command JSON remain in session scratch under `p2b-host-fixed/`.

## Discrimination and corrections

An initial test run failed before the fixture existed. The first restricted
Python attempt then timed out after 120 seconds; it establishes no P2b result.
The activated host run completed the dry-run and exposed an error in the test's
job-table parser: Snakemake separates the dashed column dividers with spaces.
Allowing those spaces fixed the parser; no fixture mechanism changed to obtain
the pass. The final normal run passed **3 tests in 12.72 seconds**.

Two scratch-only mutations showed that the checks discriminate:

- Changing one child's parent to the other root reduced the DAG from 5 to 4
  jobs and failed the exact job-count assertion ([transcript](p2b-mutation.txt)).
- Exchanging both parents retained all 5 jobs and successful execution but
  failed both child-content comparisons ([transcript](p2b-swapped.txt)).

Neither mutation changed the retained fixture or test. These are expected
failures establishing the check's sensitivity, not outstanding defects.

## Verification budget and results

Scope: rapid; numerical claims unaffected. Searches for P2b and the new fixture
references in `tests/` and the implementation plan confirm this increment adds
a standalone feasibility fixture and test, with no production caller.

| Check | Result |
|---|---|
| `pixi run --as-is python -m pytest tests/test_r12_wf3_feasibility.py -x -q` (fresh scratch basetemp) | 3 passed, 12.72 s |
| `pixi run --as-is pytest tests/test_cli.py --basetemp .tmp/scratchpad/2026-09-10_2046/cli-gate` | 20 passed, 48.51 s |
| `pixi run --as-is lint` after final test edit | Passed |
| `pixi run --as-is format-check` after final test edit | Passed; 292 files already formatted |

Full suite, production workflows and baseline recording were not run: this
increment changes no production behavior. Evidence is from Windows with
Snakemake 9.6.2; Linux execution remains unverified.

## Scope remaining after P2b

P2b is the synthetic prerequisite to GF-1, not its production acceptance. The
fresh-project current-carrier and final generation DAG checks remain outstanding.
The operation/target matrix and both checkpoint-composition probes also remain
outstanding. No fresh pre-change output root, config or numerical snapshot has
been created. P1 numerical call-site edits remain blocked by the accepted
pre-change snapshot prerequisite.
