# Process observations — wf3-experiment-v2

Driver-appended process-friction log (design-review-loop operating rule).
Process notes only; never design content.

- 2026-08-01 · The intake's P6 evidence row cited a local weathergenr checkout
  that turned out to be a DIFFERENT origin (Deltares-research) than the
  installed build (tanerumit); the stage-1 author caught it via the installed
  lazy-load DB. Lesson: an evidence-register row about an installed package
  must cite the installed artifact, not a sibling checkout — the register
  format could prompt for "installed vs source-tree" explicitly.
- 2026-08-01 · The stage-3 author agent, after delivering its contract
  deliverables, was resumed directly by the owner and produced an
  out-of-schema explanatory artifact (`v2-change-summary.md`) in the run dir.
  Registered in `status.md` § Auxiliary artifacts so resume reconciliation
  does not flag it. Lesson candidate for the skill: name a convention for
  owner-requested auxiliary artifacts (allowed, registered, non-normative).
- 2026-08-01 · Driver briefly marked stage 4-external-r1 `[done]` at dispatch
  time with a "pending output" note, violating write-then-mark; corrected to
  `[open]` before the round returned. The status schema's `[done]` gains
  nothing from a dispatch-time mark — keep dispatch state in the open line.
- 2026-08-01 · The first 6a spawn hit a Fable session limit mid-read.
  Classification per roles-and-recovery worked as written: resource
  exhaustion → preserve partial, surface to owner, resume in place after the
  limit cleared (owner directed continuation). Skeleton-first earned its keep
  a second time: the v4 copy was already on disk, so the failure cost zero
  content. Same-thread resume (rung 1) succeeded from transcript.
- 2026-08-01 · The three internal lens spawns and both revision spawns were
  heavy (180k–345k subagent tokens each); the panel round alone consumed
  ~600k. Worth recording for loop-proportionality tuning: this run's payload
  (a 1.9k→3k-line workflow spec) sits at the upper end of what a
  single-document loop handles comfortably.
