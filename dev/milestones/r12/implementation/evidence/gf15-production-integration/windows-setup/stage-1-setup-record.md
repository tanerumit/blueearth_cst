# GF15 production Stage 1 — isolated Windows setup record

Date: 2026-09-14. Session: `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: accepted
adapter design D5/D7/D8 and the [Stage 1 brief](../../../gf15-production-stage-1.md),
under the owner's 2026-09-14 Windows-only sequencing override.

This record completes the **setup** half of Stage 1. The snapshot half was
accepted separately by the [integrity review](../snapshot-integrity-review.md).
An independent reviewer re-executed every load-bearing claim below and accepted
it with findings; the [verdict](setup-review.md) records what was reproduced,
the one prose error it caught, and what the evidence does not establish. The
corrections it required are applied in place here.
No fit, workflow run, Wflow/Julia invocation, adapter edit or repository
dependency change was performed. Measured facts only; nothing below is a
scientific adequacy claim.

Machine-readable evidence beside this file: `setup-result.json` (identities and
both stage projections), `artifact-provenance.json` (PyPI versus conda-forge
comparison), `manifest.diff` (the one-line manifest delta),
`import-qualification.json` (actual imports),
`stage-environment-shared.json` (the shared production environment's projection,
the other side of the equivalence claim), `lock-solve.txt` and `install-output.txt` (the
solver run, including the both-platform timings), and
[`../materialized/retained-config-comparison.json`](../materialized/retained-config-comparison.json)
(materialized-versus-retained config deltas).

## Pixi executable — resolved

The [discovery record](../stage-1-readiness.md) reported "Pixi executable remains
unresolved". That is now closed. The installed executable is

```text
C:/Users/taner/AppData/Local/pixi/bin/pixi.exe      # pixi 0.70.2
```

Discovery checked `C:/Users/taner/.pixi/bin/pixi.exe`, Cargo, Scoop and WinGet
locations; the actual install is under `AppData/Local/pixi/bin`, which was not
among them. A second executable exists at
`.../gf15-production-integration/windows-environment/tools/pixi.exe` (**pixi
0.80.0**), downloaded by the earlier attempt. All work below used the installed
0.70.2, because that is the version a normal repository run resolves; the
vendored 0.80.0 was only version-queried.

`PIXI_PROJECT_MANIFEST` is set in this shell to the primary checkout's manifest
and pixi warns about it. Every command below passed `--manifest-path` explicitly
and cleared that variable, so no invocation resolved the primary or this
worktree's manifest.

## Isolated root and solve

Qualified isolated root, outside the repository tree and outside disposable
scratch:

```text
C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/windows-environment-pypi
```

It holds a copy of the repository `pixi.toml` with one added line, the
solver-generated `pixi.lock`, and `dev/scripts/pixi_activate.bat` (required by
`[target.win-64.activation]`). The shared `.pixi` of this worktree and of the
primary checkout were never written to; `git status` over `pixi.toml`,
`pixi.lock`, `blueearth_cst`, `scripts` and `config` is clean.

The manifest delta is exactly one line, in `[pypi-dependencies]`:

```toml
lmoments3 = "==1.0.8"
```

Executed commands (PowerShell, `PIXI_PROJECT_MANIFEST` cleared):

```powershell
& $Pixi lock    --manifest-path $Iso\pixi.toml -v
& $Pixi install --manifest-path $Iso\pixi.toml --frozen
```

The solve was first performed in session scratch
(`.tmp/scratchpad/2026-09-14_1600/gf15-stage1-setup/full-solve`) and the accepted
manifest/lock pair copied to the durable root, which was then installed
`--frozen`. Scratch is disposable; the durable root and this record are not.

**Both platforms solved.** `pixi lock` resolved the pypi requirement for
`win-64` **and** `linux-64` (722 ms each), updating the lock with
`+ (pypi) lmoments3 1.0.8`. This discharges D7's "solver-generate `pixi.lock` for
win-64/linux-64" on the solver side. It is **not** a Linux qualification: nothing
was installed or executed on linux-64, which stays deferred per the owner's
ruling and remains outstanding on the R12 checklist.

Identities: qualified `pixi.toml` SHA-256
`d2afe7f99ddf0d2fb5ed165476dcb7a7022402024f27bff332467d11ce1f04ad`; qualified
`pixi.lock` SHA-256
`43d11fc5297160152d0c728f9c9e4d4816c816b2876fc75cb3c3d210f437ffc6`. The
repository's own `pixi.lock` is unchanged at
`ca888ef1c4547ee0624fc4da319de87fd9284418b2fbe16171118bc8f7b64041`.

## D7 dependency identity — satisfied

The generated lock records the pinned wheel, byte for byte:

```text
- pypi: https://files.pythonhosted.org/packages/28/a8/88ba989f510c5e0d8889fbc8141ff0ae307dcf743baa2385ebaa6169b43c/lmoments3-1.0.8-py3-none-any.whl
  name: lmoments3
  version: 1.0.8
  sha256: 984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e
```

which equals D7's pinned wheel SHA-256. The installed package in the qualified
environment reports version 1.0.8 with both guarded source digests matching D7:

| File | Installed SHA-256 | D7 |
|---|---|---|
| `__init__.py` | `1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2` | match |
| `distr.py` | `f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee` | match |

### Placement finding — the earlier attempt used an unqualified artifact

The superseded `windows-environment/` root added `lmoments3 = "==1.0.8"` to
`[dependencies]`, so it resolved the **conda-forge repack**
`lmoments3-1.0.8-pyhd8ed1ab_1.conda`
(`9a803860ac00390b94b26491129c67f3ed3f041cbc81b798e5e62dfd5088d08e`) rather than
the pinned wheel. D7 pins a wheel SHA-256 and states that "a same-version repack
with different source is unqualified", so that placement does not qualify and is
superseded by this one. `[pypi-dependencies]` is the correct home.

Measured, for the record and for any future review of D7: all six `.py` files of
the two installs are **byte-identical**, so the conda repack would have passed
the two source-hash guards while failing the wheel pin. This is an observation.
Changing what D7 pins would need scientific review and is not proposed here.

## Numerical and native closure — production-equivalent, measured

The metric-stage roots are `numpy, pandas, scipy, xarray, xclim, netCDF4,
pyproj, PyYAML` (`metric_plan.current_metric_request`). Running the repository's
own `content_identity.stage_environment` over those roots:

- in the qualified isolated environment, and
- in the shared production environment (`.pixi/envs/default`, read-only),

produces **identical output**, including both `locks` digests
(`installed-conda-dependency-records`
`9a9414c9d7a9561e50a63b96e212367293d4e82b0b2a1aee895b3705d1a74d02`,
`installed-python-distribution-metadata`
`9ba17384828e2d703cd2f5eaa1e64e9d7160410b51b79f598ef238ea5f4e37cb`). The
isolated environment is therefore a production-equivalent closure, not a
version-matched approximation. Both record 220 projected packages, with build
strings: `conda:numpy 2.4.6+py312ha3f287d_0`, `conda:scipy
1.18.0+py312h9b3c559_0`, Python 3.12.13 conda-forge MSC v.1944 AMD64,
`Windows-11-10.0.26200-SP0`.

Adding `lmoments3` to the root list changes the projection by exactly one entry,
`python:lmoments3: 1.0.8`, and moves `installed-python-distribution-metadata` to
`edf9df1c4a5680660ef22763448b0025cb48eb9f59388b25c1494d5e273a8b8c` while
`installed-conda-dependency-records` is unchanged — so a candidate metric request
gets a distinct identity, while merely *installing* the package without adding
the root does not perturb any other stage. That is the D5 property, and it is now
measured rather than assumed.

A mechanism worth recording, because it reinforces the placement finding above:
the PyPI install writes **no** `conda-meta/lmoments3*.json`, which is why only the
python-metadata digest moves. The superseded conda repack root **does** carry
`conda-meta/lmoments3-1.0.8-pyhd8ed1ab_1.json`, so under that placement lmoments3
would also enter the conda closure and move the conda digest. Placement therefore
changes the identity projection independently of the wheel pin. Both states were
observed directly.

The equivalence claim is precise: identical **as projected over the metric-stage
roots**. The projection follows those eight roots and their reachable
dependencies; packages outside that closure are not covered by it.

### Imports actually execute

`stage_environment` reads `importlib.metadata` and imports nothing, so the
projection alone is metadata evidence. It was therefore backed by a real import
check in the durable environment, invoked exactly as the recorded old argv
invokes it — bare env `python.exe`, no `pixi run`, no activation scripts.

All eight metric-stage roots plus `lmoments3` and `snakemake` import
successfully, each resolving inside the qualified root's `site-packages`, and
`scipy.optimize`, `scipy.stats` and `numpy.linalg` load — the native paths that
Windows conda DLL loading would break first. `import-qualification.json` records
each module's resolved file and version. Importing is not fitting; no estimator
was called.

**Invocation form and ambient environment.** The discovery record sketched a
`pixi run --manifest-path …` command. The form used here and written above is the
bare environment `python.exe`, because that is what the recorded old argv used
(`operations-dedicated-reuse.json`, `commands[label=metrics-reuse]`), and Stage 3
compares against that run. A bare invocation runs no `[activation.env]`, so
`HDF5_USE_FILE_LOCKING` and the gcsfs variables come from the invoking shell
rather than from this root. `HDF5_USE_FILE_LOCKING=FALSE` was present ambiently
during this check. **The old run captured no environment block** — the retained
record holds argv, exit code, log and hashes, and no environment — so the old
run's ambient variables are *unknown*, not matched. Stage 3 must set them
deliberately and record what it set, or invoke through `pixi run` and record that
instead; it must not assume parity with the old run here.

This is a Windows result. The PyPI-versus-conda-forge numeric closure that the
study venv left open is **not** settled by it: this environment takes NumPy and
SciPy from conda-forge, as production does, and takes only lmoments3 from PyPI.
Cross-platform parity remains Stage 2's E7 obligation and Linux remains
unexecuted.

### Finding for Stage 2 — the projection carries no source hashes

`stage_environment` projects versions, build strings and two metadata digests.
It carries **no module source hashes**; per-distribution METADATA digests and two
aggregate digests are as far as it goes.

This is an observation about `stage_environment`, not an open Stage 2 decision —
a first draft of this record overstated it as one. D5 already prescribes the
remedy: a proposed `resolve_metric_environment()` in `metric_plan.py` "freshly
calls existing `stage_environment` … then adds D7's observed and verified
lmoments3 version/source hashes". The source-hash binding is therefore additive
at the resolver. The measured candidate projection shows the existing projection
*can* represent D7's version (`python:lmoments3: 1.0.8`), so the master brief's
`content_identity.py` conditional — and the broader validation gate that comes
with it — is **not** triggered by this finding. Independent review confirmed this
reading.

### Hazard for Stage 2 — `pixi.lock` line endings

The repository's tracked `pixi.lock` is checked out **CRLF** (17,812 CRLF, 0 LF)
while `pixi lock` writes **LF**, so a raw byte comparison of the working-copy file
before and after a regeneration differs on every line.

> **Corrected 2026-09-14, during Stage 2 commit 1.** This paragraph originally
> predicted that Stage 2 would therefore see a whole-file **`git diff`**. That was
> wrong. `.gitattributes` puts `pixi.lock` under `* text=auto`, so the committed
> **blob is LF** (verified: 0 CRLF, 17,812 LF) and only the working copy is CRLF.
> Git compares against the normalized blob, so the regeneration produced an
> 18-line diff — the two per-platform environment entries and the package record —
> and nothing else. The byte-level asymmetry behind `t2608301524` is real and is
> why the shipped report asset is pinned `-text`; the `git diff` consequence
> asserted here was not. Raw-byte comparisons of working-copy files remain
> platform-sensitive; `git diff` does not.

Solve drift is the other half of the same obligation, and it is the reviewer's
F3. This qualification binds lock `43d11fc5…`, not the lock Stage 2 generates in
the repository; a fresh solve there may move packages outside the eight-root
closure, and the equality measured above is scoped to those roots and their
reachable dependencies.

> **Discharged 2026-09-14, during Stage 2 commit 1.** The regenerated repository
> lock is **byte-identical** to the qualified lock — the same SHA-256
> `43d11fc5297160152d0c728f9c9e4d4816c816b2876fc75cb3c3d210f437ffc6`, with the
> two manifests differing only by the three explanatory comment lines added above
> the dependency. The qualified environment is therefore the environment this
> lock produces, and the projection equality transfers by identity rather than by
> re-measurement. Had the digests differed, a fresh install and a re-run
> comparison would have been required instead.

## Materialized metrics operation, config and command — unexecuted

Retained under
[`../materialized/`](../materialized/): `project_config_gf15_metrics.yml` and
`project_config_simulate_system.yml`, copied in meaning from the retained P3
`metrics-reuse` configs and differing from the driver's 2026-09-14_0010 drafts
only in naming a durable working-copy home.

"Copied in meaning" is checked, not asserted. The retained originals are
`.../p3-operations-dedicated-reuse/project_config_metrics.yml` and
`metrics-simulation.yml`; both re-hash today to the values the P3 record
registered, `27b5463a3b601f5f6c5fe481e23373d5aa84217973382ebdcff50e3ba242c218`
and `474bc8444fb04b943ef43f67466e94e3dbfbde1bbb5034f6eee834d6c41f9433`. A parsed
key-by-key comparison against the materialized pair
(`retained-config-comparison.json`) finds:

- workflow settings: **zero** differing keys — `operation`, `metrics`,
  `experiment_name` and the collection anchor are unchanged;
- project config: **exactly two** differing keys — `project.project_dir`, moved
  to the durable working-copy home, and `workflows.simulate_system.config_path`,
  written as a sibling relative path (which resolves against the project file's
  own directory to the same settings content). `max_subbasins`, region,
  resolution, climate window, outvars, catalog and every disabled-workflow
  stanza are unchanged.

`simulate_system.operation` accepts exactly `simulate-and-metrics` and
`metrics-only` (`blueearth_cst/experiment/simulation_runner.py`). Read from
source, `metrics-only` accepts the target `metrics` or one selected
`metric_sets` file; `all`, `responses` and `scenarios` are refused. `--dry-run`,
`--forceall`, `--notemp`, `--keep-going`, `--rerun-incomplete`, `--unlock`,
`--printshellcmds` and five value switches pass through; anything else, and any
second target, is refused. **No `--metrics-only` flag exists and none is
introduced.**

Parsing the materialized project config through `simulation_settings` (read-only;
no DAG, no project access) returns `operation: metrics-only`, `metrics: [q, gwr]`,
`experiment_name: p3_final` and the intended `project_dir`.

The documented Stage 3 command, resolved and still unexecuted:

```powershell
& "C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/windows-environment-pypi/.pixi/envs/default/python.exe" `
  "C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3/scripts/simulate_system.py" `
  --config "<repo>/dev/milestones/r12/implementation/evidence/gf15-production-integration/materialized/project_config_gf15_metrics.yml" `
  --cores 3 --target metrics
```

The recorded old argv it is compared against is in
`../../p3/operations-dedicated-reuse.json`, `commands[label=metrics-reuse]`.

Working-copy home for Stage 3, resolved but **not yet created**:
`C:/Users/taner/workspace/blueearth_cst-artifacts/r12/gf15-production-integration/working/p3-final-direct/project`.
Stage 3 copies it from the frozen snapshot; the snapshot is never a write target.

### Outstanding for Stage 3 — the collection anchor lives in disposable scratch

`experiments/p3_final/config/simulation.json` embeds exactly one absolute path,
`collection.manifest_path`, pointing at

```text
.../session-3/.tmp/scratchpad/2026-09-11_0010/p3-final-direct/project/scenario_collections/71bf34ef.../collection.json
```

That tree is present today (629 MB) but sits under `.tmp`, which the repository
treats as deletable. A working copy made from the frozen snapshot will still read
the collection through that scratch path. Stage 3 must either preserve the path
until the comparison is accepted or re-materialize it from the snapshot at the
same absolute location; the immutable simulation record must not be rewritten.

## Status

| Stage 1 item | Status |
|---|---|
| Complete retained comparison located and proven readable | accepted (discovery + integrity review) |
| Read-only snapshot frozen and hash-verified | accepted (integrity review, anchor preserved) |
| Pixi executable resolved | **passed** |
| Isolated win-64 setup with `lmoments3==1.0.8`, D7 wheel and source checks | **passed** |
| Both-platform lock solved | **passed (solver only)** |
| Actual numerical/native closure recorded | **passed**, production-equivalent |
| Metric-stage roots, lmoments3 and native submodules actually import | **passed** |
| Materialized configs checked against the retained originals | **passed**, two intended deltas |
| Metrics operation, config and exact CLI materialized unexecuted | **passed** |
| Isolated linux-64 setup, install and parity | **deferred by owner, outstanding** |
| Independent review of this setup record | **ACCEPTED WITH FINDINGS** ([verdict](setup-review.md)); F1/F2/F4/F5 discharged here, F3 carried to Stage 2 |

Verification budget: no pytest, lint, baseline or suite gate was warranted or run
for a setup-qualification task that changes no repository code. Full command
output was written to files, not piped.
