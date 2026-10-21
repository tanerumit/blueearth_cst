# Named indicator sets — completion and evidence

Task `t2610161523` completed; implementation landed on 2026-10-19 at `584c0704`.
This is historical acceptance evidence, not current configuration guidance. Current behavior belongs
to the [WF4 reference](../../../docs/site/toolbox-reference/workflow-simulate-system.qmd) and the shipped metrics
package. Navigation entry: [the migration record](../milestones/post-r12/migration_named-indicator-sets.md).

## Design principles

Named indicator sets share immutable retained simulation responses. Set selection changes analysis
intent without changing simulation identity. Definitions are declarative; executable methods belong
to trusted installed registries. Each named publication captures its definitions, calculation identity,
units, coverage and diagnostics. Publication and reuse validate their dependencies and preserve legacy
artifacts. Explicit coverage distinguishes missing data and incomplete water-year blocks.

The structured registry separates neutral metric inputs and contracts from each set's calculations and
independent checks. Hash consistency establishes identity, not authenticity or scientific qualification.
The existing GEV qualification gate remains unchanged: only the qualified probabilities may publish.

## Historical design and review recovery

Original reports, candidates, ledger, acceptance status and the consumed review protocol remain unchanged
in reachable Git history. Recover the entire task tree to preserve relative citation context.

| Identity component | Value |
|---|---|
| Repository | `blueearth_cst` |
| Commit | `25f6f41c85eccc00c9635be332a66b184004ff94` |
| Original parent | `dev/tasks` |
| Task identifier | `t2610161523` |
| Task-tree Git object | `597a6fe8c9941b42013023cb6772560d37fd5878` |
| Accepted design relative to tree | `design-runs/named-indicator-sets/design-v3.md` |
| Acceptance authority relative to tree | `design-runs/named-indicator-sets/status.md`, final seal |
| Review and dispositions relative to tree | `design-runs/named-indicator-sets/` |
| Implementation evidence relative to tree | `structured-registry-implementation.md` |

Retrieve a report with `git show 597a6fe8c9941b42013023cb6772560d37fd5878:<relative-path>`.
The accepted v3 SHA256 is
`ad4cfed1b9d47c07897bf4b10d2ad259aa89603e19aa4980f31d3f09fc0f63d5`.
The owner authorized application and sealing of the review resolutions. The separate general risk
review did not run; the external reports did not review v3 bytes. The pinned status records these
limitations and the coordinator's final verification. No new acceptance or retrospective review is claimed.

## Implementation acceptance

The final candidate was `269b20d482994daa09253caafa29848af22905da`; landing recorded tree equality
and ancestry. Software coverage: 4,745 passed, 30 expected skips and one expected upstream failure;
lint and formatting passed. A fresh local all-five execution passed with 10 scenario simulations,
with documented evidence reuse across the final test-only inventory correction.

The pre-change oracle covered January and October water years. All six default tables were
byte-identical; 64 legacy branches had no differences. Named/flat export preservation, independent
set reuse and publication recovery were checked. The water-year end anchor preserved numerical values.

The structured-registry follow-up matched all 128 pre/post metric/location values exactly.
Of prototype values, 76 qualified available values met `rtol=1e-10, atol=1e-12`, with maximum absolute
difference `7.105427357601002e-15`. Twelve unsupported-probability requests were refused and eight
recharge entries were unavailable for the discharge-only input. The retained-response execution
published 700 default and 40 qualified flood estimates. These results do not qualify other return
probabilities or independently validate the shared fitting library.

The [Gabon–Ntoum walkthrough](named-indicator-sets-walkthrough.md) preserves the worked historical
example. It predates the structured registry and is not a current tutorial.

At closure on 2026-10-21 the owner requested deletion of the approximately 2 GB of local scratch.
Raw local receipts, probes, oracle outputs and staged execution products are therefore not retained;
the measurements above and original tracked implementation account preserve their reported findings.
No new execution or numerical verification is claimed by this documentation migration.
