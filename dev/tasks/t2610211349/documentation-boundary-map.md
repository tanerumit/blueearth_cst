# P1 documentation boundary map and chapter outlines

Task: t2610211349. Coordinator: cst-main. Worker: s1, technical-writer, degraded generic runtime.
Status: P1–P2 reviewed; structure and scope approved; P3 pilot authorized. No migration has begun.

Coordinator status: P1–P2 completed on 2026-10-26. The final P2 reconciliation addendum below governs
where it refines the original proposal. All 55 original source dispositions remain; external consumers
are listed separately. The original reviewed revision is retained in commit `6570242c`.

## Input and authority

All review sources were read from `C:/Users/taner/workspace/blueearth_cst`, main at
`58efe411119af402195727ea0ad3d7b6f92c438d`. The inventory's recorded source commit is `145d23e6`;
its 55 paths were reconciled against current main rather than the stale detached s1 tree.
The current working-tree task note and execution plan had coordinator changes when reading began.
The execution log also had coordinator changes by the closing status check. These were preserved.

Inputs read completely: the flat task note, execution plan, inventory dated 2026-10-26,
landscape assessment dated 2026-10-26, workflow execution log, canonical technical-writer role,
and governing documentation guidance. The task records are evidence, not editorial review targets.

Scope is exactly the 55 inventory sources. Excluded as review targets: `dev/reference`, `dev/records`,
`docs/references`, `.github`, changelog/log files, agent instructions, legal material, task records,
and generated site copies. Some governing references and implementation surfaces were consulted as
evidence without becoming additional dispositions. No source edits, Git mutations, STATUS updates,
builds, model runs, delegation, or publication occurred. Only this later-authorized scratch return was saved.

## Proposed boundaries

Owner decision, 2026-10-26: the three central document structures are approved. User-guide and
technical-manual writing take priority; scientific-approach writing is deferred. Its outline and
source dispositions remain retained for later work. The owner subsequently approved bounded generated-case
instruction reconciliation, initial tracked source-path compatibility pages, and a table-level first
publication with surface construction deferred (1A, 2A, 3A). These decisions resolve the corresponding
choices in the historical proposal and reconciliation below. The owner subsequently authorized P3 in
s2 at medium effort, returning the pilot before migration. See the execution plan for this tranche.

Centralize the reader journeys, with local sources retained where a directory reader needs their detail.
Proposed collection roots are `docs/guide/`, `docs/technical-manual/`, and `docs/scientific-approach/`.
Quick start is one prominently linked chapter in the user guide, not a second source collection.
`docs/site/` remains the presentation layer, landing page, error page, navigation and styles.
These paths and navigation changes are proposals for owner decision after P2.

The user guide owns actions and interpretation at the point of use. The technical manual owns the public
implementation account: configuration semantics, workflow boundaries, retained products and extensions.
Scientific approach owns methodological reasoning, assumptions and limits. Executable schemas, parsers,
registries and tests remain stronger authorities for machine contracts than prose.
Local indicator READMEs own set-specific conventions; central publications include selected local content
rather than maintaining independently editable copies. Existing excluded maintainer references retain their
current ownership and are not silently migrated into a new public manual.

Useful repetition: a brief reminder that WF2 is an overlay, that WF1 and WF3 independently supply WF4,
that input data are external, or that return levels are screening outputs. Those reminders prevent a wrong
action and may remain in each relevant journey. Detailed schemas, table joins, fixed calculation policies,
publication rules and migration accounts should each have one maintained prose home.

In the tables, **UG** means `docs/guide/`, **TM** means `docs/technical-manual/`, and **SA** means
`docs/scientific-approach/`. A destination is relative to the repository unless a prefix is expanded.
“Retain” includes updating links after an approved migration; it does not certify current content accuracy.
“Incorporate” means transfer content into the stated owner and retire its independent account only after
navigation continuity is demonstrated. No row authorizes deletion of historical evidence or code.

## Complete source dispositions: toolbox users and practitioners, 28

| ID | Inventoried source | Reader question and current role | Proposed owner, action and destination | Concrete overlap evidence | Migration and link consequences |
|---|---|---|---|---|---|
| 01 | `docs/guide/assets/shape-of-a-run.html` | How do the five workflows relate? Interactive execution-order explanation. | UG asset; **retain** at the existing path, with a static/text equivalent derived from the same description. | Its five node explanations repeat the quick-start workflow summary; both correctly distinguish order from dependencies. This is useful alternate presentation, not another contract. | Preserve the iframe/resource URL. Carry every essential node explanation into PDF/plain Markdown; a screenshot of the initial “Select a workflow” state is insufficient. |
| 02 | `docs/guide/benchmarking.md` | What do timings and resource measurements mean? User explanation plus diagnostic-record reference. | **Split**: retain UG `benchmarking.md` for reading reports; put exact diagnostic fields/lifecycle in TM `execution-and-provenance.md`. | Both this page and `running.md#execution-logs-and-benchmarks` explain elapsed versus summed job time, missing measurements, per-attempt folders and WF4 resource traces. | Keep the guide URL and existing useful headings. Link exact record semantics to TM; do not imply missing resource observations are zero or that all workflows have WF4 sampling. |
| 03 | `docs/guide/configuration.md` | What must I choose for my case? Procedure mixed with detailed field/path contracts. | **Split**: UG `configuration.md` owns choices; TM `configuration.md` owns composition, precedence, schema/path semantics and field constraints. | Schema-3 path rules and workflow enablement recur in starter README; WF1 YAML appears here and in its workflow reference; palette schemas recur in local plotting README. | Preserve the guide URL, `how-paths-are-read` landing anchor and migration route. Link rather than copy complete YAML contracts; correct examples only in a later accuracy packet. |
| 04 | `docs/guide/outputs.md` | Where are my results, and how do I read them? Output walkthrough plus extensive contract/history account. | **Split**: UG `outputs.md` owns discovery and worked joins; TM `retained-handoffs.md` owns layouts/publication/integrity; TM `results-transfer.md` owns transfer guarantees; local set sources own calculation conventions. | Joins and group/reference semantics recur in SA conventions; immutable/named exports recur in retained-handoffs and WF3/WF4; invocation evidence recurs in benchmarking. | Preserve guide anchors or provide old-to-new landing anchors. Keep necessary compatibility actions discoverable, not an unqualified historical narrative. Include status/reason interpretation after contract reconciliation. |
| 05 | `docs/guide/quick-start.md` | How do I execute the supplied example and recognize its products? First-example tutorial. | UG; **retain and shorten** at the existing path, using the single quick-start outline below. | It repeats setup versions, workflow summaries and output trees from root README/running/outputs, but these brief prerequisites and success cues serve the first-run reader. | Keep direct site/repository links. Link detailed setup and outputs; retain the external-data gate and qualified runtime expectations. Add static diagram fallback before promising PDF completeness. |
| 06 | `docs/guide/running.md` | How do I launch, resume or change an assessment? Operational guide carrying detailed diagnostics and identity rules. | **Split**: UG `running.md` owns supported actions/recovery; UG `new-case.md` owns scaffolding; TM `execution-and-provenance.md` and `retained-handoffs.md` own detailed records/reuse semantics. | The scaffolder checklist overlaps starter README; log/resource interpretation overlaps benchmarking; named indicator publication and input identity overlap WF4 and retained-handoffs. | Preserve entry URL and important anchors for create-case, one-workflow, rebuild and experiment selection. Keep destructive-reset consequences beside the command. Do not turn shortening into removal of recovery guidance. |
| 07 | `docs/notebooks/Climate projections.ipynb` | How do I inspect projection composition and change factors interactively? Executable teaching notebook. | Notebook-local; **retain**, subject to a later current-interface repair; central UG `notebooks.md` links it. | Its rule table duplicates WF2 reference, and source/window explanations duplicate datasets and SA climate information. Its composition/annual/monthly reading sequence is distinctive teaching value. | Keep notebook filename and cross-notebook links initially. Replace exhaustive tables with links later; execution remains opt-in. Old figure paths and raw config access need deferred accuracy work. Do not publish unexecuted outputs as retained results. |
| 08 | `docs/notebooks/Climate Stress Test.ipynb` | How do I trace runs into indicators and a response surface? Executable analysis walkthrough. | Notebook-local; **retain and shorten** repeated contracts; TM owns public join/axis reference, SA owns interpretation. | Cells 23–34 repeat run/group joins, reference handling and detailed axis derivation; outputs/SA conventions repeat joins. The notebook explicitly transcribes HM-7 instead of importing a helper. | Preserve teaching sequence and explicit provenance. Defer reconciliation of current named-set reading and axis authority. Do not replace deliberate independent consumer code with a helper merely to reduce duplication. |
| 09 | `docs/notebooks/Model building.ipynb` | How do I build and inspect a basin model? Executable WF1 tutorial with reference tables and interpretation. | Notebook-local; **retain and shorten**, with later interface/claim repair; UG `notebooks.md` states prerequisites/status. | Rule/config tables duplicate WF1 reference and templates; optional CSV schema duplicates template README. Basin/forcing/station inspection is useful reader-specific context. | Keep filename initially. Raw YAML workflow reads, old rule/figure paths, model dependency claims and KGE interpretation thresholds are deferred accuracy questions. Do not present this as a verified current first-run route. |
| 10 | `docs/notebooks/README.md` | How do I use and maintain these notebooks? User launcher plus publication policy/history. | **Split**: retain local launcher/source-only rules; UG `notebooks.md` gives learning routes; local `dev/scripts/environment-notes.md#notebook-publication` may hold bounded maintenance procedure if approved. | Installation repeats setup; source/data inventory repeats datasets; long blob-size and policy-reversal narrative repeats notebook banners. The operational distinction between source and rendered artifact is essential. | Preserve local index and source-only contract. Link historical evidence rather than reproduce chronology. Any rendered artifact must have a real discoverable location and provenance; none is established by this review. |
| 11 | `docs/README.md` | Where is the authoritative documentation, and what is generated? Reader/source map. | Central documentation index; **retain and shorten** in place. | Its source/staging explanation overlaps `_quarto.yml` and the staging script; its start route overlaps root README/site home, appropriately at another entry surface. | Update all collection/source links together. Explain local-source inclusion and HTML/PDF source ownership here once; link detailed publishing maintenance to its existing owner. |
| 12 | `docs/site/404.qmd` | How do I recover from a missing site address? Web recovery page. | Site-local; **retain and shorten** in place. | Its suggested destinations mirror site home; its “technical background not yet published” explanation is broader than the current scientific/reference collections warrant. | Preserve the 404 endpoint. Offer current routes/search and intentional repository-only boundaries; do not use a generic 404 as a substitute for move redirects. Deferred accuracy correction for obsolete publication wording. |
| 13 | `docs/site/index.qmd` | What does CST do, and where should I begin? Public orientation and approach summary. | Site-local; **shorten** in place, linking the four collections. | Assessment logic and workflow list repeat SA overview and workflows reference. A concise adoption-oriented account is useful; the full method narrative need not be repeated. | Preserve homepage and start routes. Keep screening limitations and external-data access visible; avoid suggesting a separately maintained frontend is part of this repository. |
| 14 | `docs/site/setup/env-setup-notes.md` | How do I diagnose environment failures or understand local workarounds? Mixed user recovery, maintenance, staging and incident history. | **Split**: actionable user symptoms to UG `troubleshooting.md`; detailed local maintenance to proposed `dev/scripts/environment-notes.md`; implementation summary to TM `environment.md` by reference. | Reinstallation/Julia/library advice overlaps install; staging commands overlap dev/scripts index; conda-era pin tables and timing incidents serve historical diagnosis rather than normal setup. | Preserve old setup URL with a short routing page if accepted. Keep historical evidence recoverable and clearly scoped; do not migrate excluded records. New local guide is procedural help for adjacent tools, not a competing policy reference. |
| 15 | `docs/site/setup/install.md` | How do I install and check a usable environment? Windows install plus substantial developer session/runtime operations. | **Split**: normal installation to UG `install.md`; developer borrowing/isolation recipes to proposed local `dev/scripts/environment-notes.md#session-runtimes`. | Basic setup repeats root README, quick start and notebook README. Session allocation and borrowing are a different reader task from first installation. | Preserve `setup/install.html` through staging/compatibility routing; update repository source links. Defer verification of exact pins, Defender advice and diagnostic commands. Separate a wiring check from optional data-dependent E2E; avoid baseline execution as routine first setup. |
| 16 | `docs/site/toolbox-reference/assessment-workflow.qmd` | What is the assessment sequence versus dependency structure? Hybrid workflow/method overview. | **Incorporate** into TM `workflows.md`; retain a compact compatibility landing page at the old published address. | Its five-stage product table and independence account substantially duplicate `workflows.qmd`; historical/source-selection explanations also occur in SA climate information. | Preserve incoming links and useful old anchors. Link SA for rationale. Do not retain two independently maintained workflow overview tables. |
| 17 | `docs/site/toolbox-reference/datasets.qmd` | What source classes are consumed, and what changes when I replace one? Source-role and substitution reference. | TM; **retain** content at proposed `datasets.md`, with scientific rationale linked to SA. | Source classes recur in notebook README; historical forcing's dual role recurs in SA climate information; catalog path rules recur in configuration guide. | Preserve public datasets URL. Keep catalog/code as authority for enabled entries, not a copied model/data inventory. Defer reconciliation of VITO/local versus GlobCover/P-drive examples. |
| 18 | `docs/site/toolbox-reference/modeling-tools.qmd` | Which component performs which operation? Short component table. | **Incorporate** into TM `overview.md#components`, not another independent chapter. | HydroMT/Wflow/weathergenr roles also appear in SA models-and-methods; this page adds Snakemake implementation ownership. | Preserve old modeling-tools URL as a redirect or landing section. SA retains scientific assumptions; TM retains orchestration and interface roles. |
| 19 | `docs/site/toolbox-reference/overview.qmd` | What implementation reference is available? Collection index with architecture marked planned. | TM; **retain and expand structurally** as `overview.md`, using existing components and boundaries, not invented architecture. | Its workflow/tools/datasets links overlap the workflows index; its planned architecture line exposes a genuine missing navigation/account rather than redundant prose. | Keep the toolbox-reference entry URL even if display title becomes Technical manual. Add links to contracts/extensions and clear supported-versus-planned scope. |
| 20 | `docs/site/toolbox-reference/retained-handoffs.qmd` | What is retained, mutable, immutable and reusable? Cross-workflow publication reference. | TM; **retain and reconcile** as `retained-handoffs.md`, the detailed prose owner for these public handoffs. | Layout/publication details recur in outputs, WF3 and WF4; startup identity/catalog checking recurs in running. Its collection path account differs from newer `_engine/data` descriptions. | Preserve URL and existing inbound links from excluded references. Reconcile paths before centralizing; do not promote a convenient existing table into authority. Keep implementation/schema authority explicit. |
| 21 | `docs/site/toolbox-reference/workflow-analyze-climate.qmd` | What does WF0 consume, compute and produce? Rule/reference, interpretation and case-specific findings. | **Split**: TM `workflow-analyze-climate.md` owns workflow contract; SA `climate-information.md` owns general diagnostic interpretation; case-specific findings stay qualified pending retention decision. | Climate extraction/map policy overlaps configuration and WF1 shared-map account. Long Ntoum trend/homogeneity findings differ from generic workflow documentation. | Preserve workflow URL/rule anchors. Separate general method limits from basin-specific numerical claims; no relocation into excluded records is authorized. Defer evidence/retention of those claims to owner/P4C. |
| 22 | `docs/site/toolbox-reference/workflow-analyze-projections.qmd` | What are WF2's inputs, rules and products? Workflow plus diagnostic method/output reference. | TM; **retain**, moving shared publication/transfer detail to the named contract owners and scientific rationale to SA links. Destination `workflow-analyze-projections.md`. | Figure folders/captions and production records repeat outputs; time/coverage rules connect to SA conventions; WF2 overlay reminder is useful context. | Preserve URL and rule labels. Link TM results-transfer and retained-handoffs. Reconcile version-sensitive folder/annotation accounts later; keep unavailable combinations explicit. |
| 23 | `docs/site/toolbox-reference/workflow-build-model.qmd` | How is the model constructed, forced and evaluated? WF1 contract plus extensive figure/statistic descriptions. | **Split**: TM `workflow-build-model.md` owns stages/configuration/products; SA models-and-methods owns general evaluation interpretation; per-output implementation conventions stay in TM. | Historical period and example YAML duplicate configuration guide. Shared map/completeness account overlaps WF0; temperature naming and annual aggregation overlap local/default indicator guidance. | Preserve workflow URL and reference anchors. Link exact output/figure definitions rather than duplicate inventories. No scientific convention changes are proposed by this split. |
| 24 | `docs/site/toolbox-reference/workflow-generate-scenarios.qmd` | What does WF3 publish and how is it launched? Workflow/launcher contract. | TM; **retain** as `workflow-generate-scenarios.md`; shared collection/publication semantics link to retained-handoffs. | Immutable collection, stable exports and ready-marker account recur in outputs and retained-handoffs. Grid rationale recurs in SA methods. | Preserve URL, explicitly distinguish wrapper steps from Snakemake rules. Keep owned-runner requirement and model/CMIP6 independence close to invocation; defer old collection-path correction. |
| 25 | `docs/site/toolbox-reference/workflow-simulate-system.qmd` | How do simulation and indicator requests work? WF4 reference, selection tutorial, set conventions and integrity commands. | **Split**: TM `workflow-simulate-system.md` owns WF4; TM `indicator-requests.md` owns selection/evaluation contract; UG `indicators.md` owns choosing/recalculating; local set READMEs own detailed conventions. | ERFA pulse/completeness/timing paragraphs repeat its local README; crop-water Qcrit rules repeat its local README; plain-module authoring repeats module README. | Preserve workflow URL with links to new sections. Include local convention sources in offline manual. Keep integrity inspection versus numerical recheck distinct; do not remove unsupported-probability/partial-evaluation caveats. |
| 26 | `docs/site/toolbox-reference/workflows.qmd` | Which workflow owns a product, and where is detail? Reference index with console behavior. | TM; **retain** as `workflows.md`, incorporating assessment-workflow; move detailed diagnostic presentation semantics to execution/provenance. | Stage table/independence repeats assessment-workflow; console count/verdict account repeats running and workflow pages. Short route summaries are useful; repeated detailed console rules are not. | Preserve workflows URL and links to all five workflow pages. Distinguish run order, producer dependencies and optional analyses in one central map. |
| 27 | `README.md` | Is this toolbox relevant, and where do I start? Repository orientation plus a runnable preview. | Root-local; **shorten** in place. | Julia/install commands repeat install; first-run command and product summary repeat quick start; workflow table repeats central index. Short adoption/data-access context is useful. | Preserve README links. Keep one clearly prerequisite-qualified command if useful, but send completion/recovery to quick start. Replace exhaustive maps with collection routes; retain license and fork identity. |
| 28 | `scripts/README.md` | Which executable entry point should I use? Local command discovery. | Local; **retain** in place, linking UG procedures and TM interfaces. | Runner descriptions overlap running guide but identify executable ownership rather than teaching the same procedure. It lists transfer/scaffold/benchmark tools without complete contracts. | Keep local relative script links; add central discovery for indicator inspection if later verified/assigned. Do not turn this into a second flag reference or omit owned WF3/WF4 boundaries. |

## Complete source dispositions: scientific explanation, 4

| ID | Inventoried source | Reader question and current role | Proposed owner, action and destination | Concrete overlap evidence | Migration and link consequences |
|---|---|---|---|---|---|
| 29 | `docs/site/scientific-approach/climate-information.qmd` | Why are historical climate, generated weather and projections different? Method explanation. | SA; **retain** as `climate-information.md`, authoritative for their distinct scientific roles. | Its three-information table expands reminders in homepage/quick start; its dual historical role overlaps datasets. This deeper conceptual account is useful, while catalog mechanics belong in TM. | Preserve scientific URL; link dataset selection and workflow controls. Keep scenario neutrality and conditional variability clear without copying configuration contracts. |
| 30 | `docs/site/scientific-approach/conventions-and-interpretation.qmd` | What do axes, baselines, ensembles and return levels mean? Scientific interpretation mixed with exact joins. | **Split**: SA `conventions-and-interpretation.md` owns scientific meaning; TM retained-handoffs owns exact identifiers/joins and export schema. | Run/group/st_id joins duplicate outputs; equal-weight/pooled policies duplicate default/module guidance; return-level qualification repeats outputs and flood/default set READMEs. | Preserve URL and interpretation headings. Include brief consequences and links at point of use; never remove reference/baseline or screening caveats merely because exact mechanics move. |
| 31 | `docs/site/scientific-approach/models-and-methods.qmd` | Why these model/generator/indicator methods, and what do they establish? Method overview. | SA; **retain** as `models-and-methods.md`; link set-specific conventions instead of duplicating formulas. | Component roles overlap modeling-tools; perturbation choices overlap WF3; projection/indicator roles overlap climate-information. Scientific mechanisms and adequacy limits justify a separate explanation. | Preserve scientific URL and `wflow-sbm-and-the-historical-reference` anchor. Keep implemented/evaluated/illustrative distinctions and qualified upstream citations. No new empirical adequacy claims. |
| 32 | `docs/site/scientific-approach/overview.qmd` | What assessment question does this approach answer? Scientific collection entry point. | SA; **shorten** into `overview.md`, retaining assessment logic and scope. | Homepage and assessment-workflow repeat the response-surface/overlay sequence. Here the compact conceptual chain orients scientific readers; detailed operations belong elsewhere. | Preserve scientific entry URL. Explain outputs versus analyst-supplied thresholds and point to the three deeper method chapters. Keep the 2025 note explicitly historical rather than current implementation reference. |

## Complete source dispositions: indicator users and extension authors, 6

| ID | Inventoried source | Reader question and current role | Proposed owner, action and destination | Concrete overlap evidence | Migration and link consequences |
|---|---|---|---|---|---|
| 33 | `blueearth_cst/indicators/README.md` | How do I call or extend independent calculations? Module orientation, Python example, extension and identity contract. | Local calculation-module owner; **retain** and selectively include in TM `indicator-extension.md`. UG links only the user-level selection route. | WF4 repeats file responsibilities, trusted code versus YAML selection and authoring guidance. This README also explicitly delegates set interpretation to local READMEs, so absorbing all set science here would violate its useful boundary. | Preserve package-relative links and plain-Python route. Include extension contract once in offline TM. Keep source/checker identity and WF4 boundary explicit; later example changes require relevant language checks. |
| 34 | `blueearth_cst/indicators/sets/crop_water/README.md` | What do crop-water indicators measure and require? Set-specific methods, thresholds and limits. | Local set owner; **retain** as canonical source; include in TM indicator-set appendix, link from SA/UG. | WF4 duplicates the Qcrit baseline rule, dry-run behavior, seasonal choices and ET-proxy limits. This local table uniquely puts formulas, overlapping May seasons and fixed recharge year together. | Retain local location. Central user procedure gives a minimal selection then includes/links this source for the exact rule. Do not merge its fixed calendar with generic water-year policy or imply crop yield/damage capability. |
| 35 | `blueearth_cst/indicators/sets/default/README.md` | What are default reductions and their caveats? Compact set conventions. | Local set owner; **retain**, included in TM set appendix. | Annual partial-block/missingness and equal-weight versus pooled reductions recur in outputs/SA conventions; temperature and return-level rules recur in WF4. | Keep module link and code-owned registration mapping. Central pages retain the consequences, not another complete policy list. Preserve the distinction between annual depth and duration-normalized rates. |
| 36 | `blueearth_cst/indicators/sets/eflow_erfa/README.md` | Which ERFA defaults were ported, and how do they differ? Scientific/implementation provenance and fixed conventions. | Local set owner; **retain**, include in TM set appendix; SA gives only rationale/limits. | WF4 duplicates 70-indicator count, completeness, pulses, cross-year windows and undefined timing. This README uniquely identifies source revision, oracle and omitted modes. | Preserve oracle provenance link and fixed-default account. Keep ecological risk classification explicitly outside scope; verify included provenance remains reachable offline or mark its online/repository dependency. |
| 37 | `blueearth_cst/indicators/sets/flood_risk/README.md` | What do flood declarations estimate, and which are qualified? Opt-in hazard and qualification limits. | Local set owner; **retain**, include in TM set appendix; SA links qualification meaning. | WF4 reproduces example periods and 2-/10-year eligibility; outputs repeats general screening limits. Here the exact refusal domain is essential local information. | Preserve local warning and qualified-period constraints in any inclusion. Do not advertise selecting the entire set as a successful example or relabel hazards as damage/risk estimates. |
| 38 | `blueearth_cst/indicators/sets/flow_regime/README.md` | What additions and aliases are in this set? Set-level reduction semantics. | Local set owner; **retain**, include in TM set appendix. | WF4 lists optional additions; module/default READMEs cover general authoring and group policies. Whole-period sample weighting versus equal-block annual means is a distinctive explanation worth retaining. | Keep module-authoring link and alias names. Central selection page links this source rather than repeating window/missingness rules. No renaming of existing registered selectors. |

## Complete source dispositions: configuration users and maintainers, 9

| ID | Inventoried source | Reader question and current role | Proposed owner, action and destination | Concrete overlap evidence | Migration and link consequences |
|---|---|---|---|---|---|
| 39 | `config/basemap/README.md` | What is this vendored map asset and how is it rebuilt? Asset provenance and maintenance recipe. | Local asset owner; **retain** in place; TM datasets gives a short locator-asset distinction. | Repository layout also explains why Natural Earth is vendored. The README alone provides layers, provenance and rebuild code, which serve maintenance rather than normal basin setup. | Preserve adjacency/provenance. Do not fold it into supplied scientific datasets or imply the repository distributes real basin forcing. Rebuild recipe remains opt-in maintenance. |
| 40 | `config/catalogs/archive/README.md` | Why are these catalogs archived and which old configs use them? Local compatibility/history orientation. | Local archive owner; **retain and shorten** only action-irrelevant narrative after evidence review. | It pairs explicitly with templates/archive and repeats the archive event; former-path map constraints are maintenance-specific and not duplicated by central user guide. | Keep pairing and historical-reference paths valid. Exclude archive content from supported setup/manual default routes. No deletion or rewriting of historical path maps is proposed. |
| 41 | `config/defaults/README.md` | Which nearby YAML files change runs? Local live-default ownership with migration history. | Local defaults owner; **shorten** in place; TM configuration explains categories by link. | Guide configuration repeats defaults/templates distinction; templates README repeats their historical split. Generated archive-path prose differs from newer guide output accounts. | Keep file-consumer table only after later reconciliation. Retain present editing consequences; link current archive contract instead of maintaining an older generated-layout narrative. |
| 42 | `config/plotting/README.md` | What appearance settings may I change, and who reads them? Local editing and loader contract. | Local plotting owner; **retain**; selectively include its user-editing section in TM configuration appendix. | Guide configuration repeats palette structure, reload behavior and invalidation; this local source uniquely separates portable plotting core from CST YAML adapters. | UG offers a small choice summary and links here. Keep scientific methods/classification distinct from style knobs; preserve existing plot-style policy link without importing excluded guidance into publication. |
| 43 | `config/templates/archive/README.md` | Can I use these old projection configs? Unsupported-example orientation. | Local archive owner; **retain** in place with a clear unsupported boundary. | Catalog archive README describes the paired event; templates index also labels these unmaintained. The warning and limited test coverage are useful contextual repetition. | Preserve catalog pairing and current-starter links. Do not include archived CMIP5/ISIMIP examples as supported technical-manual workflows; any restoration is separate work. |
| 44 | `config/templates/example-basin/data/README.md` | What should I replace or record in copied case data? Copyable local sidecar instructions. | Starter-local owner; **retain and shorten**, linking central exact format reference. Destination unchanged. | Observation/location schema is detailed in templates README and configuration guide. This source adds the crucial header-only/synthetic-data and provenance warning at the copied file location. | Because this directory is copied outside the toolbox, use resolvable portable/published references rather than fragile source-tree relative links. Preserve the fact that the observation file is not a supplied usable record. |
| 45 | `config/templates/example-basin/notes.md` | How do I record a run worth retaining? Copyable case-history template. | Case-local template owner; **retain** unchanged in role. | Provenance themes overlap outputs and workflow-report guide, but a blank case record is a different artifact, not duplicate explanatory prose. | Keep scaffolder's fresh-history behavior and relative evidence convention. Do not populate with toolbox-task progress or imply each rerun needs a new narrative record. |
| 46 | `config/templates/example-basin/README.md` | How do I configure and run this copied starter? Local adoption checklist and staged run instructions. | Local starter owner; **shorten**, with generic procedure in UG `new-case.md`; retain concrete replacement checklist locally. | Nine-step setup, WF0-first sequencing and runner examples overlap running/configuration. Its actual supplied files, reviewed example grid and disabled workflow state are specific to the starter. | Preserve source/copy usability and links from scaffolder. Link stable central topics from external copies. Do not maintain a second starter or replace example settings with universal assessment recommendations. |
| 47 | `config/templates/README.md` | What can I copy, and what formats/defaults mean? Index mixed with rationale, model inventory and exact CSV contract. | **Split**: local orientation remains; TM `configuration.md` owns general semantics; TM `input-formats.md` owns exact locations/observation formats; rationale belongs in SA or linked local source where appropriate. | Long CMIP6 model list duplicates generated catalog; experiment numbering repeats running; CSV schema appears in model notebook/data README; climate-window wording differs from guide. | Preserve local URL/anchors used by copied data instructions. Replace volatile exhaustive lists with generated/catalog lookup, not another hand-maintained list. Preserve meaningful default rationale after reconciliation; do not claim every CSV scaffold is an observation. |

## Complete source dispositions: developer and maintainer guidance, 8

| ID | Inventoried source | Reader question and current role | Proposed owner, action and destination | Concrete overlap evidence | Migration and link consequences |
|---|---|---|---|---|---|
| 48 | `dev/README.md` | Where do contributors find current rules and evidence? Developer orientation. | Local development index; **retain** in place. | Its placement/lifecycle pointers summarize excluded owning references. This is useful routing, not a second maintained rulebook. | Keep references/tasks/records distinctions and shared-board warning. Link new local environmental procedures if approved; do not publish internal development inventory as a user-manual chapter. |
| 49 | `dev/scripts/README.md` | Which maintenance tool should I use? Local executable and test-library index. | Local maintenance owner; **retain and shorten** inline procedures where a named local guide owns them. | Data-staging entries overlap env-setup-notes; navigation/coordination paragraphs repeat excluded session guidance. Script discovery and test-imported-library distinction are unique local needs. | Link proposed `environment-notes.md` for recipes, existing policy for authority. Preserve vendored-console restriction and report-only cleanup defaults. Verify inventory later rather than promise its present completeness. |
| 50 | `dev/templates/figure-comparison.html` | How can I inspect before/after figures? Empty interactive review implementation. | Local template implementation; **retain** in place. | Its visible controls/help echo the companion Markdown guide, which explains authoring. That UI-level repetition is useful; neither owns scientific plot conventions. | Keep `const items=[]`, offline behavior and local assets. Exclude from central manuals except a developer index link; a static screenshot cannot preserve comparison interaction. No UI redesign or browser QA was performed. |
| 51 | `dev/templates/figure-comparison.md` | How do I populate and use the comparison template? Local authoring/interaction guide. | Local template owner; **retain** in place. | UI control descriptions overlap HTML intentionally; scratch placement and figure-style policies already have excluded owners and are linked. | Preserve HTML pairing and JSON-escaping requirement. Keep actual reports untracked and in task scratch. Link policy instead of adding another lifecycle or scientific-style rulebook. |
| 52 | `dev/templates/lane-status.md` | What belongs in a lane's STATUS snapshot? Blank maintenance template. | Local template owner; **retain** in place. | Its fields implement the linked lane-status convention; dev/templates index already supplies the route. This is an instance scaffold, not redundant policy. | Preserve filename and current policy link. Do not include in public manuals or populate from another lane/task. No STATUS change was made in this assignment. |
| 53 | `dev/templates/README.md` | Which reusable developer template fits my task? Local template index. | Local template owner; **retain** in place. | It summarizes each companion guide but does not repeat its schema. Scratch and retention details are already pointers to excluded owners. | Preserve paired HTML/Markdown links. Keep report templates separate from populated evidence and scientific-style decisions. |
| 54 | `dev/templates/workflow-report.html` | How can I browse/share one workflow's evidence? Empty offline report prototype. | Local template implementation; **retain** in place. | Its fields/headings mirror companion Markdown schema. It includes interactive gallery, method disclosure and browser-print behavior, not an engine-produced report contract. | Preserve report-data/renderer separation and embedded-image boundary. Do not add to automatic pipeline or central PDF assembly. UI reference to a populated WF0 example needs deferred discoverability checking. |
| 55 | `dev/templates/workflow-report.md` | How do I populate, qualify and print the report? Authoring guide plus scientific reporting rules. | Local template owner; **retain**, shortening generic method repetition to links only when meaning remains visible. | Workflow roles repeat central workflow map; provenance/limits overlap outputs/SA, but they are necessary instructions to the person making a shareable report. The JSON schema is specific and should stay local. | Preserve prototype/nonautomatic status and paired HTML link. Keep browser-print verification requirement. Do not claim this prototype is the HTML/PDF documentation publishing path. |

Coverage: 55 unique source rows: 28 + 4 + 6 + 9 + 8. No excluded source was added as a review target.
No whole source is proposed for unconditional deletion. The two incorporated overview pages, rows 16 and 18,
lose independent detailed prose only after replacement navigation exists; their public addresses remain
supported.

## Proposed chapter outlines

These are reader contracts and heading maps, not drafted chapters or implemented navigation.
The new chapter destinations below account for split material without adding a second prose authority.

### Quick start: one source at UG `quick-start.md`

Audience: a hydrology/climate-risk practitioner with the installed toolbox and access to the example's
external catalogs. Outcome: run the configured rapid example, locate its records and read one output
correctly.

1. **What you will produce**: preview the five-workflow products and one indicator-reading outcome;
   explicitly distinguish an execution example from an assessment-quality result.
2. **Check feasibility**: link installation; confirm required catalog roots, network, writable output root,
   material compute/storage availability and repository/config revision. Do not imply bundled forcing.
3. **Understand the route**: compact static/text workflow map, optional interactive enhancement;
   WF1 plus WF3 supply WF4, WF2 overlays plausibility, WF0 runs first or alone for source comparison.
4. **Preview this fixed example**: use the current rapid config through the owned runner and dry-run;
   explain that checkpoint-dependent previews may be partial.
5. **Execute**: one supported command after prerequisites; explain where progress and failure evidence appear.
6. **Recognize completion**: exact summary named by the runner, workflow outcomes, ready retained products;
   successful exit alone is not scientific adequacy or proof of all requested outputs.
7. **Read one result**: dictionary, selected table, location, baseline and perturbation membership;
   retain reference rows and interpret units/status. Link the detailed output walkthrough.
8. **Recover or continue**: data/Julia/weather-generator/lock routes; own-basin and deeper reference links.

Do not duplicate full installation, configuration schemas, output trees, migration chronology or formula
lists.
Keep runtime estimates qualified by input/machine evidence. “Rapid” does not mean seconds or universally
cheap.

### User guide: perform and interpret an assessment

| Chapter | Reader outcome and proposed contents | Boundary |
|---|---|---|
| `install.md` | Install supported tools; understand Pixi versus juliaup; verify wiring; check external data feasibility; find recovery. | No developer worktree allocation/borrowing manual; version claims must follow current environment evidence. |
| `quick-start.md` | Complete the single fixed execution/reading arc above. | No alternate source copy or promise of supplied model data. |
| `new-case.md` | Scaffold externally; review catalog coverage, outlet/locations, output root and copied starter; run WF0 alone, choose forcing, then enable downstream work. | Local starter retains file-specific checklist; configuration chapter explains choices rather than repeating it. |
| `configuration.md` | Choose region/resolution, forcing/source period, historical model period, outputs, scenario domain/realizations, projection comparison and presentation. | TM owns exact schemas, path rules and constraints; SA owns scientific design justification. |
| `running.md` | Run all/one workflow, preview, select/resume/new experiment, recalculate indicators, regenerate figures and recover safely. | Exact identity/publication invariants in TM; destructive reset warnings remain beside procedure. |
| `indicators.md` | Choose a set and retained variables; supply case-specific thresholds; distinguish strict/partial, undefined/unavailable; change indicators without rerunning an intact simulation. | Local set conventions included/linked; TM owns request syntax and extension contract. |
| `outputs.md` | Find summaries and products; check completion/currentness; read dictionary/status/units; perform one run join and one group join; retain reference members; share provenance. | TM owns exhaustive retained layouts and compatibility; SA owns inference limits. |
| `benchmarking.md` | Read elapsed time/job samples and WF4 resource traces without conflating them; identify missing coverage. | TM owns exact diagnostics and record lifecycle. |
| `troubleshooting.md` | Symptom → bounded diagnosis → justified remedy → confirmation for installation/data/locks/incompatible requests. | Local maintenance recipes remain beside developer tools; no unqualified incident fix becomes universal advice. |
| `notebooks.md` | Select optional interactive learning; know prerequisites, source-only status, side effects and current verification limits. | The `.ipynb` files remain the only editable teaching source under the recommended initial policy. |

The order supports first example, own basin, repeated operations and interpretation. Troubleshooting is linked
at each likely failure, not required as linear reading. Do not fragment chapters further merely to reduce
size.

### Technical manual: implemented behavior and extension surfaces

| Chapter | Proposed sections | Owner boundary |
|---|---|---|
| `overview.md` | Supported version; computational scope; component roles; source/config/output separation; dependencies and external consumers; routes to reference. | Incorporates modeling-tools. Describe observed implementation; remove “planned” only when actual content exists. |
| `environment.md` | Runtime/dependency ownership; Python/R/Julia division; data/tool availability; what environment provenance does and does not establish. | Link installation and local maintenance recipes; no copied package lock inventory or session policy. |
| `workflows.md` | WF0–WF4 products; run order versus input dependencies; shared producers; optional branches; per-workflow pages. | Incorporates assessment-workflow; one authoritative overview table. |
| `configuration.md` | Project/workflow composition; schema 2/3; declaring-file path bases and `toolbox:`; defaults/templates/catalog roles; validation/precedence; current migration actions. | Parsers/schemas and annotated templates own exact machine contracts. Local README includes remain local sources. |
| `input-formats.md` | Locations/roles/IDs; observations delimiters, dates, units and matching; cataloged forcing requirements; retained response metadata boundaries. | Source-backed contract, not a mirror of complete upstream HydroMT/Wflow manuals. |
| `datasets.md` | Spatial, climate and observation roles; catalog selection/substitution consequences; coverage and provenance; locator asset distinction. | No unsupported catalog/model enumeration; source selection science links SA. |
| Five `workflow-*.md` chapters | Purpose/prerequisites; rule or wrapper-step map; owned settings; inputs; outputs; actionable refusals; links to shared contracts. | Shared detailed semantics are linked, not repeated in each chapter. Preserve WF3 wrapper versus DAG distinction. |
| `retained-handoffs.md` | Collection, simulation and indicator identities; ready/integrity records; immutable data versus named exports; table schemas, joins, reference membership; compatibility and reuse. | One detailed public publication/layout account. Reconcile disagreements before transfer. |
| `execution-and-provenance.md` | Invocation hierarchy; logs/summaries; configuration captures; diagnostic fields and measurement limits; producer attribution; currentness and failure evidence. | UG gives reading procedure; exact code/record fields remain executable authority. |
| `results-transfer.md` | WF2 export/import contents, checks, attribution, differences, refusal/recovery and post-import limits. | UG provides task entry/link; no claim that transferring results recreates the environment or enables continued production. |
| `indicator-requests.md` | Operations/sets/selections; inline/file requests; parameter validation; required inputs; strict/partial; status/reason; publication independence and rechecking. | Set science comes from local canonical sources. |
| `indicator-extension.md` | Module versus WF4 responsibilities; ResponseSeries/context/result; trusted registration; closed parameters; paired inputs; independent checks; identity/dependency boundaries. | Include module README, not another editable copy; preserve public APIs. |
| Indicator-set appendix | Include default, flow_regime, eflow-erfa, crop-water and flood_risk local READMEs with source attribution and adjusted links. | Exact interpretation remains maintained beside calculations. Bibliographic/test evidence is linked and its offline availability disclosed. |
| Response-surface coordinates section | Monthly lookup, supported axis derivation and labelling, baseline exclusion/retention, units, consumer responsibilities. | Placement within retained-handoffs is proposed; current claimed HM-7 authority is unresolved. Do not invent a settled replacement contract. |

The manual describes public implementation boundaries. Excluded `dev/reference` continues to own internal
maintenance and engine-replacement rules. If achieving a complete public contract requires relocating one
of those rules, cst-main must expose that scope/ownership change rather than copy or silently edit it.

### Scientific approach: why and how to interpret

| Chapter | Proposed sections | Boundary |
|---|---|---|
| `overview.md` | Assessment question; bottom-up sensitivity/vulnerability logic; analyst thresholds; intended screening use; limits; route through method chapters. | Compact scientific orientation; no command reference or implied decision automation. |
| `climate-information.md` | Historical forcing and generator conditioning; source quality/coverage; stochastic variability; scenario-neutral domain; projection plausibility and ensemble selection limits. | TM owns source/configuration mechanics. No probability assigned to grid cells from projection spread. |
| `models-and-methods.md` | HydroMT data-to-model role; Wflow-SBM processes enabled by setup; no local calibration; historical evaluation; weather generator mechanisms; perturbations/trajectories; retained responses and indicator families. | Explain established implemented methods and distinguish upstream capability from locally enabled/evaluated behavior. |
| `conventions-and-interpretation.md` | Separate time windows/calendars and baselines; additive temperature and multiplicative/relative precipitation; water-year reductions; spatial support; realization versus pooled summaries; response surfaces and thresholds; uncertainty sources; return-level qualification. | Exact table fields/joins in TM; set-specific formulas and fixed conventions from local README sources. |

Potential deeper sections on historical diagnostics or return-level estimation should be added only when
the evidence and reader question justify them; do not reconstruct the missing figures/platform chapters
of the 2025 note. P4C must trace scientific claims to primary support and attributable evaluation.
This structural pass did not certify literature claims or numerical adequacy.

## Owner choices for decision after P2

| Choice | Recommendation | Alternative and tradeoff / consequence |
|---|---|---|
| Quick-start placement | Keep `docs/guide/quick-start.md` as the one source, prominent in root/site navigation and PDF contents. | A separate quick-start collection adds routing/maintenance without another reader need; a short derived PDF extract is acceptable if it uses the same source. |
| Setup placement and promise | Put user installation inside UG; retain a prominent Setup navigation alias. Separate developer runtime operations into the local maintenance guide proposed above. | Keeping setup source in `docs/site` minimizes initial moves but leaves the source/presentation boundary inconsistent. Windows remains the documented setup route; do not invent Linux parity from available configs. |
| Local-source inclusion | Include the indicator module and all five set READMEs in the offline technical manual; include only relevant config editing/format material. Keep archive/dev templates out. | Links alone are cheaper but make the PDF incomplete for indicator use/extension. Whole-directory inclusion accidentally publishes internal/archive material. Require an explicit inclusion manifest and source attribution. |
| Notebook editable source | Initially retain `.ipynb` as the sole editable tutorial source; repair later in a bounded packet, with no automatic execution during docs rendering. | A text source with generated notebooks may improve reviewability but requires a conversion pilot and metadata/output policy; do not start it within P1 or maintain duplicate prose. Current source-only notebooks contain no supplied results. |
| Static/interactive assets | Text/static workflow explanation is required; interactive diagram enhances HTML. Preserve template HTML as local developer tools. | Dropping interaction loses exploratory value; embedding only HTML breaks PDF/plain-Markdown understanding. Static/interactive variants must share meaning and have captions/alt text. No new design/build is authorized here. |
| PDF composition | One versioned manual with four named parts: quick start (as UG entry), user procedures, technical manual plus selected local appendix, scientific approach. Allow derived part downloads later from the same source list. | Four independent books ease selective distribution but duplicate introductions and complicate cross-book links. Do not include quick-start text twice in one assembled manual. Offline completeness applies to promised included contracts, not every linked upstream manual or test fixture. |
| Source and published URLs | Keep existing `guide/*`, `setup/*`, `toolbox-reference/*` and `scientific-approach/*` public routes where practical; source moves do not require URL renames. | Renaming public routes to match source folders needs an old-to-new URL/anchor map and compatibility mechanism proved in P3. No hosting base URL is established: `_quarto.yml` deliberately lacks `site-url`. Do not invent deployed/PDF URLs. |
| Scientific versus technical detail | SA owns rationale/inference; local sets own fixed calculation conventions; TM owns public implementations/interfaces and includes local sources; UG owns choices/actions. | Copying full policy/formula lists into every collection makes later disagreement likely. Short reader-specific context remains appropriate and should not be removed mechanically. |
| Case-specific findings in WF0 | Hold the numerical findings as qualified existing material until P4C/owner chooses an attributable example or separate retained-evidence treatment. | Silently deleting loses evidence; publishing them as general tool behavior misleads. Moving them into excluded records requires a separate authorized destination/retention decision. |
| Axis/contract and excluded-owner boundary | Mark the detailed axis account unresolved; have P2 identify whether a narrow reconciliation/scope decision is needed before P4B writes it. | Current notebook and axis-module docstrings claim HM-7 defines detailed rules, but the current HM-7 section does not contain them. Treating the notebook, code or older prose as settled authority would exceed this structural assignment. |

All choices above are proposals, not settled owner approvals or P3 instructions. P2 should prioritize
offline completeness, excessive fragmentation, local-copy portability and unresolved ownership over prose
polish.

## Three reader journeys: structural walkthrough results

These are source-based reader-task checks, not observed usability tests or executed examples.

| Journey | Route exercised in source | Result and gap | Proposed structural completion criterion |
|---|---|---|---|
| First example | Root README → setup → quick start → summary/output guide. Compared rapid project/workflow config structure and runner docstring. | A discoverable command route exists and clearly states external P-drive/network requirements. The rapid config is not a supplied self-contained dataset. Setup mixes user/developer tasks; interactive diagram lacks a complete static presentation; output detail overwhelms the first reading task. | A prerequisite-qualified command, partial-DAG explanation, visible summary/product success cues and one interpretable output. Separate wiring success, workflow completion and scientific adequacy. No new runtime promise. |
| Own basin | Root/guide → starter/scaffolder → configuration → running → outputs; read copied data and notes instructions. | The starter enables WF0 alone and keeps other workflow files available. Generic setup/checklists repeat across pages; copied README links can depend on original repository layout. Detailed format/default explanations are spread across templates and guide. | One central procedure with local replacement checklist, portable references, data coverage check, WF0 forcing decision, explicit WF1/WF3 prerequisites and optional WF2 context. User reviews example periods/grid/realizations rather than inheriting assessment recommendations. |
| Interpretation and extension | Output guide → scientific conventions → WF4 → module and five set READMEs → notebook response-surface sequence. | The needed concepts exist but detailed joins/publication/set policies have several homes. Available/undefined/unavailable semantics need one route. Extension boundary is strong locally; set limitations must survive offline inclusion. Axis authority and several current-path/interface questions remain deferred. | Dictionary/units/status → correct run/group/reference joins → method/qualification limits → select/recalculate → trusted extension contract and independent checks. An omitted retained variable requires a new simulation; a different indicator request alone can reuse compatible responses. |

Deferred accuracy questions identified incidentally, not audited further:

- Calendar wording differs: configuration guide calls `climate.window` inclusive calendar years while
  template material calls it water years. Resolve against the current parser/extraction behavior later.
- Some example YAML/path accounts predate schema-3 `toolbox:` and declaring-file bases. The model/projection
  notebooks load raw YAML while current project stanzas contain only enablement/config paths; exact repairs
  belong to the subsequent notebook/interface packet.
- Retained-handoff/WF3 collection paths differ from newer output-guide `_engine/data` accounts.
- Outputs and some workflow pages still describe captioned directories while newer configuration guidance
  describes annotation at ordinary paths. Reconcile once with the implementation owner.
- The output guide's layout/table discussion does not consistently expose the newer status/reason fields
  described by WF4; indicator publication code was consulted only to establish that this is a real boundary.
- Model-building notebook rule/figure names, KGE thresholds and claims about downstream model checks require
  later evidence review. No threshold or adequacy claim is endorsed here.
- Detailed monthly axis rules lack the claimed current HM-7 textual home. No algorithm/API change is proposed.
- Setup security/workaround prescriptions, exact pins, archive-layout claims and notebook rendered-artifact
  availability remain unverified content claims.

## Migration and publication contract proposed for P2/P3

1. Freeze the accepted source-to-owner map and explicit local inclusion list before publication work.
2. Retain canonical Markdown prose outside the site tree where approved; preserve site-local wrappers/routes.
   Generated copies are not independently editable sources.
3. Preserve known published paths and important headings; inspect incoming links, including excluded files,
   as consumers without editing them under this packet. If a preserved route cannot satisfy a consumer,
   report the required scope decision instead of quietly expanding work.
4. Rewrite links against both canonical source and publication layouts. Current staging handles only five
   named guides and one literal link rewrite; it is evidence of a pattern, not proof of general inclusion.
5. Assemble only approved local content. No automatic publication of `dev/`, archives, upstream manuals,
   task evidence or notebooks. The manual can link intentionally external/repository evidence and label it.
6. Rendering must not launch model/data acquisition or notebook execution. `freeze: auto` is not an
   unconditional no-execution guarantee; P3 must inspect and prove the selected render path.
7. P3 chooses/tests PDF tooling and URL/anchor handling. Existing `docs-build` is HTML-oriented and does not
   establish PDF support. Browser print of workflow-report.html is a separate prototype, not that solution.
8. P4 reconciles content once in its accepted owner; P5 assembles and checks continuity; P6 walks journeys
   from fresh context. This return authorizes none of those later phases.

## Checks and evidence actually obtained

- Read all 55 sources from main. Notebooks were parsed as JSON and all source cells inspected:
  Model building 43 cells, Climate projections 33, Climate Stress Test 37. All three had zero output-bearing
  cells and zero non-null execution counts. No notebook was executed.
- Read all three inventoried HTML sources, including full CSS/markup/script content, through consecutive
  bounded reads. This is source inspection only: no browser, interaction, accessibility-conformance or print
  QA.
- Reconciled inventory links to files using PowerShell regex extraction, URI decoding, `Test-Path` and
  `git -C <main> ls-files`: 55 paths, 55 unique, zero missing/untracked.
- Ran a bounded relative Markdown file-link scan across non-HTML inventory sources, including notebook
  cell text: 196 link occurrences. Raw scan found 19 absent site/guide copies; each resolved through the
  inspected pre-render source mapping to an existing canonical guide. Zero unresolved file targets after
  that mapping. Anchors, external URLs, HTML links and rendered destinations were not validated.
- Consulted `_quarto.yml`, `stage_site_guides.py`, `tests/test_site_guides.py`, documentation Pixi task
  definitions, relevant runner/config-composition/path interfaces, rapid/starter config structure,
  indicator publication field/schema excerpts and the axis-module header. These were bounded evidence
  reads, not a full implementation/content-accuracy audit or executed test suite.
- Git read-only checks: main remained `58efe411`, ahead of origin/main by 12; coordinator task-record
  changes were present. S1 remained clean and detached during the P1 inspection. No branch was claimed.
- No build, pytest suite, DAG preview, model execution, data acquisition, numerical validation, PDF render,
  browser check or external citation validation was performed. Earlier task-record build evidence is
  historical context and is not claimed as a fresh pass for this proposal.
- Before saving this return, `git check-ignore -v .tmp/tasks/t2610211349/p1-boundary-map.md` matched
  `.gitignore:200:.tmp/`. The file did not exist; `.tmp`, `.tmp/tasks` and the task directory were ordinary
  directories with no reported link target. Only the authorized scratch evidence file was created.

## Role and skills actually loaded/applied

Full canonical role read:
`C:/Users/taner/workspace/brain-infrastructure/artifacts/agents/technical-writer.md`.
Applied its reader-question, one-authoritative-home, prerequisite/output/recovery and evidence-limit rules.
Runtime is degraded generic execution; reading the role does not prove registered persona activation.

For each skill below, checked `_external/<name>/SKILL.md` before using the canonical non-external path.
No external override existed for the first four; tutorial-authoring was resolved with the same precedence.
All applicable SKILL.md bodies were read completely. Truncated combined output was followed by bounded
or individual reads; headings alone were not treated as complete loading.

| Exact skill body | Applied action | Triggered references fully read and phase |
|---|---|---|
| `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/scientific-software-documentation/SKILL.md` | Classify README/guide/method roles, retain scientific qualifications, separate reader journeys and source/publication ownership. | `references/readme-authoring.md`, `site-structure-and-lifecycle.md`, `task-guides-and-troubleshooting.md`, `documentation-review-and-accessibility.md`: loaded for boundary classification, navigation and source-based journey verification. |
| `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/project-reference-docs/SKILL.md` | Canonical-source map, current reference boundaries, safe split/link consequences and history distinction. | `references/current-state-reference.md`, `audit-checklist.md`, `history-and-archaeology.md`: loaded for substantial restructuring proposal, scoped boundary checks and action-changing history treatment. No record was moved/shortened. |
| `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/project-system/SKILL.md` | Respect project placement/lifecycle, local sources and coordinator-owned evidence; return rather than create a shared task record. | `references/layout.md`, `layout-python.md`, `layout-hybrid.md`, `migration.md`, `workflow.md`: loaded for placement/handoff/migration consequences. Hybrid generic layout was not imposed; existing repository layout governs. No creation/scaffolding/cleanup/implementation phase occurred. |
| `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/testing-policy/SKILL.md` | Select source/coverage/link checks appropriate to a structural, evidence-only return; distinguish unexecuted examples from established behavior. | No conditional reference branch was needed: no numerical change, slow suite, borrowed runtime, gate reuse or relevant policy-pin decision. Repository validation reference was read before verification selection. |
| `C:/Users/taner/workspace/brain-infrastructure/artifacts/skills/tutorial-authoring/SKILL.md` | Outline one first-example arc and assess notebook learning versus reference duplication. | `references/checklist.md`: loaded for outlining and source-based tutorial/journey review. Clean-session execution and rendered-output checklist items remain unverified. |

Repository governing material read: main `AGENTS.md`, `dev/reference/README.md`, `dev-documentation.md`,
`dev-repository-layout.md`, `dev-naming-conventions.md`, `dev-validation.md`, `toolbox-indicator-glossary.md`,
and the hydrological-model interface when the HM-7 ownership question arose. S1's local STATUS was read
without updating it; main had no STATUS. Excluded guidance was consulted, not reviewed for revision.

No incomplete applicable skill body or triggered reference remains known. PDF/Quarto implementation,
Python/R editing, citation-management, diagram/plot design, Git workflow, agent routing and publication
skills were not applied: this packet did not perform those governed actions. Their possible later use
is a handoff condition, not claimed skill activation here. No agents were dispatched.

## Measurements and limitations

- P1 first recorded UTC: **2026-10-26 13:00:18 UTC**, after the initial role/input read.
- Structural inspection/checks complete by **2026-10-26 13:11:23 UTC**; observed interval **11m 05s**.
  This is wall-clock turnaround to the ready structural evidence, not model compute time or accepted lead
  time.
- Return-capture follow-up: scratch preflight recorded **2026-10-26 13:15:19 UTC**. File write/verification
  completion is recorded in the closing capture addendum below. Coordinator acceptance time is unknown.
- Requested/owner-verified model and effort: **GPT-6.1-Sol medium**. An attempted `/model gpt-6-sol` command
  occurred, but the coordinator confirmed the UI still reported GPT-6.1-Sol medium. Do not record a fallback
  as effective. Backend identity/effort were not independently observable through the tools.
- Role: requested technical-writer; full canonical role applied manually under degraded generic runtime.
- Input/output/cached token totals and cost: **unknown**; no attributable usage counters were exposed.
- Explicit wait: one shell read returned a session ID after about 10 seconds and completed at the next poll;
  no separate agent/user-decision wait was initiated. Active compute duration and measurement overhead
  unknown.
- First-return acceptance, P2 findings, rework/repair burden and accepted-deliverable lead time: unknown.
  This file captures the complete first structural return for coordinator retention, not an accepted design.
- Boundaries and user-facing layout choices remain proposals. Content accuracy, citation support, external
  availability, command execution, numerical adequacy and rendered/offline usability remain deferred.
- No reusable role/skill change is proposed from this single structural pass. Existing guidance already
  covers source ownership, safe splitting and scoped verification; repository-specific drift belongs here.

Next handoff: cst-main retains this return and commissions the already-planned P2 critique. P2 should test
the 55-row map, three journeys, offline inclusion and unresolved owner choices. No pilot or migration starts
until the owner settles the post-P2 choices and authorizes its dependent packet.

## Return-capture completion addendum

End UTC: **2026-10-26 13:24:34 UTC**, at the completed file/coverage check. First recorded P1 time
to captured return: **24m 16s**; this includes drafting and the capture follow-up, not just inspection.
Capture preflight to completed file check: **9m 15s**. These are observed wall-clock intervals;
active compute time, output-token count and acceptance lead time remain unknown.

Saved-file verification: 55 disposition rows, 55 unique IDs, 55 unique source paths; comparison against
the current inventory produced no differences. The authorized path remains ignored by `.gitignore:200`.
Git status remained clean and detached; no tracked change, claim, commit, merge or landing occurred.
This addendum records successful capture, not coordinator acceptance or a build/test pass.

## P1 addendum: reconciliation of P2 findings

All four findings are accepted. The four collection roles and **55 source dispositions remain unchanged**. The
amendments below refine ownership, compatibility and publication promises; they do not authorize P3, migration
or implementation.

### 1. Generated case instructions — accepted, major; owner scope decision required

**Affected rows:** 06, 10, 44, 46 and 47.
**Affected outlines:** UG `new-case.md`, `configuration.md` and `running.md`; own-basin journey; local-source
inclusion and setup choices.

Amend the own-basin route to distinguish two products:

- **Scaffolded case:** receives generated `INSTRUCTIONS.md`; the scaffolder removes the starter README.
- **Manually copied case:** retains the starter README and its replacement checklist.

The proposed central procedure must explain both routes. Row 46’s shortening cannot, by itself, reconcile the
instructions scaffolded users receive. Row 44 must retain data provenance and header-only observation warnings
beside the copied data.

**Recommendation:** extend a subsequent bounded packet to reconcile generated instructions with the accepted
central procedures. Generated instructions should provide the minimum local commands, prerequisites, output
locations and recovery guidance needed to operate the case, then identify the matching toolbox/documentation
revision. Their procedural detail must not evolve independently.

**Owner choice:** authorize the producer/generated-instruction consumer work, or explicitly defer it. If
deferred, label the first migration as central/source documentation work with scaffolded-instruction
reconciliation outstanding. Do not claim the own-basin journey is fully reconciled.

A version-identifiable locator is also required. An unversioned GitHub `main` link is insufficient for
compatibility, and a textual repository locator alone does not establish offline access. The owner should
decide whether copied cases point to a separately obtained matching documentation bundle, a versioned online
route, or both. No bundle or deployed URL is assumed to exist.

### 2. Repository source links — accepted, major; compatibility choice required

**Affected rows:** 03–04, 11–26 and 29–32 where sources move, split or acquire new destinations.
**Affected outlines:** all relocated TM/SA chapters, setup chapters, and the migration/publication contract.

Add **old repository source path** as a separate migration field from **published URL and anchor**. Preserving
an HTML address does not preserve an excluded maintainer reference linking directly to the old `.qmd` source.

**Recommendation:** retain small tracked compatibility pages at existing moved `.qmd`/setup source paths
during the first migration. They should route repository readers to the canonical source without reproducing
detailed prose. Publication engineering must determine how those wrappers preserve the corresponding rendered
routes without creating duplicate substantive chapters.

**Owner choice:** accept this compatibility footprint, or authorize explicit updates to affected
consumers—including currently excluded consumers. Generated staging copies alone are insufficient because
fresh-checkout source navigation must work before a build.

Amend the **future P3 acceptance specification** to exercise one old source link in an unbuilt checkout and
its rendered route, alongside local-source inclusion and PDF handling. This is a proposed acceptance
amendment; P3 remains held.

### 3. Offline response-surface endpoint — accepted, conditional major; owner promise decision required

**Affected rows:** 04, 08, 25, 30 and 33.
**Affected outlines:** TM response-surface coordinates, UG `outputs.md`/`notebooks.md`, SA conventions,
interpretation/extension journey, and PDF composition choice.

The axis-authority gap cannot be covered by including indicator-set READMEs. The deferred notebook repair
likewise cannot support a promised current offline walkthrough.

**Recommendation for the first publication:** promise **table-level indicator interpretation, selection and
extension**. Explain response surfaces conceptually, but visibly defer supported construction instructions
pending authority reconciliation and a checked worked route. Keep that boundary consistent in the homepage,
outlines, PDF description and journey acceptance criteria.

**Owner alternative:** retain a complete response-surface walkthrough as the promised endpoint. That requires
a narrow assignment to reconcile axis authority and provide an offline worked route before publishing the
promise. It does not imply changing the algorithm.

This condition blocks the broader surface-construction promise, not unrelated documentation work. Neither the
notebook nor implementation comments should silently become the normative replacement for missing contract
text.

### 4. Crop-water preparation ownership — accepted, minor; editorial clarification

**Affected rows:** 25 and 34; supporting links in rows 04 and 33.
**Affected outlines:** TM `indicator-requests.md`, WF4 chapter, indicator-set appendix and UG `indicators.md`.

Clarify row 34: the local crop-water README owns the **complete set-specific preparation contract**, including
Qcrit syntax, historical prerequisites, preparation timing, dry-run behavior, provenance, compatibility and
interpretation.

Central chapters own generic request mechanics and a task-level entry link. They may show a minimal selection
example, but must direct threshold diagnosis to this single complete account. Offline inclusion brings that
account into the manual without creating another editable owner.

This clarification needs no separate user-facing layout decision.

### External consumer dispositions — separate from the 55 rows

| Consumer | Proposed disposition |
|---|---|
| Scaffolded `INSTRUCTIONS.md` and its producer | Reconcile only through an explicitly authorized follow-up scope; otherwise record the outstanding consumer gap. |
| Existing copied case documentation | Preserve local usability; define version-identifiable documentation access without assuming network or supplied bundles. |
| Excluded references linking old source paths | Preserve through tracked compatibility pages, or obtain authority for consumer updates. |
| External surface consumers and axis implementation | Preserve existing behavior; defer normative reconciliation to a narrowly assigned owner. |
| Publication/staging consumers | Exercise source-path and rendered-route continuity in an authorized P3 packet; no changes now. |

### Handoff and execution record

P2 supports the first-example route and the collection structure. The own-basin and interpretation journeys
now have explicit completion limits. Accuracy questions unrelated to these promises remain deferred.

Reused the fully loaded canonical technical-writer role and skills: `scientific-software-documentation`,
`project-reference-docs`, `project-system`, `testing-policy` and `tutorial-authoring`. Applied existing
boundary, migration, source-authority and journey guidance; no new conditional reference was triggered.

Read only the supplied P2 critique; performed no additional investigation, edits, scratch rewrite, Git
changes, builds, runs or delegation. Model/effort remains owner-verified **GPT-6.1-Sol medium**; no effective
fallback is claimed.

**UTC:** start 2026-10-26 13:32:21; final recorded check 13:32:37. Drafting followed that check; exact return
time and token/cost totals are unknown. Coordinator retains the addendum and obtains the identified owner
decisions. **P3 and migration remain held.**
