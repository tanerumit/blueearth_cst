# R9 — WF3 v2.0: climate experiment redesign — scoping intake

**Status.** Scoping record, authored 2026-08-01 via `design-scoping` from the
direction the owner approved in the prior session. The § Approved architecture
below is a **fixed anchor** for the design cycle; the § Open questions are what
the design-review-loop (and the owner rulings marked inside them) must settle.
Design-cycle start is **user-gated** — do not start without the owner's go.

**Provenance.** Phase 5 workflow rework, second milestone: R8 reshaped wf2
(`dev/workflows/wf2-climate-analysis-v2-*`); this milestone does the same to
`Snakefile_climate_experiment` (wf3). Milestone id **R9** continues the `R##`
series across the phase per the roadmap's numbering rule (proposed; confirm at
design start). Commit prefix `r09:`; dev artifacts under `dev/workflows/`
following the R8 precedent.

## Why a ground-up redesign (the evidence, all measured or code-grounded)

The inner `RLZ_NUM × ST_NUM` sweep has outgrown the file-per-wildcard DAG:

1. **The cost is session warm-up, not process startup.** P3-3's measured
   decomposition (`dev/p33/batching-results.md`): per-member fixed cost
   `F ≈ 24 s`, first run in a session `S_cold ≈ 92 s`, runs 2..B `S_warm ≈
   35 s`. A persistent worker that loads Wflow once and stays warm captures the
   `S_cold → S_warm` discount for **every** member; LPT batching captures it
   only within a batch. Pool beats batching at scale, ties on the fixture.
2. **The batch construct carries structural debt.** Rule 3.10 is a parse-time
   loop generating anonymous `run_wflow_batch_<b>` rules; logs/benchmarks are
   keyed by batch id, not member; C5 failure isolation is DEGRADED to batch
   granularity (GN-4: one failed member deletes B−1 sibling CSVs and blocks
   rule 3.11 sweep-wide until re-run).
3. **The disk-aware batch-size default is unsolvable in the current shape.**
   `dev/followups.md` § Post-P3-3: the §6.1 disk ceiling needs a per-run
   forcing-size estimate that cannot exist at parse time (the forcing NCs are
   `temp()` and not yet written). A ledger-driven sweep with forcing built and
   deleted per member caps peak temp disk at `p × 1` forcing by construction —
   the open problem is dissolved, not solved.
4. **Rule 3.06 writes all realizations in one job.** No parallelism across
   realizations, and any re-run touching a `temp()` intermediate cascades
   through 3.06's all-realization output into every batch (GN-4 incidental
   finding; re-measured by the `--notemp` capture: one intermediate target →
   19 jobs). `--forcerun` of one batch re-runs the whole sweep.
5. **Baseline NCs are `temp()`**, so the cascade above is structural: every
   partial re-run pays the full generation chain again.

## Approved architecture (fixed anchor — owner-approved in the prior session)

Snakemake stays the outer skeleton over **4 scientific stages**; the
`snakemake all --configfile …` entry and config-driven contract survive. The
inner RLZ×ST sweep leaves the file-per-wildcard DAG:

1. **Extract** — the keyed historical store, unchanged (R07 B1; one producer
   declared identically in wf1/wf3).
2. **Generate** — one job **per realization** with explicit per-realization
   seeds; baseline `rlz_<n>_cst_0.nc` **not** `temp()` (kills the 3.06
   cascade; enables cross-rlz parallelism).
3. **Sweep** — **one rule**. Emits a members manifest (member id, rlz, dT, dP,
   precip_variance, seed, config digests) plus a per-member ledger; a
   persistent Julia worker pool loads Wflow once and pulls members off a
   queue; per member: build forcing on demand (perturb + downscale, today's
   3.07 + 3.09, fused back-to-back), run wflow, write the indicator CSV,
   update the ledger, delete the forcing. Peak disk = `p × 1` forcing.
   Replaces the parse-time batch rules and the disk-aware `batch_size`
   followup.
4. **Reduce** — response surface from the ledger; keep `Qstats.csv` /
   `basin.csv` (HM-7 surface), add a tidy long-format table with
   `(rlz, dT, dP, indicator)` coordinates.

Drift guard: rule 3.00b's mechanism simplifies to — the members manifest
records the wf1/wf2 snapshot digests; the sweep runner verifies them at start.

Direction ≈ the `cst-run-control` skill's contract (manifest + ledger + resume
semantics), at a depth to be settled by OQ-2.

## New evidence from this scoping pass (not in the prior session)

- **[E1] The precip_variance axis is likely inert today.** In the weathergenr
  source (`~/workspace/weathergenr/R/climate_perturbations.R`),
  `apply_climate_perturbations` defaults `scale_var_with_mean = TRUE`, under
  which `precip_var_factor` is **ignored** and the variance factor is derived
  as `mean_factor²`; the warning announcing this prints only under
  `verbose = TRUE`. `impose_climate_change.R` passes `precip_var_factor =
  cst_data$precip_variance` but does **not** pass `scale_var_with_mean` (and
  not `verbose`), so under this version the WG-2 `precip_variance` column
  never reaches the output. **Caveat:** the *installed* package (via
  `remotes::install_github`) must be pinned and checked against this checkout
  at design start — an older installed build may predate the parameter and
  behave differently. Either way this is a scientific decision the redesign's
  manifest schema depends on (the member tuple carries `precip_variance`), so
  it needs an owner ruling (OQ-1).
- **[E2] Perturbation is deterministic in practice; generation seeding is
  joint.** 3.07 passes no `seed` to `apply_climate_perturbations`; its
  stochastic branches (occurrence resampling via `sample`/`rgamma`) are
  inactive because no occurrence factor is supplied, and the R5 commit-9
  characterization measured bit-identical re-runs. 3.06 calls
  `weathergenr::generate_weather` **once** with a single config seed and
  `n_realizations = RLZ_NUM` — all realizations draw from one RNG stream, so
  per-realization jobs **cannot** reproduce today's realizations. Stage 2 is
  value-changing by construction (grounds OQ-5/OQ-6).
- **[E3] t260720a is fixed.** The variance max-reads-min bug in
  `prepare_cst_parameters.py` is closed
  (`tests/test_prepare_cst_parameters.py::test_precip_variance_grid_uses_max_endpoint`);
  the grid genuinely spans `variance.min..max`. Only E1 stands between the
  config axis and the output.

## Constraints (standing; not new to this milestone)

- **CST automation scope** (`AGENTS.md` Hard Constraints): no re-engineering of
  weathergenr internals, hydromt data handling, or Wflow physics. The
  spatial_ref workaround block in `generate_weather.R` stays until the
  upstream fix lands. E1 is a *call-site* decision (which arguments we pass),
  in scope; changing how the perturbation algorithm works is not.
- **New dependencies need explicit owner approval**
  (`new-dependency-requires-approval`). The worker pool should be built on
  what the env already has (Julia via juliaup, stdlib IPC); anything beyond
  that is an ask.
- **netCDF stays the interchange format**; per-member forcing remains
  transient (now deleted by the runner rather than Snakemake `temp()`).
- **Seam contracts are the acceptance frame, with deltas enumerated.**
  WG-1/WG-2 semantics, WG-4 shape, HM-1..HM-5 and HM-7 (incl. the
  gauge-column-identity invariant and the `Q_` prefix reliance in the
  reduction) carry over as acceptance criteria. The design must table which
  pinned surfaces survive verbatim, which change home (e.g. WG-2's per-member
  CSV grid → the members manifest; WG-3's per-member config YAMLs → member
  specs), and which artifacts become runner-transient (WG-4 perturbed NCs,
  WG-6 forcing, HM-6b states) — a contract-doc update lands with the
  milestone, not after it.
- **Web-app independence**: no decision may be gated on how CST-API/frontend
  consume artifacts; `Qstats.csv`/`basin.csv` stay because *this repo's*
  contract (HM-7) names them.
- **Worktree discipline**: implementation runs in its own worktree
  (`worktree_policy: always`); pushes are a separate explicit decision.
- Naming per `dev/conventions/naming.md`; a member-id vocabulary is a new
  naming surface the design must register there.

## The stated tradeoff (scope it as a designed milestone, not a refactor)

Moving the sweep out of the file-per-wildcard DAG moves **incrementality out
of Snakemake and into our ledger code**. What Snakemake gave for free — resume
after crash, partial re-run, output/input freshness, `--dry-run` visibility of
pending work, stale-output deletion — becomes our responsibility inside the
sweep rule: ledger crash consistency (a member killed mid-write must re-run,
not read as done), atomic ledger updates under `p` concurrent workers,
idempotent member execution, config-change invalidation (the manifest's config
digests are the freshness boundary Snakemake no longer sees), and honest
`--dry-run` behaviour for a rule whose internal work is invisible to the DAG.
This is exactly the territory `cst-run-control` formalizes, and it is the
reason this is a **designed milestone with its own failure-injection gates**
(GN-4-style: kill a worker mid-member, corrupt a ledger row, change a config
mid-sweep), not an incremental refactor of rule 3.10.

## Open questions for the design cycle

Each with grounding and a recommendation; **owner rulings** are marked — the
rest are design-loop decisions.

1. **precip_variance semantics [OWNER].** Given E1: (a) is the variance axis
   *intended* to be active (pass `scale_var_with_mean = FALSE`), or is
   variance-scales-with-mean the intended science and the config axis should
   be removed/repurposed? (b) Porting 3.07 to Python would need a tolerance-0
   parity gate against the R implementation (Gamma-QM with `mme` fit,
   transient ramps, PET recompute) — high effort, high risk, and the R stage
   is ~6 % of sweep wall. **Recommendation:** keep the R step and invoke it
   per member from the worker (the prior session's fallback becomes the
   primary); the per-member `Rscript` cost is bounded and the parity question
   dissolves. Revisit a port only if per-member R invocation measures as a
   real cost. The E1 ruling is needed regardless of porting.
2. **Ledger contract depth.** Adopt `cst-run-control` as-is, subset it, or go
   repo-local? The full contract (compare-and-set claims, fencing tokens,
   content-addressed staging, conformance vectors) is service-grade machinery
   for a single-machine sweep. **Recommendation: a named subset** — adopt the
   vocabulary and semantics that carry the risk (immutable intent/manifest vs
   mutable state/ledger; canonical config digests; append-only attempts;
   checkpoint-reuse conditions; quarantine-before-resume), skip the
   distributed-coordination layer, and record the mapping so a future
   conforming adapter is a lift, not a rewrite.
3. **Member naming.** Coordinate-bearing ids (`t+2.0_p0.85`) vs index + mapping
   table. **Recommendation: index-based** (`cst_<m>` per realization, `cst_0`
   reserved baseline — today's vocabulary, naming.md §4) with coordinates
   carried in the manifest and the tidy long output. Floats in path segments
   invite formatting/precision drift, and the manifest exists precisely to be
   the id→coordinate record.
4. **Reduce-with-holes on member failure [OWNER].** Today one failure blocks
   the reduction sweep-wide (GN-4). A ledger-driven reduce *could* emit a
   response surface with holes. **Recommendation:** default **fail loud**
   listing the failed members (a silently sparse response surface distorts
   exactly the robustness judgment CST exists to inform), with an explicit
   `allow_partial` config key that produces the surface plus a
   machine-readable completeness record. Needs an owner posture call.
5. **Per-realization generation vs seed reproducibility.** Given E2, choose
   the per-rlz seed scheme: derive per-realization seeds deterministically
   from a master seed + realization index, recorded in the manifest.
   `generate_weather` already accepts `seed` + `n_realizations = 1` per call.
   Old realizations are not reproducible under the new scheme — that is a
   documented re-baseline (OQ-6), not a defect. Design should verify
   weathergenr's per-call output naming supports the per-rlz invocation
   cleanly.
6. **Migration parity strategy + baseline manifest.** End-to-end value
   identity is **impossible** (E2), so the R8 discipline applies: per-stage
   falsifiers written before code, characterized diffs before any re-record.
   Stages that *can* be held identical are proven so (perturb: same R code on
   same inputs, tolerance 0; wflow: warm-session ≡ cold-process byte identity
   is already measured, GN-2; reduce: same reduction on same member CSVs).
   The generation change is characterized statistically (same generator, new
   seeds — distributional equivalence, not byte identity). Manifest: wf3's
   3-row slice re-records **exactly once** at the end; the design decides
   whether the tidy long table joins the manifest. Baseline-provenance
   stamping (R7-21) already guards the fixture-sharing risk.
7. **Pool boundary: Julia-side queue vs Python orchestrator over warm
   workers.** **Recommendation: Python orchestrator.** The sweep rule runs a
   Python runner that owns the manifest, the ledger (single writer), member
   scheduling, and the R/downscale steps; it spawns `p` persistent Julia
   workers that each load Wflow once and serve `run this TOML` requests over
   a line-protocol (stdin/stdout JSON), returning per-member status + timing —
   `run_wflow_batch.jl` is the seed of that worker loop. A Julia-side queue
   (Distributed.jl) would put scheduling next to the ledger's single-writer
   logic's *wrong* side and grow the Julia surface we maintain. Worker crash
   handling (respawn, member marked failed after N attempts) is part of the
   design's failure-injection gates.

## Success criteria

1. **Entry + stage contract:** `snakemake all -s Snakefile_climate_experiment
   --configfile …` works unchanged; the DAG shows the 4 stages; dry-run stays
   clean and meaningful (pending-member visibility stated honestly).
2. **Resume correctness, measured not asserted:** kill the sweep mid-flight →
   re-invoke → only unfinished members run; ledger shows a coherent attempt
   history; a corrupted/partial ledger row quarantines rather than passes.
3. **Blast radius = 1 member:** a failing member costs itself only; completed
   sibling indicators survive; the reduction is blocked (or partial per OQ-4's
   ruling) with the failure named per member.
4. **Peak temp disk = `p × 1` forcing**, sampled during a sweep (the GN-3
   method), independent of sweep size.
5. **Per-member visibility:** logs, timing, and status per member (better than
   the batch-id granularity P3-3 accepted).
6. **Drift guard preserved:** wf1/wf2 snapshot digests recorded in the
   manifest and verified at sweep start; the 3.00b failure modes still fail
   loud.
7. **Seam acceptance:** the WG/HM validator suite (adjusted per the enumerated
   contract deltas) green; HM-7 outputs byte-stable for unchanged inputs; the
   gauge-column-identity invariant holds.
8. **Performance floor:** at fixture scale the pool is **not worse** than
   P3-3's batching (399–400 s class; ties expected per the estimator); the
   at-scale advantage is stated as a model from the measured F/S_cold/S_warm
   terms, not claimed as measured, unless a production-sized sweep is run.
9. **Migration honesty:** per-stage parity/characterization evidence (OQ-6),
   one manifest re-record, a user-facing migration note (R8's
   `docs/migration-r08-wf2.md` precedent).

## Cut (YAGNI) / non-goals

- The keyed historical store (R07 B1) — untouched.
- No CMIP coupling of the experiment (bottom-up posture; wf2 stays overlay).
- No weathergenr/hydromt/Wflow internal changes; upstream defects stay in
  `dev/followups.md` § R5.
- No wf1/wf2 changes beyond what guard-digest recording needs.
- No multi-node/distributed execution; the pool is single-machine (`-c N`).
- No PackageCompiler sysimage (stays dormant per P3-3's adjudication — it
  attacks `F`, which is not where the cost is).
- No GUI/platform surface changes (`run_workflows.py` wrapper contract,
  `workflows:` config sections unchanged).

## Handoff

Next step (user-gated): a `design-review-loop` run — full variant; the sweep's
crash/resume semantics and the E1 science ruling are exactly the kind of
findings the external rounds earn their cost on — with this intake as scope
authority. The design decides: the manifest/ledger schema and its
`cst-run-control` mapping (OQ-2), the worker protocol and process topology
(OQ-7), the member lifecycle state machine and failure-injection gate set, the
contract-delta table, the per-stage falsifier plan (OQ-6), and the commit
sequence. Then task-brief → implementation, R8-style.
