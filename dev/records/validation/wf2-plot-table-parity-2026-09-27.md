# Historical WF2 plot-to-table parity — retained 2026-09-27

Evidence extracted on 2026-10-20 from the completed plotting-standardization task `t2608091006`;
no calculations or figures were regenerated. Recover the source at:

```text
git show 53d07f52:dev/records/reviews/wf2-plot-standardization-2026-09-27.md
```

The initial prototype exposed a producer error: monthly changes used an annual historical mean
and the full future series instead of corresponding calendar months within each selected horizon.
Across 72 rows, the corrected prototype agreed with the authoritative monthly change-factor table
within reported differences of 0.000491% precipitation and 0.000894 °C temperature;
the worst case was `GFDL-ESM4 · ssp585`. These are the source's reported comparison bounds,
not new acceptance tolerances.

The subsequent table-to-figure regression `test_values_come_through_untouched` passed sentinel values
999.0 and −42.0 through rendering, checking that the renderer did not introduce a second calculation.
The production port reported 53 new unit tests, 14 CLI checks and a full suite with
2538 passed, six skipped and one expected failure. Its render preserved nine traces per overview
panel, six cloud points and six monthly traces.

The independent prototype was retired on 2026-09-24; its source is recoverable through
`archive/dev-scripts-2026-09-24`. The evidence source does not supply a final port candidate hash,
input-table digest or skip rationale, so this is a historical reported result rather than a
fully reproducible numerical qualification.

The September 27 follow-up reported 40 focused tests, Ruff checks and inspected single/multiple
subcatchment, multi-gauge and evaluation-sheet renders, with calculations/output names unchanged.
Those fixtures were illustrative and established no hydrological model-performance claim.
The old prototype instructions, production paths and blanket no-title ruling are superseded;
current styling belongs in [toolbox-plot-style.md](../../reference/toolbox-plot-style.md).
