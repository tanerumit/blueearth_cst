# BlueEarth Climate Stress Test toolbox

[![CI](https://github.com/tanerumit/blueearth_cst/actions/workflows/ci.yml/badge.svg)](https://github.com/tanerumit/blueearth_cst/actions/workflows/ci.yml)

> [!NOTE]
> **Fork status.** This is a personal fork of
> [Deltares/blueearth_cst](https://github.com/Deltares/blueearth_cst). Three
> planned phases are complete:
>
> - **Phase 1 — Foundation** (sealed, `v0.2.0-alpha`): replication baseline,
>   pixi-based env, library upgrades (hydromt 1.x, Wflow.jl 1.0.x), unit-test
>   coverage.
> - **Phase 2 — Refactor** (sealed 2026-07-23, R1–R6): modularity contracts,
>   naming conventions, one milestone per workflow, then the structural refactor
>   that moved `src/` to the `blueearth_cst` package and split `config/` into
>   `workflows` / `catalogs` / `templates`.
> - **Phase 3 — Usability & flexibility** (sealed 2026-07-25, P3-1…P3-3):
>   project/experiment structure, model-independent climate analysis, model-swap
>   interchange contracts, and performance work (the wf3 stress-test sweep is
>   ~35 % faster, value-identical).
>
> Phase 4 is open; CI was its first item. `dev/roadmap.md` is the authoritative
> status record — this note summarises it and may lag. See also `CHANGELOG.md`,
> which tracks releases rather than milestones.

The BlueEarth Climate Stress Test toolbox (`blueearth_cst`) is a free,
open-source toolkit for interactive climate risk assessment based on bottom-up
analysis principles. It enables end-users to:

- Explore the range of hydro-climatic uncertainty in a chosen geographic area,
  including natural variability and climate-change signals.
- Design and execute climate stress tests against user-defined thresholds and
  metrics.
- Assess the plausibility of identified vulnerabilities using climate model
  projections — i.e. estimate how sensitive a chosen metric is to climate
  change.
- Visualize results for non-specialist audiences.

The toolbox is part of the [BlueEarth](https://blueearth.deltares.org/)
initiative and uses [weathergenr](https://github.com/Deltares-research/weathergenr) as
its weather generator and [Wflow](https://github.com/Deltares/Wflow.jl) for
hydrological modelling.

![image](docs/_images/CST_scheme.png)

## Installation

`blueearth_cst` is a Python + R + Julia toolbox. Python and R dependencies are
managed with [pixi](https://pixi.sh/); Julia and Wflow.jl are managed via the
standard `Project.toml` / `Manifest.toml`. A single `pixi run install` task
wires both layers together.

For a step-by-step walkthrough of a fresh install, see `docs/install.md`.

### Prerequisites

1.  **pixi** (manages Python 3.12 + R 4.4 via conda-forge; the exact pins live
    in `pixi.toml` — R is held at 4.4 because conda-forge's 4.5 `r-waveslim`
    build is broken on win-64).

    Windows (PowerShell):

    ```powershell
    iwr -useb https://pixi.sh/install.ps1 | iex
    ```

    Or via winget: `winget install prefix-dev.pixi`. Restart your shell after
    install.

2.  **Julia 1.11.7** via [juliaup](https://github.com/JuliaLang/juliaup).
    conda-forge has no win-64 Julia build, and Wflow.jl 1.0.x deadlocks under
    Julia 1.12. The exact patch is pinned: every Julia call the toolbox makes
    carries the `+1.11.7` selector, so any other 1.11.x fails to start. After
    installing juliaup:

    ```console
    juliaup add 1.11.7
    ```

    Verify with `julia +1.11.7 --version` (expect `1.11.7`). No
    `juliaup default` is needed — the selector picks the version.

3.  Clone the repo:

    ```console
    git clone https://github.com/tanerumit/blueearth_cst.git
    cd blueearth_cst
    ```

### Install

```console
pixi install         # Python + R toolchain (conda-forge)
pixi run install     # weathergenr (R) + Wflow.jl (Julia)
```

The first command installs everything declared in `pixi.toml` into a local
`.pixi/` env. The second runs `dev/scripts/install_weathergenr.R` (installs
`Deltares-research/weathergenr@v2.0.1`) and
`julia +1.11.7 --project=. -e 'using Pkg; Pkg.instantiate()'` (locks Wflow.jl
and ~130 transitive Julia deps from `Manifest.toml`).

To activate the env in your shell:

```console
pixi shell
```

### Docker

> [!WARNING]
> **Not supported in v0.2.0-alpha.** Docker / Linux end-to-end validation is
> **deferred** in this fork — see "Deferred: Linux replication" in
> `dev/roadmap.md`. The `Dockerfile` builds against the pixi env but is not
> exercised in CI. Docker support will be re-introduced in a later Phase 2
> milestone.
>
> The instructions below describe the **v0.1.0-alpha** (upstream conda-based)
> Docker workflow and remain valid for users of that release. They do **not**
> apply to v0.2.0-alpha or later pixi-based releases.

A pre-built image of the v0.1.0-alpha conda-based stack remains available at
`containers.deltares.nl/CST/cst_workflows:0.1.0`:

```console
docker pull containers.deltares.nl/CST/cst_workflows:0.1.0
```

## Running

The five workflows separate historical characterization, generation, model
construction, simulation and projection analysis:

| Entry point | Id | Purpose |
|---|---|---|
| `analyze_climate.smk` | wf0 | Optional model-free historical climate analysis |
| `build_model.smk` | wf1 | Build Wflow-SBM and run historical forcing |
| `analyze_projections.smk` | wf2 | CMIP6 plausibility overlay |
| `generate_scenarios.smk` | wf3 | Generate and retain a scenario collection |
| `simulate_system.smk` through `scripts/simulate_system.py` | wf4 | Simulate a ready collection or reduce retained responses |

Generation and model construction are independent prerequisites of simulation.
Projections never drive generation. Run WF0 alone when selecting historical
forcing; otherwise run it first or omit it.

WF0 compares only variables each source actually provides. A CHIRPS source
added only as a comparison candidate therefore reads and stores precipitation
only. When CHIRPS is the selected pipeline source, the shared store is instead
enriched with ERA5 temperature, radiation and pressure plus orography because
WF1 and WF3 require the complete forcing contract.

WF0 and WF1 share one canonical source-plot producer. Figures under each
historical store's `plots/` use source-local scales and are reused when switching
workflows with unchanged inputs and settings. WF0's `comparison/` figures put
sources on common axes. The former `shared_plot_scales.json` is no longer used;
existing figures may refresh once after this change, then subsequent runs reuse
them. Existing run files are not automatically deleted.

### Configuration

Start from `test_case/project_config_rapid.yml` for execution checks. A project
file has five closed `{enabled, config_path}` stanzas. Each settings file sits
beside it; `config_path` resolves from the project file, while ordinary paths
resolve from the working directory. Shared basin, climate and model keys stay
in the project file. Production `project_dir` belongs outside the checkout.

`project.catalog` accepts one catalog path or an ordered list. HydroMT loads
lists in order, so a later project-owned catalog can replace a named source
without modifying an upstream catalog. The rapid config uses this mechanism to
load `config/catalogs/deltares_era5_daily_zarr.yml` after its original
`deltares_data.yml` base. The override gives only `era5` a P-drive root; all
other sources retain the original base catalog and root. Its `era5` entry uses
`raster_xarray` with Zarr-compatible options only and covers 1950-01-02 through
**2023-02-01**. ERA5 extraction refuses requested dates outside advertised
catalog coverage rather than silently returning the overlap. The baseline
config remains on its existing catalog so the numerical reference is
unchanged.

Generation owns realization count, simulation window, perturbations, generator
settings, seed and unit capacity. Simulation owns `experiment_name`, the required
`operation`, optional `scenario_collection: {manifest_path: ...}`, compute controls
and metric selection. Existing seeds are preserved by
`scripts/migrate_project_config.py`; new `auto` seeds are independent of experiment
names and identifier capacity. See [configuration migration](docs/migration-config-shape.md).

### Commands

Activate `pixi shell`, or prefix commands with `pixi run`:

```console
python scripts/run_workflow.py analyze_climate --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py build_model --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
python scripts/run_workflow.py analyze_projections --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3 --keep-going
# Enable only generate_scenarios in this config to run WF3 alone.
python scripts/run_workflows.py --config <wf3-only-project-config.yml> --project-dir <project-dir> --cores 3
python scripts/simulate_system.py --config test_case/project_config_rapid.yml --target all --cores 3
```

Or run all enabled workflows in that fixed convenience order:

```console
pixi run python scripts/run_workflows.py --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3
```

Preflights run immediately before their consumer, after preceding producers.
Generation uses the owned all-workflow runner, which may be configured with only
WF3 enabled. Simulation must use its dedicated runner or
the all-workflow runner; bare `simulate_system.smk` invocation is unsupported.
`--dry-run` shows a partial DAG until a missing source or metric checkpoint has
resolved its content identity. Each workflow executes once per invocation.

Snakemake flags go after a `--` sentinel and are appended verbatim to every
invoked workflow — this is how you pass `--rerun-incomplete`, `--dry-run`,
`--notemp`, `--unlock` or `-p`, since the wrapper's own flags are only
`--config`, `--cores` and `--simulation-target`:

```console
$ pixi run python scripts/run_workflows.py \
    --config test_case/project_config_baseline.yml \
    --project-dir test_case/test_local \
    -- --rerun-incomplete
```

### Retained results and metrics-only

Collections live under `scenarios/collections/<collection_id>/`, selected by the
exact `scenarios/requests/<generation_request_id>/request.json` or an explicit manifest.
Simulation never creates missing collections. A missing or stale plan names the
generation command required to resolve it; no directory scan or latest fallback
is used.

Each `experiments/<experiment_name>/` retains `config/simulation.json`, its native
`hydrology/wflow/output/run_<run_id>.csv` responses and
`_engine/response_inventory.json`. Metric sets live in
`results/metric_sets/<metric_set_id>/`; their tables contain
`metric,location,unit_id,value`, joined through `unit_index.csv` to scenario rows.
Model-grid forcing and per-run catalogs are temporary. Collection forcing and
native responses are durable.

To reduce existing responses, set `operation: metrics-only` and the existing
`experiment_name` in the simulation settings file, then run:

```console
pixi run python scripts/simulate_system.py --config <project-config> --target metrics
```

The all-workflow runner accepts `--simulation-target metrics` for this operation;
disable other workflows when only retained reduction is wanted. Default target
`all` never infers an operation from files. Metrics-only requires no live model,
generation inputs or Julia. Changed simulation inputs require a new experiment;
changed metrics select a new immutable metric set. See
[retained handoffs](docs/wf3-retained-handoffs.md),
[workflow migration](docs/migration-workflow-names.md) and
[the post-R12 project-tree migration](docs/migration-post-r12.md).

### Logs and DAGs

WF0/WF1/WF2 retain their project-level logs and provenance records. Generation
parts are scoped by generation request under `logs/_parts/generate_scenarios/`;
simulation parts are scoped by experiment under `logs/_parts/simulate_system/`.
Benchmark parts use the same scope beneath `benchmarks/_parts/`. The all-workflow
runner retains an invocation record under `config/runs/_engine/invocations/`.

```console
# WF3's owned dry run shows the source-preparation DAG.
pixi run python scripts/generate_scenarios.py --config test_case/project_config_rapid.yml --project-dir test_case/test_rapid --cores 3 -- --dry-run
pixi run python scripts/plot_workflow_dag.py -s simulate_system.smk --configfile test_case/project_config_rapid.yml
```

The graph helper applies the shared simulation target validator. Graphs live
under the project's `logs/dag/`; simulation graphs include the experiment name.

## Testing

The test suite has three explicit tiers. For normal development, run the fast
tier; it keeps all pure/unit coverage and excludes only tests that invoke real
Snakemake workflows or require fresh Python processes:

```console
$ pixi run test-fast
```

Run the workflow/process contracts after changing a Snakefile, a workflow
boundary, or process-isolated behaviour:

```console
$ pixi run test-contract
```

The authoritative full non-integration suite remains the unfiltered run. The
Pixi task is only a memorable alias; bare `pytest tests/` has the same meaning:

```console
$ pixi run test-full
$ pixi run pytest tests/
```

`workflow_contract` marks real Snakemake CLI/API/DAG and lifecycle checks;
`process_isolation` marks non-Snakemake proofs that need fresh interpreters. The
markers partition execution cost, not coverage: the full tier runs both. In the
August 2026 clean-Windows measurement, the fast tier ran in about one minute and
the contract tier in about five minutes (roughly 1,070 tests total).

Notes on what the suite does and does not cover:

- Tests that need the untracked `test_case/test_local` fixture tree **skip**
  when it is absent, as do three end-to-end workflow tests that are opt-in
  behind `--run-integration`. Run `pytest -rs` to see every skip reason. The
  August 2026 clean-checkout profile had 31 skips: 28 fixture-dependent checks
  and the three opt-in integrations.
- `dev/scripts/check_baseline.py check` and `dev/scripts/semantic_tree_diff.py`
  compare a produced output tree against a recorded baseline. They are
  **local-only gates** — they need that fixture tree, so CI cannot run them. **A
  green CI badge does not mean the baseline was checked.**
- CI (`.github/workflows/ci.yml`) runs the unit suite on `ubuntu-latest` and
  `windows-latest` for every push to `main` and every pull request.

## Documentation

User-facing:

- **Notebooks** — Jupyter notebooks explaining each workflow live under
  `docs/notebooks/` (inherited from the [upstream
  repository](https://github.com/Deltares/blueearth_cst/tree/main/docs/notebooks)).
- **HydroMT references** — `docs/` also contains HydroMT architecture and
  user-guide content.

Fork-specific (development):

- `dev/roadmap.md` — milestone roadmap: what each phase set out to do and how it
  landed.
- `dev/reference/git-conventions.md` — branch / tag inventory plus the
  branching, tagging, and commit-message conventions.
- `docs/install.md` — step-by-step install walkthrough.
- `dev/milestones/phase-1/` — sealed foundation milestone artifacts (audits,
  plans, baseline diffs).
- `dev/milestones/r01/` … `dev/milestones/r06/` — sealed Phase 2 milestone
  designs and review records (modularity contracts, naming, the three workflows,
  structural refactor).
- `dev/milestones/p31/`, `dev/milestones/p32a/`, `dev/milestones/p32b/`,
  `dev/milestones/p33/` — sealed Phase 3 milestone designs, review records and
  evidence notes.
- `dev/tasks/` — the open backlog, with closed items retained and dated.
- `CHANGELOG.md` — release history (release-level; milestone detail lives in
  `dev/roadmap.md`).

## Publishing

### Docker

> [!WARNING]
> **v0.1.0-alpha only.** The build / tag / push instructions below describe the
> upstream Deltares container registry workflow for the conda-based stack.
> Docker publishing is **still deferred** in the pixi-based fork — see
> "Deferred: Linux replication" in `dev/roadmap.md`. It was *not* re-introduced
> during Phase 2 or 3, and is not currently scheduled. It remains blocked on the
> same thing as Linux replication (no Linux machine), though CI's green
> `ubuntu-latest` leg now shows the linux-64 half of `pixi.lock` resolves and
> installs, which removes the largest unknown.

The entire workflow is contained in one Docker image. Build it:

```console
docker build -t cst-workflow:0.0.1 .
```

Tag and push it under a new `<<Tag>>`:

```console
docker login -u <<deltares_email>> -p <<cli_secret>> https://containers.deltares.nl
docker tag cst-workflow:0.0.1 containers.deltares.nl/CST/cst_workflows:<<Tag>>
docker push containers.deltares.nl/CST/cst_workflows:<<Tag>>
```

## License

Copyright (c) 2021, Deltares.

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program. If not, see <https://www.gnu.org/licenses/>.
