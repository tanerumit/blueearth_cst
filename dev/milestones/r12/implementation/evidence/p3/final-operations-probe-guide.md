# GF30/GF32 final-interface follow-up

`probe-final-operations.py` passed all eight final-interface cases (32 real
commands); see [execution evidence](execution-evidence.json) and the eight
`operations-*.json` records. It invokes real commands.
The coordinator must release the repository Snakemake lock and selected scratch
project before **each** invocation. Run sequentially; never overlap with GF27,
fresh simulation, or physical offline metrics preparation. GF15 is excluded.

## Preconditions and exact inputs

1. Complete fresh direct and all-workflow-runner GF30 executions and preserve their
   invocation transcripts. Those prove absent responses → metric publication in
   one invocation; this follow-up cannot reconstruct that evidence afterward.
2. Complete the coordinator's physical offline metrics-only check. Its additional
   retained metric set must exist before the preservation inventory is captured.
3. Complete GF27 generation before `selection`, so several **ready** collections
   exist in the direct project. Supply their exact recorded manifest paths.
4. Supply the exact original project config, scenario `plan.json`, metric
   `plan.json`, selected `collection.json`, and final source inventory. Obtain
   these from run provenance, not a `latest` glob. The probe cross-checks their
   simulation, collection/revision and metric-set identities and verifies every
   source-inventory file against current bytes before executing a command.

The direct config is
`.tmp/scratchpad/2026-09-11_0010/p3-final-direct/project_config_p3.yml`.
Use the independently recorded runner config/artifact paths for the runner root.
Both projects and each new `--work` directory must resolve below repository
`.tmp/`; the script refuses production roots and reused evidence directories.

## Sequential invocation

Inside the established Pixi environment, set these variables to the exact paths
from the chosen run. `$metricPlan` selects an already published full metric set;
the probe inventories **all** existing metric sets, including the offline set.

```powershell
$probe = 'dev/milestones/r12/implementation/evidence/p3/probe-final-operations.py'
$sourceInventory = 'dev/milestones/r12/implementation/evidence/p3/final-source-inventory.json'
# Set $projectConfig, $scenarioPlan, $metricPlan, $manifest,
# $otherManifest, and $newWork to exact recorded absolute paths.
python $probe --config $projectConfig --scenario-plan $scenarioPlan --metric-plan $metricPlan --manifest $manifest --source-inventory $sourceInventory --interface dedicated --case reuse --work $newWork
```

Run each case once on `dedicated`, then once on `all`, using a fresh work path
each time. Use the appropriate independent root's inputs. Cases are:

| Case | Final-interface evidence |
|---|---|
| `reuse` | Unchanged simulation reuse and `--forceall`; retained-only metrics reuse and forced reuse. All retained bytes/paths must survive; mtime-only changes are listed. |
| `targets` | An exact selected metric-table filename succeeds; native-response filename, different metric-set filename and metric-plan filename refuse before execution. |
| `stale` | Missing/stale source plan refuses without fallback; stale metric plan refuses; attempts to repair either by a forbidden simulation filename target refuse. Each modified scheduling leaf is restored in `finally`, including original times for corrupted plans. |
| `selection` | Exact routine request-plan selection among several typed-validated ready manifests; explicit retained metric-table selection with a deliberately absent generation config; mismatched explicit collection refuses. Add `--other-manifest $otherManifest` (repeat for more explicitly selected manifests). |

For `selection`, reuse the direct multi-collection project with both interfaces
unless the runner project independently contains multiple ready collections.
The `all` interface uses the real `scripts/run_workflows.py` with five stanzas
and only simulation enabled. The original orchestration config is copied and
never edited; fresh whole-pipeline orchestration remains the coordinator's GF30
evidence. All config variants and full command logs stay in `--work`.

This probe does **not** move model/data directories, hide Julia, repair plans by
running generation, or regenerate scientific outputs intentionally. Physical
offline isolation is the coordinator's separate check. Stale plans are refused
and restored, not silently repaired. A preserved `.gf32-backup` after a hard
process kill identifies the exact withheld source plan requiring restoration.

## Evidence and acceptance

Each work directory contains `result.json`, exact argv/log digests, original and
variant config digests, simulation/collection/metric identity provenance, full
retained-artifact hashes, and per-command mtime changes. A failed command retains
its report/log. No test or scientific acceptance is inferred from compilation.
Review the report and full logs, then retain the necessary reports in this evidence
directory with the coordinator's stage acceptance. Do not claim physical offline
isolation or fresh checkpoint publication from these reuse cases.

The first dedicated stale-plan probe wrote ordinary JSON and therefore reached
the canonical-serialization refusal before the intended digest refusal. The
corrected probe changes only `plan_sha256` using canonical bytes. That case and
all subsequent cases passed in new `*-final` scratch directories. The original
failed report is preserved, and the plan was restored before the repeat.

The final full suite already covers logical target matrices, collection/metric
typed readers, missing/stale plan behavior, retention invariants, seed projections,
configuration migration and runner sequencing. Its eight failures were repaired
by the bounded 37-test follow-up (including the real retained-only dry-run).
Do not repeat that suite for these operational probes: these runs supply the
remaining real-artifact/final-interface evidence, not another unit-test gate.
