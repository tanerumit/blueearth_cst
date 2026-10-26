# Documentation

Start with the [installation guide](site/setup/install.md) for Windows setup, then
use the [quick start](guide/quick-start.md) to run the supplied basin. For your own
assessment, follow [configuration](guide/configuration.md),
[running](guide/running.md), and [outputs](guide/outputs.md). The
[site home](site/index.qmd) also links the scientific approach and toolbox reference.

The canonical user guides live in [`guide/`](guide/), independently of the site.
Open and edit those Markdown files directly. The diagram asset lives in
`guide/assets/`. The [Quarto render list](site/_quarto.yml) selects published
pages; notebooks and offline references remain in the repository.

Run `pixi run docs-preview` for a local preview or `pixi run docs-build` to build
the site. Quarto's pre-render hook stages ignored copies under `site/guide/` and
adjusts links to the site layout. Edit only the canonical files; the site copies
are overwritten on each render. After editing a canonical guide outside the site
tree, restart preview or run the build to refresh it. Published guide URLs stay
the same. Quarto callouts and the embedded diagram retain their site formatting;
their appearance in other Markdown previews depends on the editor.

| Location | Purpose |
|---|---|
| [`guide/`](guide/) | Canonical Markdown user guides and their assets; readable without building the site. |
| [`site/`](site/) | Published Quarto site and its assets. |
| [`notebooks/`](notebooks/) | Executable walkthroughs, kept source-only in Git. Repository-only. |
| [`references/`](references/) | Offline upstream guides and the dated 2025 toolbox note. Repository-only. |

For current commands and file layouts, use the guide and
[toolbox reference](site/toolbox-reference/overview.qmd).
The external guides describe their own tools; the 2025 note records the original
method and platform design rather than the current workflow contract.
