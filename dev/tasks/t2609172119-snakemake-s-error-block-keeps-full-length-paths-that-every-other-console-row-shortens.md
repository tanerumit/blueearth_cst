---
title: Snakemake's error block keeps full-length paths that every other console row shortens
type: todo-item
status: backlog
effort: 1
area: console / path tokens
origin: wf1 failure-transcript render, 2026-09-17
queue:
created: 2026-09-17
updated: 2026-09-17
---

> [!note] Overview
> **What** — A path token only ever matches an ABSOLUTE path, because
> `declare_path_tokens` absolutizes what it is handed. Snakemake's error block
> prints paths in the relative spelling the Snakefile declared, so none of them
> shorten — in the one block where a reader most needs a short path.
> **Why it matters** — On a failed run the error block is what the reader acts
> on, and it is the only console region still printing twelve path components
> while the rows above it print `<model>/staticmaps.nc`. One console, one
> spelling of a path, is the standing rule (`AGENTS.md`, `_relativize_paths`).
> **Effort** — small; the mechanism is understood and the fix is a few lines.

## Measured 2026-09-17 on `24fd73e0`

The handler does relativize the block — ERROR records are not muted, so they
reach `_relativize_paths(self.format(record), "", _path_tokens())`
(`console_style.py:1343`). The tokens simply cannot match:

```python
su.declare_path_tokens(model="test_case/test_rapid/hydrology_model")
su._path_tokens()
# (('model', 'C:\\Users\\...\\session-3\\test_case\\test_rapid\\hydrology_model'),)

su._relativize_paths("    log: test_case/test_rapid/hydrology_model/run_default/output.csv",
                     "", su._path_tokens())
# '    log: test_case/test_rapid/hydrology_model/run_default/output.csv'   <- unchanged
```

Every workflow declares its tokens from `project_dir`, and `project_dir` is
relative in both shipped configs (`test_case/test_rapid`, `test_case/test_local`).
So this is the DEFAULT path, not an edge case. With an absolute `project_dir` —
a production project, which lives outside the repo tree — the same block
shortens correctly, which is why nobody has seen it.

What it looks like in the wf1 failure transcript
(`dev/scripts/render_console_sample.py`, `wf1.failed.txt`):

```text
Error in rule run_wflow:
    jobid: 1
    input: test_case/test_rapid/hydrology_model/wflow_sbm.toml
    output: test_case/test_rapid/hydrology_model/run_default/output.csv
    log: test_case/test_rapid/logs/_parts/1.14_run_wflow.log (check log file(s) ...)
```

against the rows a few lines above it, in the same run:

```text
09:19:09 - tables - Wrote 4 table(s) -> <model>/run_default
```

## Why it survived

Nothing rendered a failure until 2026-09-17. `run_summary(failed=True)` has
existed the whole time and the sample renderer could only produce the clean
shape, so the block was never read side by side with the rows it disagrees
with. The failure spec added in `7be73500` is what surfaced it.

## Options

1. **Match tokens against both spellings.** Keep the absolutized token for what
   rules print, and also try the declared form. Cheapest, and it fixes the
   general case of any caller printing a project-relative path — `log_row`
   callers can do this too, not only Snakemake.
2. **Absolutize the text before matching**, in `_relativize_paths`. Wrong shape:
   it would have to guess which whitespace-delimited fragments are paths, and
   resolving a fragment that only looks like a path is how a log line gets
   rewritten into something that was never on disk.
3. **Declare tokens relative as well as absolute** — i.e. store a pair. Same
   effect as 1 with a wider blast radius, since `_path_tokens` is read by
   `target_banner` and the run header too.

Option 1, with a test that asserts an error block's paths shorten under a
relative `project_dir`. Note the docstring of `_relativize_paths` currently
states the absolute-only rule as a deliberate design ("a token registered in
absolute form — which is the only form that can match what a rule prints"); it
is right about what a RULE prints and wrong about Snakemake's own block, so the
paragraph needs correcting in the same change rather than left to contradict
the new behaviour.

## Progress

- [ ] Decide between option 1 and 3 (option 1 recommended).
- [ ] Fix, with a test rendering an error block under a relative `project_dir`.
- [ ] Correct the `_relativize_paths` docstring paragraph about absolute form.
- [ ] Re-render `wf1.failed.txt` and confirm the block shortens.

## Related

- [[t2609171637a]] — the other console-column defect found in the same pass.
- `dev/scripts/render_console_sample.py` — renders the transcript that shows it;
  WF1 is the only workflow with a `Failure` spec so far.
