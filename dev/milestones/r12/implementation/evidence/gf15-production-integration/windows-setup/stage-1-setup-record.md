# GF15 production Stage 1 — isolated Windows setup record

Date: 2026-09-14. Session: `session-3`, branch `feat/wp3-improvements`, worktree
`C:/Users/taner/workspace/.worktrees/blueearth_cst/session-3`. Authority: accepted
adapter design D5/D7/D8 and the [Stage 1 brief](../../../gf15-production-stage-1.md),
under the owner's 2026-09-14 Windows-only sequencing override.

This record completes the **setup** half of Stage 1. The snapshot half was
accepted separately by the [integrity review](../snapshot-integrity-review.md).
No fit, workflow run, Wflow/Julia invocation, adapter edit or repository
dependency change was performed. Measured facts only; nothing below is a
scientific adequacy claim.

Machine-readable evidence beside this file: `setup-result.json` (identities and
both stage projections), `artifact-provenance.json` (PyPI versus conda-forge
comparison), `manifest.diff` (the one-line manifest delta).

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
`edf9df1c4a5680660ef22763448b0025cb48eb9f59388b25c1494d5e273a8b8c`). The
isolated environment is therefore a production-equivalent closure, not a
version-matched approximation. Both record 220 projected packages, with build
strings: `conda:numpy 2.4.6+py312ha3f287d_0`, `conda:scipy
1.18.0+py312h9b3c559_0`, Python 3.12.13 conda-forge MSC v.1944 AMD64,
`Windows-11-10.0.26200-SP0`.

Adding `lmoments3` to the root list changes the projection by exactly one entry,
`python:lmoments3: 1.0.8`, and changes the `locks` digest — so a candidate metric
request gets a distinct identity, while merely *installing* the package without
adding the root does not perturb any other stage. That is the D5 property, and it
is now measured rather than assumed.

This is a Windows result. The PyPI-versus-conda-forge numeric closure that the
study venv left open is **not** settled by it: this environment takes NumPy and
SciPy from conda-forge, as production does, and takes only lmoments3 from PyPI.
Cross-platform parity remains Stage 2's E7 obligation and Linux remains
unexecuted.

### Finding for Stage 2 — the projection carries no source hashes

`stage_environment` projects versions, build strings and two metadata digests.
It carries **no module source hashes**. D5 says the resolver "binds installed
source hashes as well as versions/artifacts at planning and execution", and D7's
pre-fit guard is adapter-level. Stage 2 must therefore decide explicitly whether
the source-hash binding lives only in the adapter guard or also in the identity
projection; the latter is the `content_identity.py` conditional the master brief
flags, and it takes the broader validation gates. Nothing here presumes that
choice.

### Hazard for Stage 2 — `pixi.lock` line endings

The repository's tracked `pixi.lock` is checked out **CRLF** (17,812 CRLF, 0 LF).
`pixi lock` writes **LF**. Regenerating the lock in the repository will therefore
rewrite every line of the file, and a later CRLF checkout re-keys it back; this
is the same mechanism already tracked as `t2608301524`. Stage 2 must expect a
whole-file lock diff and must not read it as a dependency change.

## Materialized metrics operation, config and command — unexecuted

Retained under
[`../materialized/`](../materialized/): `project_config_gf15_metrics.yml` and
`project_config_simulate_system.yml`, copied in meaning from the retained P3
`metrics-reuse` configs and differing from the driver's 2026-09-14_0010 drafts
only in naming a durable working-copy home.

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
| Metrics operation, config and exact CLI materialized unexecuted | **passed** |
| Isolated linux-64 setup, install and parity | **deferred by owner, outstanding** |
| Independent review of this setup record | **outstanding — gates Stage 2** |

Verification budget: no pytest, lint, baseline or suite gate was warranted or run
for a setup-qualification task that changes no repository code. Full command
output was written to files, not piped.
