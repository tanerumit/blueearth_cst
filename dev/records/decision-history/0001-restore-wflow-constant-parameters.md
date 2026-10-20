# ADR 0001 — Restore Wflow constants through two-sided equivalence evidence

Historical decision, accepted and implemented 2026-07-21 by Ümit Taner.
Condensed 2026-10-20; no measurements repeated.

**Current authority:** [wf1-model-construction.md](../../reference/wf1-model-construction.md).
The build template owns exact values and names; this record explains their historical selection.
Use [dev-validation.md](../../reference/dev-validation.md) for present verification requirements,
not the former implementation protocol below.

## Context and decision

The HydroMT-Wflow 0.x → 1.x migration rejected legacy constant names. An interim build retained
only required `KsatHorFrac`, leaving the engine's implicit defaults for the other parameters.
The owner chose explicit reference continuity and protection against default drift, rather than
silently accepting all new engine defaults.

Restoration was conditional on authoritative **both-sided** evidence for each parameter's units,
sign, scale, timestep basis and semantics. A name mapping or a reference template alone was
insufficient. Missing or ambiguous evidence excluded that parameter from restoration.
All thirteen mappable constants subsequently passed; `KsatHorFrac` remained, and deprecated
`InfiltCapSoil` was dropped.

The restored values came from template commit `6ebc46f`. Eight matched the HydroMT documentation
template, four differed (the three glacier constants and `InfiltCapPath`), and `MaxLeakage` was
initially unresolved. The equivalence investigation established its 1.x default as zero, making it
a ninth default-equal pin. **Template equality is not engine-default equality:** for example, the
recorded `TTI` and `EoverR` template values differed from the engine's defaults.
None of these choices was a claim of local calibration.

Two priority ambiguities were resolved by source evidence: the old `g_ttm`/`g_tt` mapping referred
to the glacier melt-onset threshold, and `MaxLeakage=0` preserved the previous physical meaning.
The per-parameter sources and conclusions remain in the
[equivalence gate log](../validation/wflow-constant-restoration/equivalence-gate-log.md).

## Landing and numerical evidence

`setup_constant_pars` wrote `input.static.<CSDMS-name>.value` scalars in the model TOML,
not constant layers in `staticmaps.nc`. The plugin rejected unrecognized names; the consequential
risks were semantic mismatch, a competing raster binding and inactive processes.

The full build evidence and separately pinned configurations remain in
[constant-restoration validation](../validation/wflow-constant-restoration/README.md).
The baseline config was snapshotted from `48bc1d3`; the candidate and equivalence work were
committed at `1d011c0`. Three clean WF1 builds used the same basin/settings and Julia 1.11.7:
one restored build and two baseline builds. Discharge covered 7670 daily timesteps,
2000-01-02–2020-12-31, at outlet `Q_130000086`.

- All fourteen retained/restored constants landed as the expected TOML scalars, without shadowing.
  Snow was enabled; glaciers were disabled.
- The two baseline builds produced identical discharge: maximum normalized difference zero.
- Restored versus baseline had zero failing timesteps. Maximum absolute difference divided by
  mean reference discharge was `1.655e-4`; maximum relative difference over the eligible subset
  was `7.091e-3` (about 0.71%). The change was nonzero but below the recorded tolerances.
- The reported comparison used `ATOL = 1e-3 × mean(Q_ref)` (0.01095 here), `RTOL = 0.01`.
  A timestep failed if `|ΔQ| > ATOL`, **or**, when `Q_ref ≥ ATOL`, `|ΔQ| > RTOL × Q_ref`.
  This was an OR test, not an additive absolute-plus-relative tolerance.
- The implementation record reports promotion of the restored config, a full WF1 rebuild and
  replacement of five WF1 baseline targets including a stored discharge series.
  WF2/WF3 manifest rows were preserved unchanged.

The old comparator aligned timestamps and rejected duplicate timestamps, unequal index sets,
NaNs and nonnumeric values. Its same implementation served reproducibility, materiality and
the stored-reference check, avoiding inconsistent verdicts across those uses.
These historical thresholds are not an instruction to apply them to unrelated changes.

## Interpretation and limitations

The discharge comparison measured the **aggregate restored set on one test basin**. It did not
attribute changes to individual parameters or distinguish weak sensitivity from cancellation.
Disabled glacier processes supplied no hydrological validation of glacier parameters.
Snow being enabled did not establish that snow materially influenced this forcing period.
Default-equivalence claims rested on source evidence, not on a small discharge difference.

The historical verification was a one-time scalar-landing check; the discharge baseline did not
constitute permanent direct coverage of every restored TOML value. That was a stated coverage gap,
not evidence that a later build remained correct.

The former protocol distinguished a material change, requiring examination of affected downstream
outputs, from an immaterial aggregate change, which re-recorded WF1 only. It warned that byte-exact
downstream fingerprints could still move after an immaterial WF1 change. Such a later failure
required investigation and attribution, never an automatic re-record. Present checks and baseline
decisions are owned by the current validation reference.

The subsequent closure of the mixed-provenance indicator concern is retained separately in
[R09 indicator-axis migration §5](../milestones/r09/migration_indicator-axis-columns.md#5-gate-status).

## Alternatives considered

- **Adopt implicit engine defaults:** smallest config, but changes reference physics silently as
  defaults evolve, including processes absent from the test basin.
- **Restore only differing defaults:** smaller explicit set, but requires reliable per-parameter
  evidence and relinquishes drift protection for omitted equal defaults.
- **Drop values immaterial on the test basin:** rejected because aggregate inactivity or cancellation
  cannot establish that an individual constant is unnecessary on another basin.
- **Defer restoration:** initially viable because the model built, but postponed the unresolved
  scientific reference choices and two-sided mapping investigation.

## Original section and finding recovery

The complete pre-condensation record, including the parameter table, numbered protocol and
review chronology, is recoverable with:

```text
git show e9bbd72d:dev/records/decision-history/0001-restore-wflow-constant-parameters.md
```

| Historical citation | Meaning and recovery |
|---|---|
| Decision; parameter reconciliation | Evidence-gated restoration; exact table in the pinned record |
| Validation steps 1–3c | Mapping, distinct configs, scalar landing, precedence and two-sided gate |
| Step 4 / 4b | Reference build and independent clean-build reproducibility |
| Step 5 / 6 | Aggregate materiality and aligned per-timestep comparator, summarized above |
| Step 7; immaterial branch | Scoped baseline merge and qualified downstream recovery |
| Consequences; durable-coverage gap | Direct scalar coverage was deferred |
| `ext1-1`, `ext2-1` | Semantic equivalence required authoritative evidence for both engine generations |
| `ext2-2` | Baseline and candidate configs were separately materialized |
| `ext2-3` | Proposed downstream coherence review was made explicit, not claimed as executed |

The review recorded 26 findings and acceptance under owner arbitration after two external rounds.
Original review detail and former path mappings remain recoverable through the
[decision-history migration map](../migrations/decision-history-transition-2026-10-20.md).
