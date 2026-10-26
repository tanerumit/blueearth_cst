# Documentation

Choose the task you want to complete:

- [Install](guide/install.md), then [run the example](guide/quick-start.md).
- [Create your own case](guide/new-case.md) and [choose settings](guide/configuration.md).
- [Run/resume](guide/running.md), [choose indicators](guide/indicators.md) and [read tables](guide/outputs.md).
- [Read timings](guide/benchmarking.md), [diagnose a failure](guide/troubleshooting.md), or
  [use optional notebooks](guide/notebooks.md).
- [Technical manual](technical-manual/overview.md): implemented interfaces and advanced extension.
- [Scientific approach](site/scientific-approach/overview.qmd): existing methodological context and limits.

Canonical guide Markdown is in `guide/`; its asset sources remain in `guide/assets/`.
The technical manual and local component READMEs own reference detail.
The site configuration selects published sources and stages derived guide copies; edit canonical sources,
never those generated copies. Repository source compatibility pages remain at existing setup/reference routes.

The accepted publication pilot demonstrates shared-source HTML/PDF handling; whole-manual assembly is a
separate integration step. The new source chapters here do not imply that every route is already published.
Use the [site configuration](site/_quarto.yml) to inspect the current render list.
`pixi run docs-build` and `pixi run docs-preview` operate that configured site, not arbitrary repository files.

Notebooks remain editable `.ipynb` sources and are not executed by documentation rendering.
[Upstream references](references/) are repository-only consultation material; the 2025 note describes
the earlier platform, not the current workflow contract. No supported response-surface construction
walkthrough or completed new scientific-approach volume is claimed by this tranche.
