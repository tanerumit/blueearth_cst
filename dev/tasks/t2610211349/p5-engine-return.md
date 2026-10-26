# P5 engineering return

Task t2610211349; session-2; `feat/t2610211349-publication-engine`.
Base `31aaafab99920ea7d9b75b2cd43e5f00f0b72633`. Stable uncommitted delivery; source writes stopped.
Coordinator owns review, commit and transfer. No commit, landing, push, cross-lane/shared-record write,
nested agent, dependency change, installation, model/notebook execution or scientific rewrite occurred.

## Exact delivery paths

```text
dev/scripts/build_publications.py
dev/scripts/publication_links.lua
dev/scripts/stage_site_guides.py
tests/test_publications.py
tests/test_site_guides.py
```

Builder, Lua helper and publication tests are new. Pilot helpers are unchanged; pilot tests still pass.
Ignored STATUS/evidence are excluded from delivery. Writer owns all docs, manifests, navigation and styles.

## Schema, API and integration

Coordinated directly with existing s1 `technical-writer-p1` via Herdr. Frozen schema-version-1 manifest:
`repository_url`, optional `source_revision`, `format`, `asset`, `appendix_manifest`, and ordered
`publications[{id,title,chapters,include_appendices}]`. Source revision describes a local candidate,
not online availability. Six-source appendix declaration and format file remain writer-owned.

- `prepare_publications(source_root) -> (dict[str, bytes], dict[str, str])`: preflight required inputs/links,
  prepare relative generated files and consumed-input SHA-256 hashes before writes.
- `stage_publications(source_root, output) -> dict[str, str]`: refresh beneath executing checkout's `.tmp`;
  explicit source root may be a different read-only lane. Refuse output outside the boundary.
- `render_publications(output)`: render both volume QMDs to HTML/Typst PDF with `--no-execute`, Markdown
  engine and `execute.enabled: false`. No installation or scientific execution path.
- `check_stale_outputs(output, generated)`: refuse undeclared QMD/HTML/PDF files in generated guide,
  technical-manual and manuals trees. Deletes nothing; error names file for deliberate cleanup.
- `stage_guides(docs_dir)`: manifest mode stages all declared chapters, complete appendices, assets/maps;
  preserves authored wrappers. Without the new manifest, retain Markdown API, expanded from five to ten guides.

```powershell
python dev/scripts/build_publications.py --source-root <checkout> --output .tmp/tasks/t2610211349/p5/build
# Add --stage-only to prepare without rendering.
```

Routes: `guide/*.qmd`, `technical-manual/*.qmd`, `technical-manual/appendices/<anchor>.qmd`.
Volumes: `manuals/user-guide.html|pdf` and `manuals/technical-manual.html|pdf`.
Source-relative links rebase to chapter routes or namespaced volume headings. All six appendix bodies
are included completely. Inline/fenced examples remain code; source front matter cannot override formats.

Writer already added the required website filter:

```yaml
filters:
  - ../../dev/scripts/publication_links.lua
```

Pre-render stages `technical-manual/publication-links.json` and `technical-manual/source-hashes.json`.
Lua uses current input path and preflighted map to rebase authored wrappers at render time, retaining
source bytes and old heading IDs. The builder copies this helper into isolated output for volume rendering.
Copy **only `manuals/*.html` and `manuals/*.pdf`** to `docs/site/manuals` before website rendering.
HTML embeds resources and iframe as data URIs; PDF embeds SVG. No adjacent final volume assets required.
`manuals/assets/shape-of-a-run.svg` is a build-only Typst input within its permitted compiler root.
Website chapters continue to use staged `guide/assets`. Do not copy QMD/Typst intermediates or caches.

## Checks and retained evidence

Evidence root: `.tmp/tasks/t2610211349/p5-engine/` in this lane.
Main runtime borrowed through `session_runtime.py`, with compatible-contract, session-2 cwd/import and
main interpreter verification. Fitz used writer-supplied existing infrastructure runtime, recorded in
`artifact-proof.json`; it is a validation tool, not a publisher dependency. No install/update occurred.

Final `tests-final.log` and `checks-final.json`:

```text
python -m pytest tests/test_publications.py tests/test_site_guides.py tests/test_docs_pilot.py -q --tb=short
26 passed in 1.69s
ruff check dev/scripts/build_publications.py dev/scripts/stage_site_guides.py tests/test_publications.py tests/test_site_guides.py
ruff format --check <same four Python files>
python -m py_compile <same four Python files>
git -c core.safecrlf=false diff --check
```

All exit 0. Tests cover complete sources beyond pilot boundaries, deterministic refresh/source preservation,
missing inputs/anchors, same/cross-volume links, code-labelled and wrapped-label Markdown links, reference
links, inline/fenced examples, wrapper map, stale products refused without deletion, no-execute arguments,
and all-ten canonical guide inventory. Live code-labelled link found in TM environment chapter; rebased.

Full build: `run-build.ps1` calls s2 builder against read-only frozen s1 source, writing local `build/`.
It ran in s2's visible Herdr watch tab, preserving focus. Final `build.log` / `build-result.json`: exit 0,
**16.86 s**, completed **2026-10-26 21:53:03 UTC**. This is build wall time, not whole-task active compute.

`check-publications.py` / `artifact-proof.json`:

| Claim | Observed result |
|---|---|
| Source integrity | All 63 consumed input byte hashes unchanged after builds |
| Completeness | Ten guide chapters, 16 manual chapters, six complete appendix pages |
| HTML links | 280 TM and 237 UG links resolve, including local fragments |
| HTML resources | Source resources are data URIs; UG includes embedded iframe and SVG |
| TM PDF | 42 pages, 102 named destinations, 174 native named links, five sibling PDF URIs |
| UG PDF | 21 pages, 81 named destinations, 127 native named links, 24 sibling PDF URIs |
| Sibling PDF targets | All 29 URIs name an existing destination in the other PDF |
| Appendix roots | All six exist in TM HTML and PDF |

`check-filter.py`, `filter.log`, `filter-proof.json`: actual Lua rendering of a verbatim compatibility
wrapper snapshot proves current route/rules-anchor rebasing and unchanged source-lane wrapper bytes.
This evidence remains applicable after later changes confined to wrapped-link matching and stale-file
refusal; Lua did not change afterward. No full website build or browser/interactive review claimed.

Representative raster spot checks only: UG pages 1/4/6; TM pages 40/42. Static SVG, commands, appendix table
and prose readable; no engine defect found. Writer retains complete HTML/PDF visual and website acceptance.
No external-link availability check, broad scientific suite or P6 acceptance claimed.

## PDF navigation limitation

Coordinator accepted sibling `.pdf#nameddest=<namespace>` URIs; HTML uses sibling `.html#<namespace>`.
Same-volume PDF links remain native named destinations. Fitz checks target names and emitted `/S /URI`:
**not native remote `/GoToR`**. Cross-reader section jumping is unproven and reader dependent. Two PDFs
suffice for reading; use the target contents if its reader ignores a fragment. No postprocessing workaround
or dependency added. Probe retained in `link-probe.qmd|pdf` and `probe-pdf.py`; decision retained here.

## Roles, skills, timing and rework

Full canonical Python-engineer role manually applied in implement mode; no native persona activation claimed.
Requested and launch/UI-reported model/effort: **GPT-6.1-Sol / medium**. Effective backend model/effort,
tokens, cached usage, cost and billing remain independently unobservable/unknown. No model escalation.

Full applicable skill bodies read: python-discipline, testing-policy, project-system, scientific-workflows,
Quarto, PDF, Herdr and bug-diagnosis. Console-formatting read for routing; retained argparse/Quarto forwarding,
so no styled terminal surface was designed. Completed triggered references: Python style/hazards/validation;
testing configuration/execution-checks; project workflow/phased-execution/placement; scientific workflow-contract;
Quarto reference map; bug-diagnosis error-patterns. Governing repo docs/validation/lane-status/scratch guidance,
full continuation/P5 packet and P4 returns read. Aggregate truncations completed with bounded continuation.
No governing body or triggered reference known incomplete. PDF operation marker succeeded once before creation.
Official Quarto Lua API and Typst link reference consulted for exact runtime behavior.

Observed first explicit checkpoint **21:35:26 UTC**; final checks **21:54:54 UTC**, **19m 28s** between them.
True start preceded that checkpoint; total duration and active compute unknown. No user-decision sleep.
Rework: omitted fixture evidence input; over-specific link assertion; heading whitespace consuming fence
boundaries; duplicate appendix root labels; Typst asset-root boundary; cwd-dependent Quarto format-download
path; live wrapped-label link. Final consumer checks cover these. Several patch-context misses corrected
without writes. One sandbox Quarto probe failed with invalid subprocess handle; established watch environment
completed it. No permissions relaxed or automatic-review rejection. Historical failed runs are not passes.

Next: coordinator reviews/commits these five paths and transfers to s1; writer performs combined website/full
visual acceptance, then P6. No landing to main before P6. Worker source writes stopped.
