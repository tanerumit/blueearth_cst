---
title: "Use the workflow notebooks"
subtitle: "Optional interactive walkthroughs and their current limits"
---

The [notebook index](../notebooks/README.md) links model building, projection analysis and stress-test
walkthroughs. The `.ipynb` files are their sole editable sources; figures and execution output are not
committed. No rendered result or input dataset is supplied by an empty notebook.

## Choose a route

- Use the [quick start](quick-start.md) for the maintained command-line example.
- Use [outputs](outputs.md) to read tables without executing a notebook.
- Use a notebook only when you want to inspect or adapt its code interactively.
  Its cells execute real workflows and need installed tools, external data and compute/storage capacity.

The notebooks contain code and paths that have not been updated to every current interface.
Read their opening status note before running cells. Treat them as advanced source walkthroughs,
not verified current end-to-end examples. In particular, a supported response-surface construction
walkthrough is deferred; the current documentation promise ends at table interpretation and extension.

## Open a notebook

1. Complete [installation and data checks](install.md).
2. Start the kernel from the same toolbox checkout used for your project:

   ```powershell
   pixi run jupyter lab docs/notebooks
   ```

3. Inspect its configuration reads, commands and output paths before executing cells.
   Keep scientific outputs outside the checkout for your own assessment.
   Use the [owned runners](running.md) for WF3/WF4; do not translate notebook code into bare Snakemake calls.
4. Distinguish execution from interpretation. Source agreement, a completed run or an attractive plot
   does not establish model skill or assessment adequacy.

The [local notebook guide](../notebooks/README.md) explains source-only handling.
Rendering the documentation does not execute these notebooks.
