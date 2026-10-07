- 2026-10-07 stage 0: gate materialization found a stale "pre-change" artifact (rapid tree older than the
  lane's own fixes). The checklist asks whether a snapshot exists, not whether it is current relative to HEAD;
  worth a "dated after the last change to the producing code" check.
- 2026-10-07 stage 6: the round-2 trigger check only names "blocking mechanism change" and "rejected
  blocking/major". A scoped pass that re-raises an accepted major (resolution faulted) is not named; I treated it
  as firing round 2. Worth stating in findings-and-closure § Round 2.
