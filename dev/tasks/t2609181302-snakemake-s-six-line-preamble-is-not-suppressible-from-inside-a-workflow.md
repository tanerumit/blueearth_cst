---
title: "Snakemake preamble cannot be suppressed"
type: todo-item
status: backlog
effort: 1
area: console
origin: console polishing (2026-09-18)
queue: 10
created: 2026-09-18
updated: 2026-10-05
---

> [!note] Overview
> **What changes** — Six lines open every workflow -- Using workflow specific profile / Assuming unrestricted shared filesystem usage / host: / Building DAG of jobs... / Provided cores: N / Rules claiming more threads. Thirty per pipeline run, none of them ours.
> **Why it matters** — Measured 2026-09-18 on an isolated probe: --quiet host has NO effect; --quiet progress removes two of the six but takes the plan block and every DONE row with them; --quiet rules degrades job rows to 'Finished jobid: 0'; --quiet all removes all six and guts our console entirely, because quiet filters at the RECORD level before handlers; installing the handler at parse time changes nothing and additionally restores Snakemake's raw Job stats table. The only remaining route is a --logger plugin, which is early enough but requires a new dependency (the plugin set is empty).
> **What it takes** — Nothing for now. Revisit if a snakemake logger plugin gets added for another reason, or if snakemake makes the preamble filterable.

## Progress

- [ ] Check whether the condition in What it takes has happened
