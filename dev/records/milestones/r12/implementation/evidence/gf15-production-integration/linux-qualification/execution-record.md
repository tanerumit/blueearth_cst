# Linux GF15 source and parity execution

Date: 2026-09-26. Host: WSL2, Ubuntu 26.04.1 LTS, x86_64. Scope: D8 handoff
2/4 for `gf15-lmoments-c/1`; no WF4 simulation or production response run.

## Isolated environment

WSL2 was installed through an elevated `wsl --install` after the first
non-elevated attempt failed. The user completed Ubuntu's first-launch account
setup. `wsl --exec uname -a` reported kernel 6.18.33.2 under WSL2. Linux Pixi
0.70.2 was installed in this worktree's ignored scratchpad at
`.tmp/scratchpad/2026-09-26_2231/pixi/`. A copy of the tracked `pixi.toml` and
`pixi.lock` was installed with `pixi install --locked` under
`.tmp/scratchpad/2026-09-26_2231/linux-gf15/`; the repository's own Pixi
environment and lock were not changed. This scratch environment is disposable;
the scripts and results here are the retained evidence. Julia was installed by
juliaup; `julia +1.11.7 --version` reported 1.11.7 on Ubuntu's login-shell PATH.
Julia packages were not instantiated because this adapter parity run invokes no
Julia code.

From Ubuntu at this worktree root, the retained probe commands are:

```bash
ISO=.tmp/scratchpad/2026-09-26_2231/linux-gf15/.pixi/envs/default/bin/python
PYTHONPATH="$PWD" "$ISO" -B dev/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/quantile-probe.py
PYTHONPATH="$PWD" "$ISO" -B dev/milestones/r12/implementation/evidence/gf15-production-integration/linux-qualification/parity-probe.py
```

For the owning tests, set `GIT_DIR` to the primary checkout's `.git` directory
and `GIT_WORK_TREE` to this worktree's Linux mount path before invoking this
interpreter. The environment root above is session scratch: reinstall from the
tracked manifest and lock if it has been removed.

The Linux interpreter reports Python 3.12.13 (conda-forge, GCC 14.3.0), NumPy
2.4.6, SciPy 1.18.0 and `lmoments3` 1.0.8. The lock's linux-64 PyPI entry
points to the D7 wheel SHA-256
`984d1f1b0c3feefd57afc7a270931c1d28e4face2df1c2293559faf47681ef5e`.
The installed `lmoments3` source digests were rehashed:

| File | Installed SHA-256 | D7 match |
|---|---|---|
| `__init__.py` | `1d2c066a2ec4925bb838b7680d63ae8ae87c5234aa3c986d6ebe81500d75d6e2` | yes |
| `distr.py` | `f8859d11f10c3206e3e5009c1b238a328c6c9215b1cc7436800160fa929bb2ee` | yes |

`resolve_metric_environment()` was observed inside that interpreter and is
retained in [quantile-results.json](quantile-results.json), including the source
digests. [environment-comparison.json](environment-comparison.json) compares its
package projection with the accepted Windows Stage 1 projection: Linux has 224
packages, Windows 220; 204 keys are shared, 83 values equal and 121 differ;
20 keys are Linux-only and 16 Windows-only. Both native/metadata lock digests
differ. This is an expected platform-specific identity, not projection equality
across platforms.

## Parity and controls

[parity-probe.py](parity-probe.py) compares the production adapter with the
frozen assessed candidate on 28 sample shapes × 7 probability sets. It compares
acceptance, refusal reasons, warning records, input digest, normalization,
moments, both parameter maps, quantile values and status, and both diagnostic
count maps. [parity-results.json](parity-results.json) records **196/196
matching cases** (168 accepted, 28 refused), plus **84/84 matching
invalid-probability cases**. A deliberate 1e-9 change to an accepted published
estimate fails the same comparator. The candidate does not serialize production
stage/source fields or retain diagnostic `log_density` in the same shape; their
contracts are covered by owning tests, not candidate equality.

[quantile-probe.py](quantile-probe.py) checks all 44 retained quantile controls
against the fixed readiness tolerance `1e-10 × max(1, |reference|)`.
[quantile-results.json](quantile-results.json) records **44/44 within tolerance**
and 41/44 bit-identical to the Windows references. The three differences are
`population_.2`, `positive_tau_.2` and `snap_tau_-.00002`, each one ULP; the
largest absolute difference is 4.44e-16. A 1e-9 wrong-result multiplier
breaches the retained tolerance on 40 controls.

The owning Linux run of `tests/test_gev_lmoments.py` and
`tests/test_return_level_validation.py` passed **86 tests**, with five
Windows-specific bit controls skipped. These modules cover exception-derived
refusals and injected warnings that the parity matrix does not generate. The
same Windows run passed **86 tests**, with five Linux-specific tolerance
controls skipped. The Linux run set `GIT_DIR` and `GIT_WORK_TREE` explicitly:
the linked worktree's `.git` file contains a Windows `C:` path that Linux Git
cannot resolve. The initial Linux test run had 79 passes, five skips and two
Git-tracking failures; the two checks passed with those variables set. The
initial Windows runs hit sandbox temp-directory permissions and then the
relocated-loader test's requirement that pytest's temp directory be outside
the checkout. The final Windows run used pytest's external default temp path
outside the sandbox and passed.

The retained scripts were rerun from their final paths; all three result JSON
documents reproduced as parsed JSON. Windows `ruff check` and `ruff format
--check` passed on the touched Python files. No full test suite or Linux
workflow run was used as evidence for this narrow adapter qualification.
