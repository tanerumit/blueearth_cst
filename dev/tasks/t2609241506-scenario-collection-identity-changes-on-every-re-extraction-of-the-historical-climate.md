---
title: Scenario collection identity changes on every re-extraction of the historical climate
type: todo-item
status: backlog
effort: 1
area: wf3
origin: wf3 identity bundle (2026-09-24)
branch: wf3-improvements
queue:
created: 2026-09-24
updated: 2026-09-24
---

> [!note] Overview
> **What** — The WF3 source inventory hashes the extracted historical-climate netCDF by file bytes. HDF5 stamps write times into object headers (70 bytes differ between two extractions with identical values and attributes, measured 2026-09-24), so every fresh extraction yields a new collection id, and with seed: auto a new seed. Option: hash a canonical content digest (values + attributes) for netCDF sources instead of bytes -- an identity-contract change.
> **Why** — Identical inputs should resolve to the same collection so reuse works across projects and re-extractions; the checkout and region_source parts were fixed in 3c80542c.
> **Effort** — small

## Progress

- [ ] <first step>
