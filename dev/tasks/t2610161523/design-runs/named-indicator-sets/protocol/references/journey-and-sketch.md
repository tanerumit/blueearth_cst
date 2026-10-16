# Journey and sketch handoff

Preserve the ordinary user journey and actor/artifact boundaries from the request
or prior `design-exploration` in `intake.md`: who transforms what, where, user choices,
tool checks, and useful results. Include the chosen approach, rejected
alternatives with reasons, unresolved assumptions, next decision, and the
current sketch link where used. Write a complete description for readers
unable to render HTML; do not reopen settled choices merely to fill a template.

The author carries the journey and proposed layout into `design-v1.md`, making
initial independent review self-contained. At G1, lead with the user's outcome
and ordinary end-to-end journey, then the smallest useful change, selected and
rejected alternatives, consequential tradeoffs, complexity, migration, and
unresolved choices that could change the approach. Present the problem,
constraints, criteria, and domain findings with those decisions. Put file
names and trees behind the decision they illuminate, and reuse settled intent.
Record in the existing gate record which sketch was shown: repository revision
and path, or digest plus a recoverable copy. Keep those bytes available while
the working sketch evolves; apply the host's existing retention rules.

## Gate 1 structural decisions

`design-document` owns the change inventory and layout content contract in its
Gate 1 decision review section. Apply it to the candidate where those changes
affect the design; this loop owns when the owner reviews and approves it.
Reuse the candidate's inventory and tree in the G1 presentation rather than
maintaining a second checklist or document. A proposed tree does not prove that
its files exist or outputs were generated.

Record the reviewed candidate identity, owner's decision, and unresolved choices
in the existing G1 record. Record a separate path and revision or digest only for
a separately presented artifact. Keep the inventory and layout aligned with the
candidate through G2; material scope or ownership changes follow the G1 return rule.

Internal lenses receive intake's written journey and actor/artifact boundary
alongside their existing stage-2 inputs. Within each lens's remit, test whether
every new stage or artifact serves a confirmed need and whether a simpler
ownership boundary meets the same outcome. Flag divergence from the recorded
outcome as a framing issue, citing the mismatch and consequence. Reviewers
cannot silently replace approved choices; a material change follows the
existing G1 return rule. Visual agreement supplements technical review.

