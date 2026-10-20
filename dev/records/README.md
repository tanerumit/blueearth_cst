# Retained development records

These files preserve evidence and historical context. Their dates, acceptance labels and implementation
claims describe the state recorded at the time; they do not establish today's requirements.
Use [the current reference](../reference/README.md) for development and compliance.

| Location | Retained material |
|---|---|
| [decisions/](decisions/index.md) | Existing design decisions, alternatives and supporting evidence |
| [milestones/](milestones/README.md) | Milestone specifications, acceptance evidence and historical lineage |
| `validation/` | Measurements, numerical comparisons and qualified acceptance evidence |
| `migrations/` | Relocation maps and source identities needed to resolve historical citations |

Current requirements extracted from old decisions live in their owning reference topics.
New proposals belong with active tasks; a current-reference update does not require a new numbered ADR,
revision log or archived copy. Retain an additional record only when evidence needs to survive.
Task reviews stay with their tasks; the retired review directory must not be recreated.

[Record lifecycle](../reference/dev-record-lifecycle.md) governs preservation and deletion.
[Sealed records](sealed-records.yml) retain their original bodies and hashes, including
historical path spellings. Use the [reference transition map](migrations/dev-reference-transition-2026-10-20.md)
to resolve paths relocated during the current/historical separation.
The [review retirement map](migrations/review-retirement-2026-10-20.md) identifies retained findings
and Git recovery paths for the former review directory.
