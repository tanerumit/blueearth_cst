# Release qualification evidence — October 2026

Historical evidence condensed on 2026-10-20, without repeating any gate or numerical calculation.
This record preserves bounded qualification and waivers, not current release clearance.
Original narratives are recoverable at commit `53d07f52`:

```text
dev/records/reviews/2026-10-01-v0.3.0-release-gates.md
dev/records/reviews/2026-10-12-v0.4.1-release-gates.md
```

Untracked scratch logs, probes, figures and run trees named by those records are not guaranteed
recoverable through Git.

## v0.3.0 — baseline regeneration and retained-target agreement

Initial candidate `548ec08c6e596a85a6d19d1797f2df0409c858c3` passed lint/format,
fast (4027 passed, 21 skipped, one xfail) and full (4134 passed, 21 skipped, one xfail).
Numerical checks stopped on stale fixture metadata/structure; those failures established neither
numerical regression nor parity. The initial tree had four unmapped paths.

Fresh five-workflow execution subsequently succeeded from
`b34f44911aad71016a049d93069a1c7a3982bbec`, with committed
`test_case/project_config_baseline.yml`, three cores and `--notemp`.
Invocation identity was `995548f630344f8f940407323bf4e2cf`.
All 14 ensemble members completed; historical collection `2f93c7b45e8f`,
metric request `60ec869770e7` and metric set `88ac4f4e2690` identify that run.
The prior fixture was preserved as `test_case/test_local-pre-v0.3.0-refresh-2026-10-01`.

Reported numerical outcomes:

- Both projection summary tables exactly matched original normalized SHA-256 values;
  all three projection targets passed.
- All 560 discharge-indicator rows over 44 groups exactly matched accepted reference values,
  with identical keys and no column remapping. The lookup covered every emitted group.
  A control increasing the largest reference indicator by 50% failed the comparator.
- All 6209 historical discharge timesteps passed; maximum relative difference was
  `3.1276997004808734e-16`.
- Interchange checks passed 95 tests, with one retired warm-state check skipped.
  Ten previously fixture-dependent skips were exercised successfully.
- The complete baseline check passed six targets after a metadata-only manifest correction.

That correction replaced build-run-record hash
`07af91dbac2fcfe14d924f68a9c4342a04194f236537b06ca229d9dffd610317`
with `2ec3537aaa2834c1b1bf57e7acbf6f3455021d5930f5c66c596d312651d5ddcc`.
The loaded configuration differed only in archived-config digest `c7df597e1a22` → `7b5107c149cd`;
both archived YAML files parsed to identical settings. No numerical reference or tolerance changed.

The old/new semantic tree diagnostic exited 1: 188 common files, 52 differing, 179 missing,
162 extra. Differences included old identifiers/layouts, archived pointers, basin feature count
(five versus four) and graphics. The old tree was not a matched migration reference.
The six passing baseline targets therefore did not establish whole-tree equivalence.

The fresh tree initially had 124 unmapped paths out of 378. An approved constrained inventory
amendment recognized all 378, with no unmapped paths; 226 focused tests and 48 glossary/seal tests
passed. Lint/format passed, and the six baseline targets passed again.
The existing catch-all for other experiment names was unchanged: strict coverage applied to the
selected experiment, not every sibling.

Representative maps, precipitation boxes, outlet hydrograph, projection changes and generator
cycles were visually inspected. This was neither inspection of every figure nor model-performance
acceptance. Nonfatal limitations included unavailable optional RGI glacier data, upstream state-CRS
assignment and R locale warnings. Native duplicate outlet output was retained once as location `1010`.
Cross-platform CI and Linux scientific E2E qualification were not established by these local checks.

The first approved landing gate later failed one stale inventory test
(4066 passed, eleven skipped, one xfail). The corrected behavioral test passed 176 focused checks.
The retained source does not contain the final repeated gate/merge result; do not infer release
publication or completed landing from this record.

## v0.4.1 — seasonal oracles and explicit E2E waiver

Runtime candidate was `f401899a8699d45c03f9ccae995f785350b99fac`.
The owner explicitly chose version 0.4.1 despite feature/breaking changes and waived the incomplete
E2E gate for this release only. This was a historical exception, not a general verification policy.

Lint/format and 20 CLI tests passed. Full passed 4438 tests, with 28 skips, one known upstream
expected failure and 7167 warnings. Documentation candidate `0d56496a` subsequently passed fast:
4340 passed, the same 28 skips/one xfail and 7167 warnings.
Skips covered Linux-only controls on Windows, stale interchange fixtures, absent P0/lab inputs
and the separately opted-in E2E case. The xfail concerned HydroMT catalog preprocess serialization.

Independent seasonal means were recomputed from retained Gabon monthly inputs using duration
weights. A separate least-squares/variance oracle passed 1280 seasonal variability rows.
Captions reported 27/18 seasonal thresholds for those evaluated windows.
Annual/monthly rows matched the retained case within the source's stated tolerances, but that
release summary did not reproduce their numerical values or input hashes.
The scratch oracle scripts/input hashes were recorded under
`.tmp/scratchpad/release-0-4-1/`; this summary does not invent missing tolerances.
Six seasonal figures were rendered, with change and variability families visually inspected.

These were retained-input independent checks, not a v0.4.0 comparison or whole-tree baseline claim.
The baseline manifest was explicitly stale after the P-drive/GlobCover change.

The E2E attempt completed WF0 and WF1 model building/historical simulation, then stopped during
WF2 acquisition/reduction. WF3/WF4 did not run. It was not a passing all-five gate.
The partial root was `.tmp/pytest/run-41725be7cc3b48328ae9dc4745274f18/`.

The source also records publishing CI run `38279264122` exposing Ubuntu tests that depended on
a developer catalog. Those test inputs were changed to the hermetic test catalog, preserving
success/failure assertions without changing production numerical inputs or code.
The retained source calls for subsequent CI/gate verification but does not provide its final result;
it does not independently prove successful two-platform publication or tagging.
