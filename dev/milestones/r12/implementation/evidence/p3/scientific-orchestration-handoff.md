# P3 consolidated scientific and orchestration handoff

**ACCEPT — bounded P3 migration. Scientific, operational, provenance and final
software conditions are satisfied.**
Reviewer: Astra `model-validator` (`/root/model_validator_p3`), 2026-09-12.
The final `test-full` run exited 0 with 3,705 passed, 15 skipped and one expected
failure; its log and reviewed runtime inventory were independently verified.
GF15 estimator adequacy and milestone seal are explicitly outside this bounded
migration handoff and remain owner-gated.

This consolidates the accepted P1/P2 mechanisms, final successor-interface
executions, independent numerical reviews and post-execution provenance
reconciliation. The [independent consolidation record](consolidated-independent-review.json)
binds the operational reports and verifies their command/log hashes, retained
artifact bytes and source inventories. Earlier reviews' pending GF27,
operational and final-software conditions are closed by this record.

## Signed scientific stages

| Stage | Accepted evidence and conclusion |
|---|---|
| 1 — scenario collection | [Direct/runner GF9 handoff](direct-scientific-handoff.md) and [GF27 acceptance](gf27-acceptance.md): both final generated collections preserve all 14 P0 forcing members; automatic-seed capacities 21/22/100 preserve seed 568532465 and every forcing value while separating namespaces; experiment rename resolves the same exact collection |
| 2 — preparation and native responses | [GF31 acceptance](gf31-acceptance.md), [GF28 review](gf28-temporal-review.md), and direct/runner GF9 handoff: four preparation branches preserve physical values; all 14 native CSVs preserve 126 series and their 3,286 timestamps exactly against P0; source/prepared/response clocks and endpoints preserve the accepted temporal path |
| 3 — metric publication | Direct/runner GF9 handoff: all 686 old keys account for all 756 new keys; 546 Class-A and 70 Class-B values are unchanged; all 140 Class-C run values and 70 raw pooled projections reproduce independently; persisted reference and order invariance hold; all 70 return-level fits retain 18 annual blocks with unchanged operational screening |

The immutable direct and runner collection, simulation and metric-set identities
are recorded in the signed stage evidence and
[execution-evidence.json](execution-evidence.json). The retained-only gwr metric
publication independently preserves all 56 corresponding values. There are no
unexplained numerical changes, missing counterparts or duplicate joins in these
accepted comparisons. The Class-C rounding and exact catalog-selector metadata
relocations are explicitly diagnosed and recorded; no tolerance was relaxed.

## Final-interface execution review

The [checkpoint transcript](checkpoint-transcript.txt) retains decisive lines
and explicitly reports omitted verbose lines. All 19 underlying log hashes
in the execution record were independently checked. Both fresh generation runs
began without model leaves; their recorded enabling helper refuses an existing
model directory and only copies the P0 model after collection publication.

| Gate or operation | Reviewed result |
|---|---|
| Fresh direct and all-runner generation, GF29 | Each completes source preparation, actual-byte collection identity and ready publication in one invocation, 37/37 jobs; dry-runs report checkpoint-dependent unresolved targets |
| Fresh dedicated and all-runner simulation, GF30 | Each completes native responses, response-dependent metric planning and publication in one invocation, 25/25 jobs |
| Physically offline metrics-only | Three jobs publish a new gwr set while scratch model/data directories and live workflow/catalog paths are unavailable and Julia is absent from PATH; directories are restored |
| Reuse and force, both interfaces | Simulation reuse/force and metric reuse/force succeed with all retained bytes preserved |
| Selected and forbidden targets, both interfaces | Selected metric-table filename succeeds; wrong metric-set, native-output and direct plan-repair targets refuse |
| Missing/stale plans, both interfaces | Missing source plan gives the generation repair command; canonically encoded wrong source/metric plan digests give the expected named refusals; unsupported direct repair targets refuse |
| Exact collection selection, GF32, both interfaces | Routine selection chooses its exact plan with several collections retained; explicit retained metrics succeed; a different explicit collection refuses instead of switching identity |
| Output inventory | Direct 424 paths and runner 228 paths map cleanly, with zero unmapped paths; the two missing dev-tool inventory declarations found during review were corrected and their 123-test group passed |
| User-facing retained readers | Notebook reader and response-surface cells pass on final outputs; all code cells compile |

The eight operational cases contain **32 commands**. The reviewer checked every
reported command outcome and log hash, including the specific refusal diagnostic,
and rehashed all **246 unique retained files** represented across the cases.
All match their recorded pre-operation bytes. Individual cases protect 121 or
125 files. Forced/repeated metric operations can refresh timestamps on five
metric-set files; this is recorded as mtime-only change, not silently reported
as timestamp-preserving reuse. No retained byte mutation is accepted.

The first stale-plan probe used ordinary JSON serialization and therefore
exercised the serialization refusal before reaching its intended digest check.
The corrected probe changed only the intended digest while retaining canonical
serialization, reached the expected source/metric digest refusals, and restored
the original plan bytes. This was an evidence-probe correction, not a runtime or
scientific repair. These final-interface cases establish plan refusal and
selection; the earlier accepted P2 source-byte-drift mechanisms and their final
software checks remain the relevant supporting coverage for live-input drift.

## Executed and reviewed source reconciliation

The executed inventory is retained unchanged:
`b12a76551cf13b9bce3f96e5d8125954ae70dbfc88278e32f93a90f3e980be98`.
The final reviewed inventory is
`376ae0edeed8283b4cfd0cec9667ef07f97e4966e019d300af5df5b9f7d6c04b`.
[comment-provenance.json](comment-provenance.json) records the exact diff and
pre/post hashes. Only the stale explanatory comment in `scripts/run_workflows.py`
changed; the other **192 files** are byte-identical.

The reviewer independently verified all 193 current source hashes, both inventory
digests, reconstructed the pre-edit runner bytes from the recorded comment diff
and matched their executed hash, and confirmed identical parsed ASTs. The diff
contains only comment lines. This reconciliation supports retaining the completed
scientific executions without pretending the later comment bytes were executed
or rerunning numerical work for a non-executable change.

## Final software closure and excluded adequacy claim

The final `pixi run --as-is test-full` (`pytest tests/`) exited **0** on Windows:
**3,705 passed, 15 skipped, 1 xfailed, 8,845 warnings in 803.06 seconds**.
[software-validation.json](software-validation.json) records the command, exact
summary, lint/format results and log hashes. The final full-log SHA256 is
`746ecca925a2d7d90c877009e4b3874f68552c15c563a8cdba386d5fff28efe9`.
The reviewer read the final summary, independently verified all nine recorded
software-log hashes, and rechecked all 193 runtime file hashes against the
unchanged reviewed inventory. This closes the sole remaining condition of the
bounded P3 handoff.

The 15 skips comprise 12 stale-standing-fixture checks and three opt-in integration
checks. The expected failure is the known upstream HydroMT catalog round-trip
preprocessing loss, for which the existing workaround remains. The independently
reviewed final successor runs supply the separate actual execution and scientific
evidence; a skipped standing fixture is not treated as a passing test. Linux and
remote CI were not run. This review launched no tests, workflows or simulation;
it used read-only evidence and provenance checks and changed only the authorized
handoff records.

### Post-gate EOF provenance addendum

**Accepted — no executable or numerical change.** After the full suite, the
staged whitespace check identified one extra terminal blank line in
`generate_scenarios.smk`. Removing its final CRLF changes two bytes only.
[eof-provenance.json](eof-provenance.json) retains the pre/post hashes and
[commit-source-inventory.json](commit-source-inventory.json) records inventory
`7a7c6510854031a69e76ed3bf3c0a420200069d41098c3e552bf5310f0c9e1d0`.
The full-tested inventory `376ae0...` remains unchanged and remains the binding
for the full-suite result above.

The reviewer independently verified all 193 commit-inventory runtime hashes,
confirmed this is the sole difference from the full-tested inventory, and
reconstructed the exact full-tested file by appending one CRLF to the commit
bytes. Its SHA256 matches
`bf88fe7a765d30f4f0127ca8b689986b27c39f5fa1f8207e467afdf66005f279`;
the other 192 sources are byte-identical. No scientific or full-suite repetition
is warranted for this terminal blank-line removal.

The required post-edit command `pixi run --as-is pytest tests/test_cli.py`
exited **0**, with **20 passed in 38.08 seconds**.
[postgate-validation.json](postgate-validation.json) binds that result to the
commit inventory; the independently checked CLI log SHA256 is
`9bfc7f9eb178e5bc41013527e57db1f57603378a269e11fb5987a6fd13dcf937`.
Original scientific and full-suite source/log bindings are preserved explicitly.
Scoped Git attributes preserve the hashed P3 evidence and full-log bytes across
line-ending handling. The coordinator retains the final staged-whitespace and
exact-staged-byte checks before commit. This addendum changes neither the
bounded migration verdict nor the separate GF15/seal boundary below.

GF15 remains `provisional_operational`, benchmark `not assessed`. Preserved
screening and valid fits are accepted, but estimator adequacy is not. The master
brief assigns the separately owner-approved benchmark to milestone seal; the
P3 validation paragraph and ADR 0009 retain that separation. This handoff therefore
does not claim that every GF1–GF32 requirement passed, authorize an unapproved
benchmark, close milestone seal, or authorize a standing-baseline re-record.

The accepted domain is deterministic migration preservation for the seed-123
ERA5 reference and the bounded automatic-seed capacity matrix, each with two
realizations and six design points. CHIRPS preparation evidence uses ERA5 values
and synthetic elevation, and E-OBS retains its production limitation. No held-out
hydrological skill, observational accuracy or predictive uncertainty bound is
established. Parameter, structural, observational, scenario and internal-variability
uncertainties are unquantified; Class-B point estimates retain no fit interval.
