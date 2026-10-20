# WF2 suite integration evidence — 2026-10-07

Historical acceptance evidence for closed task `t2610071652`, locally merged at
`3be724c554660e9e636d46e112baeac7cb824c9b`. Condensed on 2026-10-20 without rerunning the
experiments. This records the evaluated implementation and its limitations; current WF2 behavior
is described in the [workflow guide](../../../docs/site/toolbox-reference/workflow-analyze-projections.qmd).

## Provenance and scope

Full source and decision history are recoverable at commit `53d07f52`:

```text
dev/records/reviews/wf2-suite-integration/implementation-validation.md
dev/records/reviews/wf2-suite-integration/wf2-suite-integration-design.md
dev/records/reviews/wf2-suite-integration/wf2-suite-integration-ledger.md
dev/records/reviews/wf2-suite-integration/design-runs/wf2-suite-integration/
```

The original validation source named scratch `.tmp/scratchpad/wf2-suite-evidence/` and snapshot
`.tmp/scratchpad/t2610071652-snapshots/` roots. Their untracked data/logs are not guaranteed recoverable
through Git. This record preserves reported results and hashes, not the underlying datasets.
The source describes Windows/Pixi execution but supplies no separate lock fingerprint; do not
substitute a later task's environment hash.

The integration added diagnostic analysis tables and plotting while preserving existing Stage B
change-factor arithmetic and protected runtime identities. Implementation commits included
`1672686c` (helpers), `7683ddb6` (coverage/families), `c606bcdd` (reductions),
`5b5b219e` (analysis producer) and `a9d69d47` (figures).

The P0 ensemble comprised 13 models, 25 members and four SSPs; the lab source was commit `7560e71`.
The historical design used a configured reference of 2000–2014 and a `mid` horizon of 2046–2054,
with diagnostic fallback/recentering to longer windows. Those window rules were subsequently
superseded. Even the old supersession banner's fixed 27-season minimum is not current:
current seasonal coverage depends on each window's length. Do not reuse these historical design
parameters as present-day requirements.

## Numerical preservation

Protected Stage B and reducer source hashes remained:

- Stage B: `a11fc4fbe4b92c37a623154a7a2f657c6f53790d14a8c1b577e153acc4a87fce`.
- Reducer: `942fa42db363742b5f3258cc386b7de7c7a4a5936e8a6e3d7e71e`.

WF3/WF4 repository inventories also matched the before-image.

| Case | Annual / monthly rows | Comparison |
|---|---|---|
| Isolated archived rapid | 8 / 96 | Original and extracted Stage B, raw bytes equal |
| Fresh rapid scalar inputs | 12 / 144 | Original-source oracle and revised output, raw bytes equal |
| P0 | 600 / 7200 | Original snapshot and fresh downstream output, raw bytes equal |
| Synthetic dry reference | 4 / 48 | Original/current Stage B plus serializer, raw bytes equal |

SHA-256 values, annual then monthly:

```text
archived rapid:
4984466e5f1ebd14f48e075f9573e83cf9567cc0d2c9f696e3c8ecff41a6f62a
706ab4593a9fd48ce4f793c51ba6147e1e6bdeb47abb7dc4289abcebab3f6864
fresh rapid:
27c6916dd90204fbd5f433ded5e2dc1c5d4997c7872de476e54b8da66673ff2e
5504fb8ecea0116535d0549011b6b028f4df42e845dd764f310574195c9a1b54
P0:
360d2512fce5f62a06b13f272c7e001f7e914b2b55701eacc38d6ddb6e11eea8
d41e232d6a5d80d8bfbce79b2f268d584ac9abaaf675effabc1fb432b97c0a9f
synthetic dry reference:
640f022494ed14f0e04f065073d5932ebd910161af8eb7073deb49c8471ae953
a0a0f003af7e5fcd0ecc3af3a25c0a6788217df35e8f899af352d54d8132127d
```

Archived comparisons used isolated synthetic identities on retained values because older reducer
metadata was stale. They established arithmetic/serialization parity, not production-cache validity.
Fresh rapid was an original-source oracle comparison on the same new scalar inputs, not a pre-edit
fresh workflow execution. The synthetic case exercised `reference_below_threshold` flags without
changing production identities.

## Lab agreement and scientific qualifications

The cached P0 producer processed 100 points into 14 tables: 18,700 change rows, 30,200 annual-member
rows, 5,100 member ratios and 40 exact-mask panel benchmarks.
Lab reductions matched unchanged fields in 2,444 model rows and 188 summary/agreement rows,
with no missing keys, value or count mismatches; added statistic rows were separately reported.

An initial comparison of 11,900 absolute and 5,200 nonseasonal relative rows identified float32
scalar-versus-float64 lab differences. Promoting only diagnostic slices before kernel calls corrected
these while leaving aligned arithmetic unchanged. Maximum absolute/relative change discrepancies
were then `1.42e-14` / `7.11e-14`.

Seasonal precipitation percentage changes deliberately used mean rates whereas the lab used totals;
that owner-approved exception was excluded from the parity claim. Precipitation CV used integrals.
The October fallback reference was owner-ruled WY 1984–2013, matching the lab without scenario data
in the reference; that historical fallback policy was later superseded.

Additional scientific safeguards and rationale from the accepted review:

- Null bands used a stated white-noise Monte Carlo model, actual retained year coordinates and
  missingness/overlap masks, with table-identical OLS detrending. Counts alone were insufficient.
  Member-specific mean, variability and support were reduced using the same geometric statistic.
  This was sampling-reference evidence under that null, not empirical internal-variability validation.
- Precipitation panel benchmarks used median model-mean eligible reference CVs. Each retained
  reference/future mask pair received its own band; heterogeneous masks were not collapsed to counts.
- Mean-change eligibility was statistic/unit-specific: dry references could retain absolute changes
  while relative changes were unavailable. Raw-SD status used raw SD; detrended-ratio status used
  detrended SD. A linear-trend falsifier distinguished the two.
- Family-aware agreement was a count, not a probability. The exact cited Zenodo licence was
  unverified, so no source CSV was redistributed; metadata matched the lab. Unlisted models used
  flagged unambiguous institution matching or their own family.

Those rationale points explain the evidence; current contracts remain owned by code and current
documentation. The complete accepted design/ledger preserves alternatives and finding identifiers
through the recovery pin above.

## Execution and acceptance

Fresh rapid completed in 4m36s with 14 expected PNGs. Fresh single-model WF2 completed with 13.
Both had bijective availability, PNG and caption inventories.
Fresh spatial parity passed 19 tests against the new project, without altering the standing baseline.

Fresh P0 reused 125 validated raw inputs and rebuilt all 125 scalar series and downstream products.
It was a retained-raw fresh downstream run, not 125 new remote acquisitions.
A stalled scheduler was recovered serially; the original P0 archive was untouched.
All eleven fresh P0 lab-parity checks passed subject to the stated seasonal exception.
P0 had 15 available products with bijective PNG/caption inventories.
Rule timings were 239.79 seconds for analysis and 18.78 for rendering, total 258.57 seconds,
within the historical five-minute budget.

All fifteen cached P0 figures were reported inspected; fresh cloud/member-ratio figures were also
inspected. Synthetic rendering included ordinary/captioned figures and a combined-window cloud.
Formal owner visual acceptance remained separately outstanding in the closure record.
Later [plot integration evidence](plot-improvements/verification.md) adds subsequent rendering
coverage; it does not silently certify every earlier human acceptance item.

Final software evidence:

- Fast: 3975 passed, 17 skipped, one known upstream expected failure.
- Full: 4054 passed, 17 skipped, one known upstream expected failure; lint/format passed.
- All-five `test-e2e`: one integration test passed, 4060 deselected, 47m39s; no integration skip.
- The generic 17 skips were five Linux-only controls, eleven local-input lab tests and one opt-in
  integration case. The latter twelve were exercised separately with fresh P0 overrides/all-five execution.
- Local landing candidate fast gate repeated 3975/17/one xfail; tested-tree equality and ancestry passed.

Earlier failed gates, cache-only runs and host-access failures were not counted as passes.
The final evidence establishes the bounded historical parity and integration claims above,
not a present-day full-toolbox validation or a numerical-baseline refresh.
