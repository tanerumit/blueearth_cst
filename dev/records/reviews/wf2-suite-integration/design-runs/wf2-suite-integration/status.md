---
run: wf2-suite-integration
target-repo: blueearth_cst
genre: decision-record   # milestone-style design (goal, what changes, alternatives, commit plan)
author-binding: cst-architect
started: 2026-10-07
variant: full
stage: done
external-rounds-completed: 2
allocation: >-
  author cst-architect (opus, default effort); stage 1b domain lens model-validator loading claim-evaluation
  (opus); stage 2 risk lens critical-thinker (opus); stage 4 external codex exec (GPT, independent vendor);
  driver = interactive session (orchestration only). Requested = effective.
dispatches: 13
gates:
  G1: approved 2026-10-07
  G2: approved 2026-10-07
flags: [promoted-lean-to-full, round-2-waiver-reversed]
round-2:
  dispatched: yes
  triggers-checked: [mechanism-changed, rejected-blocking-major]
  fired: [scoped-pass-reraised-ext1-1-ext1-3]
---

- [done] 0-intake — outputs: intake.md (domain content: yes; gate materialization: two pre-change snapshots
  required before the first implementation commit)
- [done] 0-snapshots — P0 change factors (sha256 360d2512…, d41e232d…) and 26 lab result tables + summary.json
  copied to session-1 `.tmp/scratchpad/t2610071652-snapshots/`. Rapid-tree change factors copied too, but they
  date from 2026-09-16, before the lane's WF2 fixes: re-run WF2 on rapid at the lane head before the first
  implementation commit to get a trustworthy before-image.
- [done] 1-draft — outputs: design-v1.md (author reported intake premise corrections: caption contract follows
  WF0's figure_captions.json/.md; more figure_relative_paths consumers; WF0 token match upgraded to high)
- [done] 1b-domain — outputs: internal-review-domain.md (verdict revise; 0 blocking, 7 major, 5 minor;
  premises 7 supported, 1 contested [baseline row: 3 WF2 PNGs are FIGURE_KINDS targets outside the default gate,
  verified check_baseline.py:313-330], 1 untestable [run time])
- [done] G1 — approved 2026-10-07. Provisional alternative: design-v1 (one calculator; rule 2.05b
  prepare_projection_analysis; 2.06 renders; figures replace the five; on by default; WF0 caption contract).
  Rulings (owner, AskUserQuestion):

  | Item | Ruling |
  |---|---|
  | dom-1 windows | Accepted: keep the 30-year analysis window for figures; record both window pairs in the analysis record and caption them; use the configured reference instead of 1985-2014 when it spans >= 30 years |
  | dom-2 far horizon | Accepted: shift the window to fit the data end (e.g. 2071-2100), keep 30 years, record and caption the shift |
  | dom-3 null band | Accepted: no-change sampling band on F3.5a and F3.5c |
  | dom-4 F3.5c weighting | Accepted: weight pooled member ratios 1/members-per-model |
  | dom-6 agreement | Accepted: family counts, small-change marker, count-not-likelihood wording on F5.1 |
  | dom-11 unlisted family | Accepted: provisional family from institution, flagged |
  | dom-5, dom-7 | Accepted by driver as correctness fixes (single dry-reference rule; known-answer tests) |
  | dom-8, 9, 10, 12 (minor) | To the author at r1 |
  | Unavailable products | No placeholder figures; listed as unavailable with reason |
  | Combined cloud | Kept, only when >= 2 horizons |
  | Future folder name | Analysis-window years (period-2036-2065) |
  | Kuma table | Ship model_families.csv only if the Zenodo licence permits; else institution fallback |

  Layout/tree and user-facing inventory: design-v1 § 11 shown as the provisional layout; owner did not object.
- [done] 2-internal-panel — outputs: internal-review-risk.md (verdict revise; 0 blocking, 6 major, 4 minor),
  internal-review-index.md (one conflict: dom-5 vs risk-2 dry-reference rule; no gate return)
- [done] 3-revision-r1 — outputs: design-v2.md, ledger.md (22 rows dom-1..12, risk-1..10; all accepted;
  dom-5/risk-2 conflict resolved as the mean-keyed per-period rule applied as a post-process, kernel untouched)
- [done] 4-external-r1 — outputs: external-review-r1.md (doc_version: design-v2.md; verdict revise; 4 major:
  ext1-1 null band validity, ext1-2 runtime availability vs parse-time declaration, ext1-3 zero variability,
  ext1-4 season boundaries). Read-only intent held (git status clean).
- [done] 5-convergence-r1 — NOT converged (revise, 4 major). Promotion lean -> full (non-convergence after the
  one round): architecture and repo-fit lenses on design-v2; external cap lifted to 2.
- [done] 2b-panel-extension — outputs: internal-review-architecture.md (revise; 3 major, 3 minor),
  internal-review-repo-fit.md (revise; 4 major, 7 minor); index extended with conflict (2): availability
  boundary ext1-2 vs arch-2; no gate return
- [done] 6-revision-r2 — outputs: design-v3.md, ledger rows ext1-1..4, arch-1..6, fit-1..11 (21 accepted;
  mechanisms changed for majors ext1-1, ext1-2/arch-2, ext1-3, ext1-4, arch-1, arch-3; no blocking findings)
- [done] 6-round-2-check — round 2 WAIVED: no blocking fix (no blocking findings) and no rejected blocking/major;
  scoped verification pass on the v2->v3 delta (§ 4, 5.7, 5.11, 5.12, 6.1, 9, 10) with ext1 regression duty
- [done] 6-scoped-pass — outputs: external-review-scoped-v3.md (doc_version: design-v3.md; verdict revise;
  regression: ext1-2, ext1-4 resolved; ext1-1 re-raised as ext2-1 [major], ext1-3 re-raised as ext2-2 [major];
  ext2-3 minor). Read-only held. Faulted resolutions re-open the round-2 trigger (a reviewer must judge).
- [done] 6-revision-r3 — outputs: design-v4.md, ledger rows ext2-1..3 (accepted); driver scope check: hunks only
  in § 4, § 5, § 6.1, § 9.2, Contents, revision log
- [done] 4-external-r2 — outputs: external-review-r2.md (doc_version: design-v4.md; verdict revise; ext3-1 major
  [regression from ext2-2: dry rows lose absolute change, verified design-v4.md:427-429], ext3-2 major
  [pre-existing: band uses counts not retained years, verified design-v4.md:372]). A first launch fired against a
  missing brief and was killed before any output. Read-only held.
- [done] 5-convergence-r2 — NOT converged; cap reached (2 external rounds) -> human arbitration
- [done] arbitration — ext3-1: owner ruled accepted, fix required (eligibility keyed by statistic and unit; dry
  absolute change stays eligible; dry-reference test). ext3-2: owner ruled accepted, fix required (actual
  retained years per member into null_ratio_band, same masks/detrending, cache key, missing-year tests).
  2026-10-07
- [done] 6a-arbitration-revision — outputs: design-v5.md, ledger rows ext3-1..2 (per arbitration rulings); driver
  scope check: hunks only in § 4, § 5.7, § 5.12, § 6.1, § 9.2, Contents, revision log -> pass
- [done] G2 — approved 2026-10-07 (design-v5.md, under arbitration authority); one editorial edit approved: F3.6b
  eligibility pinned to the % unit the cloud plots (no change to decisions)
- [done] 7-finalize — outputs: wf2-suite-integration-design.md (ACCEPTED, F3.6b editorial edit), -ledger.md (editorial-1 row), -intake.md, -external-review-r2.md landed beside the task; diff vs v5 verified 2026-10-07
