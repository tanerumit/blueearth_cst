# Weather styling: published source pin and integration evidence

Date: 2026-10-30. Scope: delivery of the reviewed WF3 weather styling and shared panel layout,
with the independent CIESM exclusion already committed in the same session branch.

## Dependency decision

The user authorized pinning the verified published upstream commit instead of waiting for an absent
`v2.1.0` tag. The installer pins `weathergenr` version 2.1.0 at
`b023e65e5237f681cb96178754488bba84afb2ae`, which is reachable from published upstream master.
It accepts an existing installation only when both `Version` and `RemoteSha` match, and checks both
again after installation. A same-version package from another source is reinstalled.

The approved implementation is `2b2f602cb3f6500fb69e014d7c6650be357f5370`. Comparison with the
published pin shows changes only to `DESCRIPTION`, `NEWS.md` and the agent manifest; no R source
changed. The original implementation's scientific and visual evidence remains applicable.
This is an R source pin outside `pixi.lock`; no conda dependency or Julia contract changed.

## Fresh verification

Checks ran in session-2 with Python 3.12.13 and normal Windows user permissions for Snakemake.
Installation used a task-owned private R library; the shared Pixi runtime was not modified.

- `pixi run --frozen --no-install python -m pytest tests/test_resolution.py
  tests/test_projection_coverage.py tests/test_derive_change_factors.py
  tests/test_prepare_projection_analysis.py tests/test_provenance.py tests/test_report.py
  tests/test_panel_layout.py tests/test_weather_plot_identity.py --basetemp <fresh-task-path> -q`:
  120 passed in 85.69 seconds. Two existing xarray `drop` deprecation warnings remain.
- The installer downloaded and installed the exact published commit into the private library.
  A second invocation returned early with `already installed`.
- A controlled private-library fixture retained version 2.1.0 but replaced `RemoteSha` with an invalid
  value. The installer rejected that identity, reinstalled, and restored the correct commit.
- A fresh R process verified the private library location, version, exact source SHA and the
  `style_weather_plot`, `arrange_weather_panels` and `export_weather_plot` exports. The CST YAML
  adapter loaded its theme and expected simulated-series colour successfully.
- Scoped Python Ruff lint and formatting passed. R `lintr` reported no lints after two indentation
  corrections and a wrapped message. `air` was unavailable; the R change follows the local style.
- `pixi lock --check --dry-run` reported that the lock file would not change.

The final integration also requires the focused WF2 DAG cases through the landing verifier.
Its receipt and raw logs remain in session-2's `.tmp/tasks/session2-landing-20261030/`.

## Reused scientific and visual evidence

The original implementation handoff recorded 1,445 R assertions (four expected skips), eight
independent numeric baseline assertions including PSOCK, and package checking with zero errors or
warnings. Actual CST wrapper runs with plotting off/on produced identical dates, resampling,
fit metrics and full-grid netCDF contents. All 15 maintained figures were rendered at 600 DPI,
inspected and approved; ten faceted figures met the 70 mm panel geometry. These runs were not repeated
for the source-pin change because the pinned upstream R implementation is identical.

The independent CIESM diagnosis and numerical evidence remain in
[the CIESM validation record](ciesm-source-quality-2026-10-30.md).

## Installation and retention

After updating a runtime, run `pixi run install-rdeps` before WF3 to install the newly pinned R
implementation. This integration verified private installation and did not update the shared runtime
while other sessions may borrow it. No tag, GitHub Release or push was performed.

Retain the private library and integration logs until the runtime owner confirms installation.
Retain the original task's approved PNGs and styled R objects while the comparison gallery needs them.
Keep the socket-stall reproducer and logs until confirmation on the originally affected Windows machine.
