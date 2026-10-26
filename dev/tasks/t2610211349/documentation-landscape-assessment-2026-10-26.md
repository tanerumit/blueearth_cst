# Documentation landscape assessment

Date: 2026-10-26. Task: t2610211349.
Status: high-level assessment and recommendations; not an approved implementation specification.

## Scope and conclusion

This assessment uses the [scoped inventory](documentation-inventory-2026-10-26.md): 55 files across five
audience groups. Its exclusions remain binding. Representative documentation and publishing code were
inspected; individual claims and every apparent overlap have not been audited for accuracy or redundancy.

The recommended direction is to centralize reader journeys, retain local instructions where useful,
and publish multiple formats from shared Markdown sources. The main need is clearer content ownership,
not simply fewer files. Much of the proposed structure already exists and can be refined incrementally.

## Findings

1. **Source ownership is inconsistent.** User guides live in `docs/guide/` and are staged into the site.
   Scientific explanations, workflow references and installation guidance are authored inside `docs/site/`.
   Extend the separation between source and presentation to all central documentation.
   [Current arrangement](../../../docs/README.md).
2. **Procedures and reference material overlap.** Configuration, running and outputs guides contain both
   practical instructions and detailed contracts. Workflow-reference pages also describe configuration and
   outputs. Define their responsibilities before deciding what to consolidate.
3. **The technical manual has a foundation.** The existing toolbox reference covers workflows, inputs,
   outputs and components; its overview identifies architecture documentation as planned. Build on that
   collection rather than introducing a parallel manual.
4. **Some content assumes HTML.** The quick start embeds an interactive HTML diagram; some scientific
   pages specify HTML formatting. PDF and plain-Markdown reading need deliberate alternatives.
5. **Notebooks and report templates need separate decisions.** They are executable or interactive artifacts,
   not ordinary prose pages. Their relationship to the core documentation should be explicit.

## Recommended central documents

Use coherent collections of short Markdown chapters with clear entry points, rather than large single files.

| Collection | Reader question | Owns |
|---|---|---|
| Quick start | How do I get my first result? | One example, prerequisites, execution and success checks |
| User guide | How do I run my assessment? | Setup, case choices, execution, recovery and outputs |
| Technical manual | What does the toolbox implement? | Architecture, contracts, interfaces and extensions |
| Scientific approach | Why these methods and conclusions? | Methods, assumptions, uncertainty and evidence |
| Repository README | What is this; where do I start? | Brief orientation and links to the four collections |

The quick start should remain a prominent entry within the user guide, with its own direct link.
A separate source copy would introduce drift.

The scientific approach owns methodological explanations. The technical manual describes how the toolbox
implements them, including configuration semantics, data interfaces and output definitions. For example:

- Scientific approach: why weather variability is sampled independently of the climate-change grid.
- Technical manual: how realizations, perturbations and retained collections are represented.
- User guide: how to choose settings and inspect the resulting collection.
- Quick start: the fixed settings used in the example.

Short contextual summaries can appear in several places. Detailed explanations and contractual statements
should have one authoritative home.

## Local documentation boundaries

Keep a local README beside its subject when readers working in that directory need it.

| Local document | Appropriate responsibility |
|---|---|
| `scripts/README.md` | Discover entry points and link to procedures |
| `config/…/README.md` | Explain nearby files, their scope and how to edit them |
| Example-basin README | Explain how to use that starter |
| Indicator-set README | Define that set's interpretation, assumptions and limitations |
| `dev/templates/` guidance | Explain how to populate and use nearby templates |

The [indicator-module README](../../../blueearth_cst/indicators/README.md) already distinguishes ownership
of contracts, calculations and set-specific interpretation.

When local content belongs in a published manual, include it during the build or link to it rather than
maintaining another prose copy. Inclusion is preferable when an offline PDF must contain the detail.

## Canonical Markdown and derived publications

A suitable target structure is:

```text
docs/
  README.md
  guide/                   # Includes quick start and installation
  technical-manual/
  scientific-approach/
  assets/
  site/                    # Publishing configuration and presentation assets

<component>/README.md      # Canonical local instructions
```

Assemble selected Markdown sources, including relevant local READMEs, into HTML and PDF. Navigation,
chapter order, styling and format-specific handling belong to the publishing configuration.

Retain the existing publishing toolchain initially. The
[guide-staging script](../../../dev/scripts/stage_site_guides.py) demonstrates the pattern, although its
fixed page list and simple link rewriting need revisiting for a broader collection.

Two qualifications matter:

1. A shared source prevents format copies from drifting; it does not prevent overlapping source pages or
   code–documentation drift. Content ownership and checks remain necessary.
2. Markdown should own prose, not every asset. Diagram source, plotting code, bibliography data, templates
   and styles remain legitimate sources. Generated HTML/PDF should not acquire independent explanations.

Provide a static equivalent of the interactive workflow diagram, generated from the same underlying
description. For notebooks, choose one editable source per tutorial; avoid maintaining identical teaching
prose in Markdown and notebooks. Trial the conversion approach before migrating all three notebooks.

## Recommended next steps

1. **Assign each of the 55 files a purpose and owner.** Record its reader question, proposed collection,
   local-versus-central role and overlapping topics. Classify it as retain, shorten, split, incorporate or
   retire, with reasons.
2. **Agree chapter outlines for the four central collections.** Define what each owns and what it links
   elsewhere before moving files.
3. **Pilot one topic across formats.** Indicator selection is a useful candidate: user procedure, technical
   contract, scientific limitations and a local set README. Produce HTML and PDF from the same sources and
   check plain-Markdown readability.
4. **Migrate incrementally.** Move scientific and technical prose out of the site tree, update links and
   preserve published URLs where practical. Consolidate content after its ownership is settled.
5. **Verify reader journeys and publishing boundaries.** Check links, equations, citations, figures and
   offline completeness. Confirm publishing does not execute expensive workflows and generated copies
   are not edited independently.

The next useful deliverable is a purpose-and-boundary matrix for the 55 files, accompanied by proposed
chapter outlines. That would turn this direction into concrete decisions without prematurely reorganizing
the repository.

## Evidence and limitations

The assessment inspected the inventory, documentation index, representative guides and workflow/scientific
pages, indicator and configuration READMEs, notebook instructions, template guidance, site configuration
and guide-staging code. Publishing implementation was consulted as evidence, not added to the review scope.

This is a structural assessment. It does not establish that individual claims are accurate or that every
overlap is redundant. No site build, PDF render, notebook execution or scientific validation was performed.
No documentation restructuring has been implemented; this file retains the assessment given in conversation.
