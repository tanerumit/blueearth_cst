# A v1 config SET, in the R13 split shape, kept so migration stays testable

`tests/data/presplit/` holds PRE-R13 configs: one whole document, workflows
inline. That was the input to R13's splitter, which P1 retired.

This directory holds the *other* v1 shape — the R13 SPLIT form, a project file
carrying `{enabled, config_path}` stanzas plus one file per workflow — which is
what R14's rewriter migrates. The two are not interchangeable, and the
migration tests need this one.

It is a byte-for-byte copy of `test_case/snake_config_rapid*.yml` as they stood
at R14 P4 commit 1, immediately before the rewriter ran on them. Taken from the
`*.v1.bak` files the migration itself left behind, so it is the real input and
not a reconstruction.

**Do not migrate these.** They exist to be v1. The stale-spelling sweep
allowlists this directory for the same reason it allowlists `presplit/`.
