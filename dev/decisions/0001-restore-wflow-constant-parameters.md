Status: proposed
Date: 2026-07-21
Deciders: Ümit Taner
Consulted: M2b handoff (dev/phase-1/m02b/handoff.md §3), advisor review 2026-07-21
Supersedes: none
Revisions:
  - 2026-07-21: initial draft (task t260719a).

# ADR 0001 — Reconcile the dropped Wflow constant parameters via evidence-gated CSDMS restoration

### Context

The upstream Deltares model-build template set 15 spatially-uniform constant
parameters through hydromt_wflow's `setup_constant_pars` (snow, glacier, soil,
and vegetation physics). The M2b library upgrade (hydromt_wflow 0.x → 1.x)
broke this: 1.x rejects the old short names (`Cfmax`, `TT`, …) and requires
CSDMS Standard Names. Under M2b's declared "intentional drift, re-baseline
aggressively" policy, the block was reduced to the single parameter Wflow.jl
1.x *errors* without — `KsatHorFrac` (=100, now under its CSDMS name) — and the
other 14 were dropped, so the model now runs on **Wflow.jl 1.x's internal
defaults** for all of them. That is the current baseline, preserved by
construction through R3/R4/R5.

Two forces make finishing this non-trivial and worth a record. **First, it is a
scientific choice, not a mechanical rename.** Restoring a value to a CSDMS name
changes the built model only where the reference value differs from Wflow.jl
1.x's default; whether that difference matters for *this* basin's discharge is
an empirical question no one has measured. **Second, the failure modes are
silent.** hydromt_wflow may accept a CSDMS name and never write it to
`staticmaps.nc` (a no-op that looks like success); and the baseline manifest
currently fingerprints only three wf1 PNGs (size ±10%) plus the snake-config
snapshot — **not** `staticmaps.nc`, the TOML, or `output.csv` discharge — so a
restoration-driven change is invisible to `check_baseline` until this task adds
those targets (manifest scope recorded in `dev/followups.md` § baseline-manifest
integrity and `dev/r01/baseline_diffs.md`).

A subtlety governs the whole decision: several of these constants only bite when
their process is active. Snow parameters (`Cfmax`, `TT`, `TTI`, `TTM`, `WHC`) and
glacier parameters (`G_Cfmax`, `G_SIfrac`, `G_TT`) do nothing on a snow- and
glacier-free basin. So a null discharge move on the reference test basin does
**not** prove a null move on the snow/glacier basins CST is meant to run
globally. The decision must therefore weigh cross-basin correctness, not only
test-basin sensitivity.

All 15 mappings are now resolved against
`hydromt_wflow/naming.py` (the M2b handoff left 5 "unresolved"; none is actually
`wflow_v1: None`). Restorability is settled: 1 retained, 1 deprecated
(forced drop), 13 mappable.

### Decision

We will **restore the 13 mappable constants to their Deltares-reference values
under their CSDMS Standard Names**, keep `KsatHorFrac`, and **drop the deprecated
`InfiltCapSoil`** (`wflow_v1: None`). Restoration is the default posture because a
global, no-calibration, rapid-assessment tool should pin its physically-meaningful
constants to a documented reference set rather than silently inherit an engine
default that can drift across Wflow.jl versions and that diverges from the
reference on snow/glacier basins the test fixture cannot exercise.

The restoration is **evidence-gated in its blessing, not its posture**: the
per-parameter *effect* is measured, never asserted. Implementation builds the
model twice into clean project dirs — restored-config vs current-config — and
(1) asserts every restored value actually lands in `staticmaps.nc`/the TOML,
(2) diffs `staticmaps.nc` to attribute which parameters change a map, and
(3) diffs `output.csv` discharge to quantify the net move. The resulting change
is recorded as a one-time, understood, **documented baseline move**; where the
reference value provably equals the 1.x default (net zero contribution), the
explicit setting stands as drift-protection and documentation rather than a
behavioral change.

**Parameter reconciliation** (values from git `6ebc46f`; CSDMS names from
`hydromt_wflow/naming.py`). `default (1.x)` and `built value` are measured during
implementation — the first two columns and the class are decided here:

| 0.x name | value | CSDMS Standard Name (`wflow_v1`) | class |
|---|---|---|---|
| KsatHorFrac | 100 | subsurface_water__horizontal_to_vertical_saturated_hydraulic_conductivity_ratio | RETAINED |
| Cfmax | 3.75653 | snowpack__degree_day_coefficient | RESTORE |
| TT | 0 | atmosphere_air__snowfall_temperature_threshold | RESTORE |
| TTI | 2 | atmosphere_air__snowfall_temperature_interval | RESTORE |
| TTM | 0 | snowpack__melting_temperature_threshold | RESTORE |
| WHC | 0.1 | snowpack__liquid_water_holding_capacity | RESTORE |
| G_Cfmax | 5.3 | glacier_ice__degree_day_coefficient | RESTORE |
| G_SIfrac | 0.002 | glacier_firn_accumulation__snowpack_dry_snow_leq_depth_fraction | RESTORE |
| G_TT | 1.3 | glacier_ice__melting_temperature_threshold¹ | RESTORE |
| cf_soil | 0.038 | soil_surface_water__infiltration_reduction_parameter | RESTORE |
| EoverR | 0.11 | vegetation_canopy_water__mean_evaporation_to_mean_precipitation_ratio | RESTORE |
| InfiltCapPath | 5 | compacted_soil_surface_water__infiltration_capacity | RESTORE |
| MaxLeakage | 0 | soil_water_saturated_zone_bottom__max_leakage_volume_flux | RESTORE² |
| rootdistpar | -500 | soil_wet_root__sigmoid_function_shape_parameter | RESTORE |
| InfiltCapSoil | 600 | None (deprecated in Wflow.jl 1.x) | DROP |

¹ `naming.py` collapses old `g_ttm` and `g_tt` onto one v1 name; the template set
only `G_TT`, so restore `glacier_ice__melting_temperature_threshold: 1.3`.
² `MaxLeakage: 0` disables leakage and is very likely already the 1.x default →
expected net-zero; set explicitly for documentation + drift-protection.

### Validation protocol (implementation)

1. **Resolve mappings** — done (table above); restorability settled.
2. **Restored build** — add the 13 CSDMS entries + `KsatHorFrac` to
   `config/wflow_build_model.yml`; build wf1 into a *clean* project dir.
3. **Landing assertion (silent-no-op guard, mode a)** — for each restored
   parameter, assert the value is present in `staticmaps.nc` (and/or the TOML)
   as the uniform constant set — a name accepted but not written must fail.
4. **Reference build (freshness, mode b)** — build the *current* config into a
   separate *clean* project dir. No `ancient()`/timestamp-blessed reuse of
   `examples/test_local`; both builds are from scratch so neither is stale.
5. **Attribution** — diff `staticmaps.nc` restored-vs-reference to see which
   parameters actually change a map (snow/glacier layers on a snow/glacier-free
   basin should show none).
6. **Discharge materiality** — run Wflow on both; diff `output.csv` discharge.
   Immaterial → the restored set matches defaults for this basin (documented
   no-op); material → a sanctioned, attributed baseline move.
7. **Manifest extension + re-record** — add `staticmaps.nc` + TOML +
   `output.csv` (discharge) fingerprints to `dev/baseline/manifest.json` (wf1's
   slice today is only 3 size-only PNGs + config), then re-record from the chosen
   config in a clean project dir with a freshness check on every target.
   Document the discharge move in `dev/tasks/t260719a` (or a `baseline_diffs.md`).

### Consequences

*Positive*
- wf1 hydrology pins its snow/glacier/soil/vegetation constants to a documented
  reference set under stable CSDMS names — correct and reproducible across
  basins, not silently dependent on Wflow.jl default drift.
- The manifest gains `staticmaps.nc`/TOML/discharge coverage, closing the gap
  where a model-parameter or discharge change was invisible to `check_baseline`.
- Both silent-failure modes (accepted-but-unwritten; stale blessing) become
  asserted contracts.

*Negative*
- A one-time, intentional baseline move on any parameter whose reference value
  differs from the 1.x default (size measured, not assumed). R1/R2/R6's
  "preserve the baseline" rule does not apply — this task is explicitly allowed
  to move wf1's slice with a documented diff.
- Larger build config surface (13 explicit parameters) to maintain against
  future hydromt_wflow renames.

*Neutral*
- The restore/adopt classification is validated on the reference test basin;
  its discharge *immateriality* is basin-specific. The cross-basin correctness
  argument — not test-basin sensitivity — is what justifies restoring the
  snow/glacier constants, and that argument is recorded here so a future reader
  does not "re-drop" them after seeing a null test-basin diff.
- `KsatHorFrac` is unchanged; this task does not revisit it.

### Alternatives considered

- **Adopt Wflow.jl 1.x defaults wholesale (keep the M2b state).** Minimal config;
  rides engine improvements automatically. Rejected: it makes the fork's
  hydrology silently dependent on Wflow.jl default drift and diverges from the
  Deltares reference precisely on snow/glacier basins — a divergence the current
  test basin cannot surface, so it would ship as a latent cross-basin defect.
  Preferable only if CST abandoned reference continuity in favor of "always
  latest engine defaults."
- **Restore only where the 1.x default differs (omit params equal to the
  default).** Smallest correct config. Rejected as more fragile: it requires
  enumerating Wflow.jl's defaults — a moving, version-specific, sparsely
  documented target — to decide what to omit; pinning all reference values
  explicitly is simpler and drift-proof. Preferable if config minimalism were
  the priority and the engine defaults were stable and documented.
- **Drop any parameter immaterial on the test basin.** The literal "measure then
  decide per basin" reading. Rejected: test-basin immateriality is an artifact
  of inactive snow/glacier processes there, so this would wrongly drop
  cross-basin-relevant constants. Measurement sets the *size* of the move and
  blesses it; it does not decide whether to restore.

### Related

- Task `t260719a` (`dev/TODO.md`); campaign tracker
  `dev/working/2026-07-21_pre-r6-followups.md`.
- M2b handoff decision #3 (`dev/phase-1/m02b/handoff.md`) — original drop + the
  first CSDMS mappings; `dev/phase-1/m02b/baseline_diffs.md`.
- Baseline-manifest scope/staleness context: `dev/followups.md`
  (§ cross-cutting — baseline manifest integrity) and `dev/r01/baseline_diffs.md`.
- Roadmap cross-cutting rule "every milestone preserves the M1 baseline unless
  intentionally changing behavior" (`dev/roadmap.md`) — this task is a sanctioned
  wf1-slice move.
- Source: `config/wflow_build_model.yml` (`setup_constant_pars`);
  `hydromt_wflow/naming.py` (CSDMS lookup).
