# Expert model revisions — intake

Date: 2026-09-28
Target: BlueEarth CST, branch `feat/wflow-improvements`, session-1.
Genre: software workflow design (run-state genre: `decision-record`).

## Request and confirmed framing

User request: improve WF1's automated model builder to allow an expert to update a poorly performing Wflow model, simulate and reevaluate it, repeat as needed, and export results while keeping workflow records and hashes consistent. The user requested a design proposal, accepted named full model revision directories, then requested a design document using `design-review-loop`. In scoping, the user confirmed that v1 must accept both HydroMT update recipes and direct edits to a copied Wflow model.

## Problem and scope

The current WF1 builds and evaluates one mutable model root. Expert changes after evaluation have no defined revision lifecycle or safe dependency boundary. WF4 binds its experiments to the model root and records a runtime-input digest; revisions must integrate with that binding without mixing old results and new model bytes.

Scope: initial automated assessment; creation, registration, evaluation and selection of full model revisions; recipe and direct-edit provenance; revision and evaluation identity; WF1/WF4 integration; drift detection, recovery, migration and validation. The document proposes behavior and contracts, not implementation.

## Constraints and decision criteria

- Retain an unattended automated WF1 path and the current model as a usable starting point.
- A revision is a complete runnable model directory with explicit parentage. Both HydroMT recipe updates and direct edits to the copy are allowed before sealing.
- Completed revisions and evaluations must be attributable to exact model bytes; existing WF4 experiments must continue refusing changed inputs.
- Respect HydroMT/Wflow conventions; do not reimplement their model internals.
- Prefer a human review boundary between invocations over a paused Snakemake job.
- Preserve current baseline behavior unless revision mode is requested. Compare alternatives by safety, reproducibility, operator effort, storage, and impact on existing workflows.

Success: an expert can evaluate several revisions, compare their recorded results, select one for future WF4 experiments, and detect changed or stale model/evaluation inputs before reuse. An interrupted update does not present a partial revision as complete.

Non-goals: automatic parameter optimization; declaring scientific calibration success from a digest or improved fit metric; changing WF3 scenario generation; web/API UI; copying a separate model into every WF4 experiment.

## Derived-artifact register

After G2, derive implementation task brief(s), current WF1 rule reference, user workflow documentation, config examples, and any migration/path map from the accepted design. Do not edit these during review.

## Evidence register

| Premise | Source | Exact observation | Precision | Reproduction | Confidence |
|---|---|---|---|---|---|
| WF1 has an in-place model writer chain and a terminal reader anchor. | `build_model.smk` rules 1.06–1.09; ADR 0004 | Rule 1.09 writes `.model_final`; model readers declare it through `ancient()`. | Source inspection, not runtime measurement in this run | Read lines 616–824 and `tests/test_model_root_ordering.py` | High |
| WF1's run record is current-only and its hashes are not a model-byte identity. | `blueearth_cst/model/copy_config_files.py` | Its README text says the record is replaced and `configuration_inputs_sha256` covers config, toolbox, lock files, referenced inputs, but not scientific data identity. | Source inspection | Read `_RUNS_README` | High |
| Model digest uses TOML and its pointer-derived runtime inputs. | `blueearth_cst/shared/model_digest.py` | `model_file_set()` walks TOML path keys; `model_digest_entries()` hashes listed files or an absence marker. | Source inspection | Read those functions | High |
| WF4 currently binds one fixed model root and guards against drift. | `blueearth_cst/experiment/rules/simulate_and_metrics.smk`; `write_model_reference.py` | `basin_dir` is fixed to `<project>/models/hydrology/wflow`; the reference records relative path, digest and inputs; changed reference raises. | Source inspection | Read lines 32–88, 137–199; `write_model_reference.py` | High |
| Direct edits can be captured completely by the existing pointer-derived digest. | Hypothesis | Not established: model bytes relevant to build provenance or later updates may lie outside TOML runtime pointers. | Requires a proposed seal-inventory probe and review | Compare full revision inventory against runtime digest after representative direct edits | Open |
| HydroMT update into a separate model root preserves an intact parent. | Vendored `docs/hydromt-wflow/user-guide.md` | Guide documents `hydromt update ... -o <updated_model>`; filesystem behavior for this repo's invocation remains unprobed. | Documentation, not execution | Representative dry-run/update fixture before implementation | Medium |

## Gate materialization

Current checks: `tests/test_model_root_ordering.py`, `tests/test_model_reference.py`, `tests/test_cli.py`, and a Snakemake dry-run against `test_case/project_config_rapid.yml` are available. They do not yet cover revision publication, direct-edit inventory, selection, or WF4 binding; the design must specify new falsifiers. Before implementation changes numeric outputs, preserve or regenerate the baseline using the repository's documented baseline workflow. No pre-change revision artifact exists because revision mode is new.

## Domain-content flag

Yes. The design determines what evidence qualifies a revised hydrological model for selection, and how historical evaluation results remain comparable. Stage 1b scientific review is required.
