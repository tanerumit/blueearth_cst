# Working-folder retirement

The owner retired `dev/working/` on 2026-10-20. All three remaining files contain cited evidence;
none was disposable. They were relocated without changing their original Git contents.

Source commit: `b9aa068660e6dff2047b9aa69e251f20cb2a988a`.
This record supersedes the three holds in the
[earlier migration](legacy-development-migration-2026-10-09.md), not its preserved evidence.

## Destinations

- `dev/working/parameter-placement.md` moved to
  [R14's problem statement](../milestones/r14/parameter-placement.md).
  R14 cites its numbered proposals and inventory. Its registered seal and content hash are unchanged.
  Original blob: `45f16fd8614325ac6692936e5bd7be12b1cbfb58`.
- `dev/working/2026-08-15_wf3-scenario-generation-trace/stress-test-design-and-surface-axes.md` moved to
  [the retained scenario trace](wf3-scenario-generation-trace-2026-08-15/stress-test-design-and-surface-axes.md).
  R12 cites its owner rulings. Its companion trace and rule-reference files already live there.
  Original blob: `bbbe34b39302de064b189064a20063cd66592d4a`.
- `dev/working/complete-run-output-schema.md` moved to
  [the output-schema package](../milestones/post-r12/output-schema/complete-run-output-schema.md).
  ADR 0011 and the P1–P7 briefs cite the accepted contract. It is historical acceptance evidence;
  its stale implementation-status statements do not describe current software.
  Original blob: `14876ecc80507079aaedd7910a55faa89485be92`.

## Reading the records

Editable citations use the new locations. Byte-preserved reviews, historical logs, and source snapshots
keep their original spellings; resolve the three paths using the mapping above.
Relative links inside relocated snapshots retain their original meaning. Read them at the source commit,
or use the earlier migration's inventory for companion files moved before this retirement.
An already-missing historical target is not made recoverable by this move.

```powershell
git show b9aa068660e6dff2047b9aa69e251f20cb2a988a:dev/working/complete-run-output-schema.md
git cat-file blob <original-blob>
```

Current output placement is owned by [repository layout](../../reference/repo-layout.md#outputs);
record-preservation policy is owned by [record lifecycle](../../reference/record-lifecycle.md).
Keep this mapping while retained historical citations depend on it.
