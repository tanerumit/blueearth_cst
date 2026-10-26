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

The [publication manifest](publication/manifest.json) selects the ten user-guide chapters, sixteen
technical-manual chapters and six complete local module/set sources for shared HTML/PDF assembly.
See [Build the publications](publication/README.md) for exact commands and output locations.
The [site configuration](site/_quarto.yml) owns navigation and retained routes.
Build the complete manuals before rendering the site so its downloads are available.

Notebooks remain editable `.ipynb` sources and are not executed by documentation rendering.
[Upstream references](references/) are repository-only consultation material; the 2025 note describes
the earlier platform, not the current workflow contract. No supported response-surface construction
walkthrough or completed new scientific-approach volume is claimed by this tranche.
