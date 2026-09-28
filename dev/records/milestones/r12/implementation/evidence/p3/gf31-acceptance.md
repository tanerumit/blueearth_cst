# P3 GF31 portable preparation acceptance

**ACCEPT — bounded GF31 preservation of the final preparation binding.**
Reviewer: Astra `model-validator` (`/root/model_validator_p3`), 2026-09-12.
This accepts the four named physical fixture comparisons. Full P3 acceptance,
final generation/simulation handoffs and GF15 remain pending.

The coordinator executed [probe-portable-preparation.py](probe-portable-preparation.py)
in fresh `.tmp/scratchpad/2026-09-11_0010/gf31-final-physical2`, completing all
four branches with exit 0. The [comparison record](gf31-preparation-comparison.json)
identifies the immutable fixture collections and prepared old/new files.
The [independent review record](gf31-independent-review.json) binds their hashes,
the probe, source inventory and complete raw log, and records the checks below.

| Source branch | PET path | Independent prepared comparison | Complete parsed TOML |
|---|---|---|---|
| ERA5 | De Bruin | Exact after declared selector relocation | Exact |
| CHIRPS | De Bruin | Exact after declared selector relocation | Exact |
| CHIRPS-global | De Bruin | Exact after declared selector relocation | Exact |
| E-OBS | Makkink | Exact after declared selector relocation | Exact |

Each pair contains 3,287 daily times by 16 latitudes by 24 longitudes, covering
2046-01-01 through 2054-12-31. All values and coordinates match exactly: zero
observed numerical drift. The only excluded attributes are `precip.precip_fn`,
`pet.pet_fn` and `temp.temp_fn`. Each is explicitly required to change from
`forcing` to `run_01`, and each old/new pair is recorded. Every other variable,
coordinate and global attribute matches exactly. These selectors implement the
accepted catalog-key migration; no tolerance or numerical criterion changed.
Complete parsed TOMLs match, including `input.path_forcing`; no TOML exclusion
was actually necessary in these runs.

The reviewer independently reopened all four collections through `read_collection`
with physical forcing and ancillary readers, rechecking retained payload hashes
and descriptors. The original `live` fixture paths are absent in every branch.
For each pair, an in-memory +1 precipitation perturbation preserving attributes
fails the same exact comparison. This demonstrates numerical discrimination.
The final catalog entry is `run_01`. The relevant preparation, simulator adapter,
catalog resolver and descriptor file hashes match
[final-source-inventory.json](final-source-inventory.json).

Verification: release / numerical affected at the migration boundary. The
independent read-only Python command used the existing environment through
`pixi run --as-is python -B`, completed with exit 0 and wrote only the compact
review JSON. It repeated the four array/attribute/TOML comparisons, source-path
absence and collection validation; it ran no Snakemake, preparation, Wflow or
estimator benchmark. The coordinator owns the full software gate and its
missing/changed-ancillary refusal checks. The first failed GF31 root remains
preserved; its failure and exact metadata diagnosis are recorded in
[scientific-review-preparation.md](scientific-review-preparation.md).

This verdict retains the accepted [P2 fixture scope](../p2/portable-preparation.md):
the CHIRPS branches use frozen ERA5 generated values and constant synthetic
elevation, so they establish branch preservation and portable preparation rather
than actual CHIRPS climate equivalence. E-OBS exercises the dormant Makkink path
and does not remove its production limitation. No held-out hydrological skill,
observational accuracy, Wflow-response equivalence or predictive uncertainty
bound is established. Parameter, structural, observational and internal-variability
uncertainties are not quantified by exact migration comparisons.
