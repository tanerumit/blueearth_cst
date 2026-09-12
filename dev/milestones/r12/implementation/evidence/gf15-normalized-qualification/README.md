# GF15 normalized candidate qualification

Owner-approved B-only qualification of the original retained IID GEV matrix.
The numerical candidate is imported unchanged from the committed
`../gf15-candidates/compare-candidates.py`. Production is unchanged.

From the repository root in the pinned Pixi environment:

```powershell
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15-normalized-qualification/qualify-normalized.py prepare --output <new-output-directory>
pixi run --as-is python dev/milestones/r12/implementation/evidence/gf15-normalized-qualification/qualify-normalized.py run --output <new-output-directory>
```

The first command freezes source, input and protocol hashes and executes only
analytical and toy controls. The second executes all 240 fixed chunks using four
worker processes. Repeating `run` reuses only completed chunks with matching
hash receipts and the same frozen binding. An unreceipted final chunk is refused
for inspection. Redirect execution to a log; do not pipe away diagnostic output.

`results/protocol.json` describes the fixed matrix and denominator rules;
`criteria.json` preserves the original criteria. `fits-*.jsonl.gz` retain every
raw fit, optimizer result, normalization constant and scalar quantile, including
refused outcomes. Final simplices and checked evaluation counts are retained;
full per-evaluation objective histories are not retained for this full matrix.
`paired-translations.jsonl.gz` separates numerical pass/failure, changed
acceptance, and both-refused pairs without numerical proof.

The matrix summaries condition accuracy on accepted fits while keeping all
1,000 attempts in each acceptance-rate denominator. Relative errors at ratio zero remain
undefined; ratio 0.05 remains diagnostic. The approved tolerances are unchanged.
The 186 previous B cases are embedded in this full matrix and checked for exact
replay, without additional fitting. The coordinator's separate independent
review recomputes the retained arithmetic and decisions without importing the
candidate or qualification runner.

Read `scientific-handoff.md` for the final scientific verdict when execution and
independent review are complete. A successful harness run does not itself imply
that the candidate passes qualification.
