# Decision-history transition — 2026-10-20

The owner authorized renaming `dev/records/decisions/` to `dev/records/decision-history/` and triaging
its contents. Current policy lives in [dev-record-lifecycle.md](../../reference/dev-record-lifecycle.md).
The [history index](../decision-history/index.md) maps each retained decision to its current topic owner.

## Dispositions

- ADRs 0001–0011 and 0022 keep their filenames under `decision-history/`. Historical bodies and
  section identifiers remain available because code, tests and records cite their rationale or
  measurements. Their banners now explicitly exclude current operational authority.
  ADR 0002 is superseded lineage; 0011's pending status is historical; 0022 does not certify adoption.
- `task-lanes.md` keeps its filename, condensed to the rationale and bounded historical measurements.
  Retired allocator commands, fixture-copy recipes and worktree execution prohibitions remain in Git.
- `0001-restore-wflow-constant-parameters/baseline_diffs.md`, `equivalence-gate-log.md`,
  `config_baseline.yml` and `config_restored.yml` moved unchanged to
  `dev/records/validation/wflow-constant-restoration/`. They describe the original comparison inputs,
  semantic equivalence checks and basin-specific aggregate sensitivity, not calibration or a new gate.
- That sidecar's `review-record.md` was retired. The accepted rationale and measured results survive;
  detailed review rounds and finding dispositions remain recoverable from the source pin.
- `0003-one-shared-region-artifact/probe_split_cost.py` was retired. Its measured outcomes and
  small-basin limitations remain in ADR 0003; the obsolete one-off harness is recoverable from Git.
- `experiment-numbering-2026-10-10/implementation-evidence.md` and `original-context.json` moved to
  `dev/records/validation/experiment-numbering-2026-10-10/`. The JSON remains unchanged.
  The redundant `original-context.zip` byte archive is recoverable from Git, including its original
  Windows and Git variants. Its SHA256 is
  `1663e9da4416e88d2178237cd7e3d59b3bbdc6ecf698739678242fb59ffb41d6`.
- `index.md` was rewritten as history-to-current navigation; the empty `.gitkeep` was removed.

Live guidance already covered most accepted decisions. The current spatial reference now clarifies
per-parent partition ceilings and spatial seam/catalog ownership. The architecture reference clarifies
source archives versus scientific identity and archive lifetime, shared elevation ownership, and the
conditional managed-root protocol. These are descriptions verified against existing sources, not
implementation of the entire old design.

## Recovery and unchanged citations

Original tracked paths are recoverable at `5fa77b34` under `dev/records/decisions/`.
For older citations beginning `dev/decisions/`, first apply the same relative suffix to this pinned tree.
The directory rename alone preserves ADR numbers, headings and section references.

```powershell
git ls-tree -r --name-only 5fa77b34 -- dev/records/decisions
git show 5fa77b34:dev/records/decisions/0001-restore-wflow-constant-parameters/review-record.md
```

To recover the original binary ZIP without shell text conversion, create a Git archive and unpack it:

```powershell
git archive --format=zip --output=decision-context-recovery.zip 5fa77b34 dev/records/decisions/experiment-numbering-2026-10-10/original-context.zip
```

The recovery archive contains the original ZIP at its historical relative path.
The retained JSON lists member identities and original task-tree objects independently of this ZIP.
Existing scratch/output paths in evidence are not made recoverable or recertified by this migration.

The ADR 0010 path in `UnitInterpretation.evidence` is serialized catalog provenance. Its historical
string is deliberately unchanged to avoid changing runtime metadata for a documentation move.
Its current rules are in `toolbox-forcing-units.md`. Immutable source inventories, retained history
and shared task/ledger citations also retain original spellings and resolve through this map.
No shared board edits, task closure, workflow execution, landing or push are part of this transition.
