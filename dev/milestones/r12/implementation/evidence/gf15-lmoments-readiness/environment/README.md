# Isolated Stage 1 environment

Created on 2026-09-12 after the owner instructed `continue to Stage 1`.
The shared Pixi environment, its locks and production code are read-only.
This environment supports readiness controls, not the full qualification matrix.

The interpreter is an isolated `venv --copies` made from the existing
conda-forge Python 3.12.13. Its standard library/base executable remain supplied
by that recorded base installation. `effective-environment.json` identifies the
base build, executable digest, effective packages, module paths and lmoments3
source digests. NumPy/SciPy here are PyPI wheels, not an assertion of binary
identity with the predecessor conda environment.

Runtime pins: Python 3.12.13, NumPy 2.4.6, SciPy 1.18.0, lmoments3 1.0.8.
Pytest 9.0.3 is the existing test-runner version; its five dependencies are
also pinned by wheel hash in `requirements.txt`. The base bundled pip is
recorded in the effective package list. No global installation was changed.

All nine wheels were downloaded from `https://pypi.org/simple` with
`--only-binary=:all: --no-cache-dir`. Before installation, the lmoments3 wheel
was checked against approved SHA-256
`984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e`.
The local install then used `--no-index --require-hashes`.
`wheels.json` records every filename, size, digest and source index;
`install-report.json` preserves the installer report. Wheels and environment
are disposable and are not committed.

## Executed commands

Run from the repository root in PowerShell. Paths below identify this session's
scratch environment; recreate in a new absent directory, not over an existing
environment or evidence namespace.

```powershell
& .pixi/envs/default/python.exe -B -m venv --copies .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv
& .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe -m pip download --index-url https://pypi.org/simple --only-binary=:all: --no-cache-dir --dest .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/wheels numpy==2.4.6 scipy==1.18.0 lmoments3==1.0.8 pytest==9.0.3
# The wheel digest check and complete hash-pinned requirements creation occurred here.
& .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/venv/Scripts/python.exe -m pip install --no-index --find-links .tmp/scratchpad/2026-09-11_0010/gf15-lmoments-readiness/wheels --require-hashes --report dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/install-report.json -r dev/milestones/r12/implementation/evidence/gf15-lmoments-readiness/environment/requirements.txt
```

To reproduce later, first verify the base interpreter is exactly Python 3.12.13,
create a fresh venv, then download from PyPI using the committed
`requirements.txt` with `--require-hashes --only-binary=:all:` and install those
local wheels with `--no-index --require-hashes`. Record the new absolute paths
and effective source/environment identity; do not overwrite this evidence.
Failure to obtain the exact pins is a readiness blocker, not permission to
substitute versions or repair the shared environment.

`protected-files.json` snapshots 177 tracked production/config/baseline files
selected on 2026-09-12 by:

```powershell
git ls-files -- blueearth_cst scripts config pixi.toml pixi.lock '*.smk' Manifest.toml Project.toml dev/baseline
```

The count was measured, not a coverage promise for future checkouts. Re-measure
and compare actual bytes at readiness completion. Predecessor evidence integrity
is additionally covered by the complete D4 inventory audit. Download/install logs
are in this session's `gf15-lmoments-readiness` scratch directory.
