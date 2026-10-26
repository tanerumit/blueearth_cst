P2 complete for `t2610211349`. **P1’s overall direction is supported, with three major boundary issues and one
minor ownership clarification.** No unconditional blocker requires abandoning the proposal. The issues below
should be resolved or explicitly excluded from the first migration before dependent work begins.

The core recommendation—central reader journeys, canonical local detail, shared publication sources—is sound.
Exact inventory coverage does not, however, establish coverage of generated reader instructions or
compatibility consumers.

1. **Major — The scaffolded-case entry point falls outside the proposed ownership map.**

   **Location:** P1 rows 44–46 and the own-basin journey;
   [create_case.py:386](C:/Users/taner/workspace/blueearth_cst/scripts/create_case.py:386).

   **Concern:** The scaffolder explicitly removes the starter `README.md` and generates `INSTRUCTIONS.md`.
   That generated document contains running, recovery, rebuilding, indicator recalculation and output
   guidance. Consequently, shortening the inventoried starter README and adding `UG/new-case.md` will not
   update the document that scaffolded-case users actually receive. Manual copying and scaffolding are
   materially different documentation routes.

   The copied data README also uses the textual locator `blueearth_cst:config/templates/README.md`, while the
   starter mixes repository-relative links with GitHub `main` links. “Portable/published references” does not
   yet specify how a copied case finds documentation matching its toolbox version without network access.

   **Reader consequence:** Scaffolded users can retain a separate procedural account; manually copied users
   can lose their links or reach newer, incompatible instructions.

   **Confidence:** High; directly established by source inspection.

   **Smallest fix:** Add an explicit consumer disposition for generated `INSTRUCTIONS.md` without changing the
   55-source inventory. Distinguish scaffolded and manually copied cases, and specify the minimal local
   instructions plus a version-identifiable documentation locator. Because generated instructions and their
   producer are outside the present editorial targets, **cst-main must obtain a scope decision or explicitly
   defer their reconciliation**. Do not silently edit the producer.

2. **Major — Source-link compatibility needs a concrete disposition distinct from published URL
   preservation.**

   **Location:** P1 migration contract items 2–4, moved technical/scientific pages, and the source/publication
   URL choice.

   **Concern:** P1 correctly calls for checking both layouts, but it does not settle how old repository source
   paths survive. Existing excluded consumers link directly to `.qmd` files. For example, [the
   hydrological-model
   interface](C:/Users/taner/workspace/blueearth_cst/dev/reference/toolbox-hydrological-model-interface.md:19)
   links to `docs/site/toolbox-reference/retained-handoffs.qmd`; architecture and weather-generator references
   have similar dependencies.

   Moving canonical prose to `.md` and preserving `toolbox-reference/*.html` addresses will not preserve those
   source links. Generated staging copies also cannot guarantee that links work in a fresh checkout before a
   build.

   **Reader consequence:** A website migration can pass while repository readers—including maintainers
   following unchanged governing references—encounter missing files.

   **Confidence:** High.

   **Smallest fix:** Before migration, record a separate old-source-path disposition alongside each public
   URL/anchor disposition. Retaining small tracked compatibility wrappers is one option; authorizing consumer
   updates is another. The owner chooses the compatibility tradeoff. Mechanical implementation should then
   check a representative old `.qmd` link in an unbuilt checkout as well as its rendered route. The P3 pilot
   should exercise this boundary, not only inclusion of a previously unpublished local README.

3. **Major, conditional blocker — The offline assessment promise remains unclear at the transition from
   indicator tables to response surfaces.**

   **Location:** P1 technical-manual “Response-surface coordinates” section, notebook policy, PDF composition
   and interpretation journey.

   **Concern:** P1 already identifies the unresolved axis authority; I confirm that this is a boundary issue
   rather than merely an incidental wording correction. The [axis module
   header](C:/Users/taner/workspace/blueearth_cst/blueearth_cst/shared/surface_axes.py:4) explicitly delegates
   the definition to HM-7, whereas [current
   HM-7](C:/Users/taner/workspace/blueearth_cst/dev/reference/toolbox-hydrological-model-interface.md:91)
   describes retained indicator publication, not axis derivation.

   Meanwhile, the detailed teaching route is assigned to a notebook whose interface repair is deferred and
   which is excluded from automatic publication. Including all five indicator-set READMEs does not fill this
   gap.

   **Reader consequence:** An offline reader may understand an indicator value and its joins but still lack a
   supported route to construct and interpret the response surface that connects those values to an
   assessment. Conversely, repairing the axis contract could unexpectedly expand this documentation task into
   excluded contract ownership.

   **Confidence:** High about the missing authority; medium about whether it blocks the intended first
   publication, because that publication’s endpoint remains an owner choice.

   **Smallest fix:** State the promised endpoint explicitly. If the first manual promises table-level
   interpretation and selection/extension only, defer surface construction visibly and consistently. If it
   promises a complete response-surface walkthrough, assign a narrow authority reconciliation and an offline
   worked route before publishing that promise. **This blocks the broader promise, not unrelated documentation
   migration.** No algorithm change is implied.

4. **Minor — Set-specific workflow preparation needs an explicit exception to the science/interface split.**

   **Location:** P1 rows 25 and 34; `indicator-requests.md` outline; [crop-water
   README](C:/Users/taner/workspace/blueearth_cst/blueearth_cst/indicators/sets/crop_water/README.md).

   **Concern:** The local crop-water source contains much more than formulas and interpretation:
   baseline-Qcrit request syntax, WF1 artifact prerequisites, dry-run behavior, preparation timing, provenance
   fields and compatibility rules. These overlap the proposed central request and WF4 chapters. Calling local
   sources the owners of “set-specific conventions” leaves room for P4 writers to split this tightly connected
   account across several pages or reproduce it centrally.

   **Reader consequence:** A user diagnosing a refused threshold request could need to traverse the user
   guide, request reference, WF4 page and set appendix to recover one complete explanation.

   **Confidence:** High about the overlap; medium about future fragmentation.

   **Smallest fix:** Explicitly assign the complete set-specific preparation contract to one source—retaining
   its current local home is sufficient—and make central chapters own only generic request mechanics and a
   task-level entry link. This is editorial clarification within the proposed boundaries, not a new
   user-facing design decision.

The three journeys otherwise withstand the structural challenge:

- **First example:** The prerequisite-qualified rapid example is an honest entry route. Preserve external-data
  requirements, limited runtime claims, completion evidence and one concrete interpretation. A bundled dataset
  or new model execution is unnecessary.
- **Own basin:** Central procedure plus a local replacement checklist is appropriate, subject to finding 1.
  WF0 selection and independent WF1/WF3 prerequisites are preserved.
- **Indicator interpretation/extension:** Local set authority and inclusion in the offline manual are strong
  choices. Preserve the plain-Python extension route, independent checking and distinction between
  unavailable, undefined and failed calculations. Finding 3 bounds the further surface-analysis promise.

I found no evidence that the four collection roles themselves are excessive fragmentation. The risk lies in
splitting a single task’s essential detail, particularly threshold preparation. Brief prerequisite and
scientific-limit reminders are useful repetition. Notebook interface drift, old paths, setup pins and other
incidental P1 accuracy questions remain deferred unless they affect a specifically promised journey.

**Evidence and execution record**

- Read the full frozen map, execution plan, scoped inventory and landscape assessment from **current main**,
  commit `58efe411119af402195727ea0ad3d7b6f92c438d`. Primary-input SHA256 matched the supplied value before
  and after review.
- Performed targeted source walkthroughs of quick start, starter/data instructions, generated case
  instructions, indicator module/crop-water/flood guidance, staging configuration and source-link consumers.
  Accepted the coordinator’s inventory-coverage check; did not repeat an exhaustive accuracy audit.
- Applied the full canonical `critical-thinker.md` manually under **degraded generic runtime**. Model/effort:
  **GPT-6-Astra medium, UI verified by owner**; backend settings were not independently observable.
- Fully loaded skills: `design-exploration`, `scientific-software-documentation`, and `testing-policy`. For
  scientific documentation, checked `_external` precedence and loaded all four triggered references: README
  authoring, site lifecycle, task guides/troubleshooting, and documentation review/accessibility. No
  scientific evidence appraisal triggered `claim-evaluation`; no decision-log or conditional testing reference
  was required. No applicable skill-body or triggered-reference read remains incomplete; truncated map output
  was recovered through bounded reads.
- No edits, Git mutations, STATUS writes, delegation, builds, runs or permission changes. Session-2 remained
  clean and detached. Read-only conduct was observed under current permissions; enforced read-only isolation
  is **not** claimed.
- No rendered/PDF, offline usability, executable-example or empirical validation claims.
- **Start:** 2026-10-26 13:26:04 UTC. **End of checks:** 2026-10-26 13:28:40 UTC. Tokens/cost: **unknown**.

Returned for editorial reconciliation and coordinator retention. No P3, migration or publication work started.
