---
title: Snakemake's six-line preamble is not suppressible from inside a workflow
type: watch-item
area: console / snakemake
origin: console polishing (2026-09-18)
created: 2026-09-18
updated: 2026-09-18
---

> [!note] Overview
> **What** — Six lines open every workflow -- Using workflow specific profile / Assuming unrestricted shared filesystem usage / host: / Building DAG of jobs... / Provided cores: N / Rules claiming more threads. Thirty per pipeline run, none of them ours.
> **Why** — Measured 2026-09-18 on an isolated probe: --quiet host has NO effect; --quiet progress removes two of the six but takes the plan block and every DONE row with them; --quiet rules degrades job rows to 'Finished jobid: 0'; --quiet all removes all six and guts our console entirely, because quiet filters at the RECORD level before handlers; installing the handler at parse time changes nothing and additionally restores Snakemake's raw Job stats table. The only remaining route is a --logger plugin, which is early enough but requires a new dependency (the plugin set is empty).
> **Trigger** — Revisit if a snakemake logger plugin is added for another reason, or if upstream makes the preamble filterable.
