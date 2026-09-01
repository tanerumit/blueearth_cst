---
title: Land C-36 - move the six config-key defaults out of Python
type: todo-item
status: backlog
effort: 1
area: config / defaults
origin: R14 closure
queue: 2
created: 2026-09-01
updated: 2026-09-01
---

> [!note] Overview
> **What** — `C-36`: move six config-key defaults out of Python into
> `advanced_settings.defaults` — `DEFAULT_SPELL_FACTOR`,
> `DEFAULT_MAX_SUBBASINS_PER_BASIN`, `DEFAULT_GAUGE_SNAP_TOLERANCE_M`,
> `DEFAULT_HYDROGRAPHY`, `DEFAULT_BASIN_INDEX`, `DEFAULT_STATS`. The keys stay
> where they are; only the DEFAULTS move. `advanced_settings.yml` and the closed
> `_ADVANCED_SETTINGS_SCHEMA` must change in one commit.
> **Why** — An R14 register row that was UNBLOCKED and then landed by nobody.
> `Q-E` ruled its destination on 2026-08-24 (owner: `advanced_settings.yml`, by
> authority and scope), and `D-11.4` says everything except `C-37` and `C-83`
> lands in the one bundle — so `C-36` was inside it. No phase brief's table
> names it, and Gate 5 did not check the register row-by-row.
> **Effort** — small; `C-36`'s own register row calls it "5 schema entries +
> tests; non-breaking".

## Measured 2026-09-01, at `06c32fc0`

All six still live in Python:

| constant | file |
|---|---|
| `DEFAULT_HYDROGRAPHY`, `DEFAULT_BASIN_INDEX` | `shared/snake_utils.py:1520-1521` |
| `DEFAULT_SPELL_FACTOR` | `shared/snake_utils.py:2151` |
| `DEFAULT_MAX_SUBBASINS_PER_BASIN`, `DEFAULT_GAUGE_SNAP_TOLERANCE_M` | `spatial/config.py:21,25` |
| `DEFAULT_STATS` | `projections/get_change_climate_proj.py:118` |

`advanced_settings.defaults` holds `batch_disk_headroom_fraction`, `seed` and
`water_year_start` — none of the six — and `_ADVANCED_SETTINGS_SCHEMA` agrees,
which is the check that makes this unambiguous rather than a grep result.

## Why it is worth landing rather than withdrawing

It is the whole of `parameter-placement.md`'s **M3**, and M3 is one instance of
that document's **P1**: a parameter's default and its key live in different
tiers, decided by whichever session added it, so a user reading the config
cannot discover what a key defaults to. R14 answered the QUESTION (`Q-E`) and
left the instance unmoved, which is the least useful of the three possible
outcomes — the convention now exists and this is the code that does not follow
it.

Withdrawing it is a legitimate alternative, but it needs the same owner ruling
`Q-E` was, because it reverses one.

## Progress

- [ ] Confirm with the owner: land, or withdraw the row now that R14 has closed
- [ ] `advanced_settings.yml` + `_ADVANCED_SETTINGS_SCHEMA` in ONE commit
- [ ] Each reader falls back to the advanced setting, not to a Python literal

## Links

- `dev/milestones/r14/config-shape-scoping.md:1855` — the `C-36` register row
- `dev/milestones/r14/config-shape-scoping.md:2238` — `Q-E`, the owner ruling
- `dev/milestones/r14/config-shape-design.md:497` — the destination table
- `dev/working/parameter-placement.md` §6 M3 — where the row came from (sealed)
