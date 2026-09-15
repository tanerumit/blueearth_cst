```yaml
verdict: approve
doc_version: design-v6.md
scope: v5-to-v6 owner-approved interface simplification
```

The delta satisfies the owner’s 2026-09-10 ruling at design level. It removes routine identity selection while retaining exact validation and advanced reuse. This verdict does not authorize implementation or establish empirical correctness.

Review began with `v5-v6.diff`, followed by affected sections and necessary v5/v6 interactions, the owner ruling, its ledger entry, and relevant configuration-composition source. No edits, delegation, tests, or scientific runs were performed; Git status remained unchanged.

| Review question | Verification | Section evidence in design-v6.md |
|---|---|---|
| **1. Routine interface and advanced reuse** | **Pass.** Routine simulation omits `scenario_collection`; users supply the experiment name and scientific/model settings. Internal identities are computed, and routine summaries report paths and the resolved seed. Advanced reuse supplies only `scenario_collection.manifest_path`. Visible `run_id` and `unit_id` remain unchanged. | §§1, 2.4, 5.7, 9.3, 9.5 |
| **2. Deterministic, fail-closed resolution** | **Pass.** Automatic resolution opens only the request-keyed plan, verifies its request and live source inventory, recomputes intent, and validates its named collection. Multiple retained collections cannot create selection ambiguity. Missing or stale state refuses without scanning or fallback. Runner and direct entry points share this boundary, including when generation is disabled. Portable/offline collection reuse uses the explicit manifest and packaged inputs. Metrics-only instead selects the immutable experiment record and cannot switch its collection. | §§5.2, 5.4–5.6, 6.8, 9.5, 11.2; GF-20, GF-22, GF-24, GF-31, GF-32 |
| **3. Identity and stale-result boundaries** | **Pass.** Collection intent, produced artifacts, simulation inputs, response inventory, and metric results retain separate digest checks. `experiment_name` remains a namespace rather than evidence of freshness. Simulation-input changes cannot reuse frozen responses. Metrics-only intentionally uses recorded settings, reports differing current settings as ignored, and validates retained artifacts. | §§5.6–5.7, 6.1–6.2, 6.7–6.8, 8.2–8.4a |
| **4. Internal consistency and actionable failures** | **Pass.** Config ownership, examples, summaries, migration guidance, alternatives, and acceptance gates consistently describe omission-based resolution and optional manifest reuse. Resolution failures name expected paths or mismatches and generation commands; frozen simulations identify the new-experiment/removal remedy. Metrics-only failures identify the retained experiment or unmet response requirement. These mechanisms remain explicitly untested. | §§6.1, 6.4, 6.8, 9.3–9.6, 10, 11.3, 12 |
| **5. Scientific and correctness preservation** | **Pass.** No changed scientific treatment was found. Text comparison confirmed unchanged metric contracts (§7), capacity and collection identities (§§8.1–8.2), seed resolution (§9.4), and numerical migration gate (§12.3). Source and response checkpoints, immutable publication, coverage checks, and preparation portability remain required. Production remains stochastic/Wflow with terminal CMIP plausibility overlays. | §§1–2, 5.2–5.7, 8.4a, 9.4–9.5, 12.1–12.4 |

**New findings:** None. No blocking, major, or minor delta findings.

**Remaining empirical gates:** GF-32 must demonstrate automatic, advanced, and retained metrics-only resolution. Existing obligations remain, including P2b and target/operation feasibility; GF-29/GF-30 checkpoint execution; GF-31 portable preparation; GF-27/GF-28 seed and temporal preservation; GF-9 numerical migration; GF-15’s reviewed estimator benchmark; and §12.4 runtime checks and separate model-validator acceptance. This review establishes none of those outcomes.

**Remaining owner decisions:** Final G2 approval remains pending. The historical Class-B fit-interval deferral (`domain-7`) still requires its separate explicit G2 ruling. The provisional screening policy remains provisional regardless of any future estimator-benchmark pass.