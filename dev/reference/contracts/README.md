# Interchange contracts

Last updated: 2026-10-20

Current obligations at the weather-generator and hydrological-model substitution seams.
Preserve contract identifiers when changing their descriptions or consumers.

- [`weather-generator-seam.md`](weather-generator-seam.md) — WG-1..WG-6: what
  a replacement stochastic weather generator consumes and must produce.
- [`hydrological-model-seam.md`](hydrological-model-seam.md) — HM-1..HM-7
  (HM-6a/6b): what a replacement hydrological model consumes and must
  produce.

Each doc carries the per-artifact contract table (pinned /
pinned-as-reliance / deliberately-unpinned), a bounded-substitution
walkthrough (the exact repo files a swap touches), and a validator index.

**Checking.** Validators live in `blueearth_cst/shared/interchange_contracts.py`;
`tests/test_interchange_contracts.py` owns executable coverage. Inspect test results for fixture-dependent
skips; skipped integration checks do not establish interchange compatibility.

[Forcing units](forcing-units.md) owns catalog admission and the reviewed interpretation of source values.
