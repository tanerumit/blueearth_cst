# Ledger — wf2-suite-integration

| ID | Round | Severity | Disposition (accepted / rejected / deferred / withdrawn) | Resolution or rationale | Doc version |
|---|---|---|---|---|---|
| dom-1 | internal | major | accepted | G1 ruling: configured reference if ≥ 30 WY else 1985–2014; both window pairs in record and captions (§ 5.5, § 4). Hollow aligned marker on F3.6b not adopted. | design-v2.md |
| dom-2 | internal | major | accepted | G1 ruling: far-end shift to last complete WY, 30 WY, recorded and captioned (§ 5.6). | design-v2.md |
| dom-3 | internal | major | accepted | G1 ruling: analytic sqrt(F(28,28)) 90 % no-change band on F3.5a/F3.5c (§ 5.7); data-driven variant deferred (§ 8). | design-v2.md |
| dom-4 | internal | major | accepted | G1 ruling: pooled member ratios weighted 1/members-per-model (§ 5.8); known-answer test (d). | design-v2.md |
| dom-5 | internal | major | accepted | One mean-keyed per-period rule for all analysis rows, applied as post-process; kernel untouched; equivalence claim corrected; synthetic test (§ 5.4). Settles the conflict with risk-2. | design-v2.md |
| dom-6 | internal | major | accepted | G1 ruling: k_fam/n_fam, small-change marker, count-not-likelihood wording (§ 5.9, § 4); AR6 simple approach deferred (§ 8). | design-v2.md |
| dom-7 | internal | major | accepted | Known-answer tests (a)–(f) independent of the lab (§ 9.2). | design-v2.md |
| dom-8 | internal | minor | accepted | Trajectory band caption wording; members per model recorded (§ 4). | design-v2.md |
| dom-9 | internal | minor | accepted | Ensemble-spread / families-count-separately caption (§ 4). | design-v2.md |
| dom-10 | internal | minor | accepted | Near-end join rule with calendar check; 2015–2030 unit case (§ 5.6, § 9.2). | design-v2.md |
| dom-11 | internal | minor | accepted | G1 ruling: provisional family from institution, flagged; own family otherwise (§ 6). | design-v2.md |
| dom-12 | internal | minor | accepted | Bands recorded and captioned as display heuristics (§ 5.9). | design-v2.md |
| risk-1 | internal | major | accepted | Parse-time suite_availability from POINTS/ACQUISITION_WINDOWS; undrawable products undeclared and listed; runtime residue raises; rapid/wf2_fast sets pinned (§ 6.1). | design-v2.md |
| risk-2 | internal | major | accepted | Constraint adopted (kernel untouched, aligned CSV byte-identical, synthetic dry byte test). Its proposed per-statistic rule for analysis rows not adopted: cannot cover CV rows and keys on variability rather than dryness (§ 5.4, `internal-review-domain.md:88-113`). | design-v2.md |
| risk-3 | internal | major | accepted | Parse-time analysis_windows shared by paths and 2.05b; Oct WY end, join, no per-member shift; shared windows merge into one folder (§ 5.6, § 4, § 9.2). | design-v2.md |
| risk-4 | internal | major | accepted | 2.05b terminal on gather edges from commit 4 and run on rapid; commit 5 split into 5a/5b (§ 10). | design-v2.md |
| risk-5 | internal | major | accepted | figure_names dropped from 2.05; report.md links figure_captions.md; 2.05b reads no 2.05 output (§ 3). | design-v2.md |
| risk-6 | internal | major | accepted | Parity tables/columns listed; dom-4/dom-6/dom-11 items excluded by name, covered by known-answer tests; unmapped column fails (§ 9.1). | design-v2.md |
| risk-7 | internal | minor | accepted | Additive-only rule stated: call roots, never edit roots, callees or referenced constants (§ 2). | design-v2.md |
| risk-8 | internal | minor | accepted | Dependency recorded in rule-index; WF2 render smoke test (§ 4). | design-v2.md |
| risk-9 | internal | minor | accepted | Three retired targets replaced by two new paths; manifest re-record deferred to pending regeneration (§ 7). | design-v2.md |
| risk-10 | internal | minor | accepted | Retired paths listed in docs and figure_captions.md; tree retired list if one exists, verified in 5b (§ 7). | design-v2.md |
| ext1-1 | ext1 | major | accepted | Per-panel null band (§ 5.7): seeded MC of the exact statistic under a stated white-noise null; CV with mean noise; overlap simulated; model markers vs m-member band; pooled quantiles unbanded; "indistinguishable" removed; coverage tests (§ 9.2). | design-v3.md |
| ext1-2 | ext1 | major | accepted | Run-time availability in 2.05b; 2.06 owned directory() outputs + captions-JSON manifest (precedent `build_model.smk:1051-1056`); empty optional product listed, never fatal; corrupt inputs raise (§ 6.1). Settles Conflicts (2). Supersedes risk-1's "runtime residue raises" mechanism (risk-1 row stands as history). | design-v3.md |
| ext1-3 | ext1 | major | accepted | Statuses insufficient_observations / zero_reference_variability / zero_future_variability; eligible-only log summaries and weights; no floors; tests (§ 5.12, § 9.2). | design-v3.md |
| ext1-4 | ext1 | major | accepted | Season-year contract: in-window ownership, no outside reads, middle-month label, calendar weights, missing-month drop, counts, MIN_SEASON_YEARS; hand-calculated Jan/Oct DJF tests (§ 5.11, § 9.2). | design-v3.md |
| arch-1 | internal-full | major | accepted | New `suite_folders`; `figure_relative_paths` and smk:352-367 constants untouched until 5b deletes them together; 5a moves only 2.06's gather edge; every commit parses (§ 10). | design-v3.md |
| arch-2 | internal-full | major | accepted | Option 2 adopted (owned directories + manifest, with ext1-2); option 1 rejected: value-dependent conditions (§ 5.12, paired points) cannot be known at parse time (§ 6.1, § 8). | design-v3.md |
| arch-3 | internal-full | major | accepted | Tables keyed by window_id, each window computed once, horizons list in record; key assertion in merge test (§ 3, § 9.2). | design-v3.md |
| arch-4 | internal-full | minor | accepted | Formula 5 + 10·n + [n ≥ 2] (§ 4). | design-v3.md |
| arch-5 | internal-full | minor | accepted | Availability moved to run-time `projection_analysis.product_availability`; no availability param on 2.05b (§ 2, § 6.1). | design-v3.md |
| arch-6 | internal-full | minor | accepted | Helpers moved to new library module `projections/series_checks.py` in commit 1; STAGE_B_HASH, REDUCER_HASH and inventory checked (§ 3, § 10). | design-v3.md |
| fit-1 | internal-full | major | accepted | `semantic_tree_diff.py` analysis tier + COVERED rows in commit 4; plots rows in 5a/5b (§ 7, § 11). | design-v3.md |
| fit-2 | internal-full | major | accepted | 5b deletes `tests/test_projection_plots.py`, edits `test_get_change_climate_proj_summary.py` (property moved) and `test_projection_figures.py`; in focused checks (§ 10). | design-v3.md |
| fit-3 | internal-full | major | accepted | Batch gate: test-fast, test-full, test-e2e (whole task, skips read); WF2-leg wording dropped (§ 9.2). | design-v3.md |
| fit-4 | internal-full | major | accepted | Named targets: workflow-analyze-projections.qmd, guide/outputs.qmd, rule-index :95-103, :782-817, :881-908, per commit (§ 7, § 10). | design-v3.md |
| fit-5 | internal-full | minor | accepted | Tables, record, 2.06 folders and caption files in WF2_TARGETS (§ 3). | design-v3.md |
| fit-6 | internal-full | minor | accepted | Script-body NOTE header / no __future__ import for script: modules (§ 3). | design-v3.md |
| fit-7 | internal-full | minor | accepted | save_figure at dpi 600, white facecolor; run_log_core.plural for console, WF0 plural in captions only (§ 3, § 4). | design-v3.md |
| fit-8 | internal-full | minor | accepted | log_row rows with listed caps pointing to analysis_record.json; console spec rewritten in 5b (§ 3, § 7). | design-v3.md |
| fit-9 | internal-full | minor | accepted | import hydromt moved to 5b; re-run claim reworded (commit 1 and 5b, bytes identical each) (§ 3). | design-v3.md |
| fit-10 | internal-full | minor | accepted | Placement checked against repo-layout/package data in commit 2; importlib.resources read; not a config default (§ 6). | design-v3.md |
| fit-11 | internal-full | minor | accepted | § 7 wording precise about prepare_climate_data_catalog imports; diagnostic_figures on the normal ladder (§ 7). | design-v3.md |
| ext2-1 | ext1-scoped | major | accepted | Model-marker band simulates each eligible member with its own reference mean, detrended SD, n and overlap, reduced to the table's geometric mean (external-review-scoped-v3.md:17-19); heterogeneous CV/count coverage tests (§ 5.7, § 9.2). | design-v4.md |
| ext2-2 | ext1-scoped | major | accepted | Per-statistic eligibility: mean-change rows eligible regardless of variability status (external-review-scoped-v3.md:24-26); § 4 and § 6.1 predicates updated; constant-reference test through reduction, availability, rendering (§ 5.12, § 9.2). | design-v4.md |
| ext2-3 | ext1-scoped | minor | accepted | ddof-0 disjoint identity corrected with ((n_f-2)/n_f)/((n_r-2)/n_r) factor (external-review-scoped-v3.md:31-33); 27 vs 29 oracle test (§ 5.7, § 9.2). | design-v4.md |
| ext3-1 | ext3 | major | accepted | Owner arbitration ruling 2026-10-07, fix required (external-review-r2.md:7-11): `mean_change_eligible` keyed by statistic and unit — dry keeps the absolute change eligible, relative ineligible; § 4, § 5.12, § 6.1 predicates aligned; dry-reference test through reduction, availability, agreement, rendering (§ 9.2). | design-v5.md |
| ext3-2 | ext3 | major | accepted | Owner arbitration ruling 2026-10-07, fix required (external-review-r2.md:13-17): `null_ratio_band` takes retained reference/future year coordinates, simulates over their union with original masks and table-identical OLS detrending, coordinates in cache key (§ 5.7); internal-missing-year and nominal-vs-retained overlap coverage tests (§ 9.2). | design-v5.md |
| editorial-1 | G2 | — | accepted | Owner-approved editorial edit at G2: F3.6b eligibility unit pinned to % (no decision change) | wf2-suite-integration-design.md |
