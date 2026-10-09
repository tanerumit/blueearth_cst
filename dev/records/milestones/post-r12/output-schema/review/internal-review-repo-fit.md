---
verdict: revise
doc_version: design-v1.md
findings:
  - id: repo-1
    severity: blocking
    section: "10.1 P0-01/P0-04; 10.3; 10.4"
    finding: "Raw WF0–WF2 Snakemake is allowed with reduced invocation coverage, yet P2 promises exact bytes captured before parsing and a run record for every production archive."
    rationale: "Snakemake parses --configfile before the Snakefile calls compose_config; copy_config_files.py runs later as a rule. A file edit between those reads can leave the captured archive bytes different from the configuration actually executed, including comment-only edits that a parsed-map comparison cannot detect. The proposed raw entry point has no pre-parse capture or immutable --configfile handoff."
    suggested_fix: "Make the byte-capturing launcher mandatory for P2 WF0–WF2 production output, passing immutable captured inputs into Snakemake with original config_path anchoring preserved; or explicitly refuse new-schema archive emission from raw Snakemake. Specify the pre-parse handoff and race test in P1/P2."
  - id: repo-2
    severity: major
    section: "10.1 P0-04/P0-05; 10.4; 10.8; 11 units 3–5"
    finding: "The P3 invocation switch has no runnable WF3 handoff before the P5 planner and launcher exist."
    rationale: "P3 assigns production history and project-wide ownership to run_workflows.py, while scripts/generate_scenarios.py and pinned generation-plan/1 first emit in P5. The current run_workflows.py build_command sends WF3 directly to generate_scenarios.smk, whose two checkpoints still choose work. Under the design's rule that raw WF3 requires a pinned plan and launcher ownership, the P3/P4 all-workflow entry point cannot both run WF3 and satisfy its declared contract."
    suggested_fix: "Define an explicit interim P3/P4 WF3 route and coverage state, or move the WF3 planner/launcher handoff into P3. Require a runnable enabled-WF3 all-workflow smoke at each phase boundary and state when raw WF3 is refused."
---
