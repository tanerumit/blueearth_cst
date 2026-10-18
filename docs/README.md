# Documentation map

The [Quarto site](site/index.qmd) publishes the current user guide, setup
instructions, scientific approach, and toolbox reference. Its render list is
explicit in [`site/_quarto.yml`](site/_quarto.yml); other documents remain in
the repository.

The canonical user guides live in [`guide/`](guide/), independently of the site:
[Quick start](guide/quick-start.md), [Configuration](guide/configuration.md),
[Running](guide/running.md), and [Outputs](guide/outputs.md). Open and edit these
Markdown files directly. The diagram asset lives beside them in `guide/assets/`.

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
| [`site/`](site/) | Published Quarto site: landing page, user guide, setup, scientific approach, toolbox reference, styles, and assets. |
| [`notebooks/`](notebooks/) | Executable walkthroughs, kept source-only in Git. Repository-only. |
| [`references/`](references/) | Offline upstream guides and the dated 2025 toolbox note. Repository-only. |

For current commands and file layouts, use the guide and toolbox reference.
The external guides describe their own tools; the 2025 note records the original
method and platform design rather than the current workflow contract.
Historical migration guides live with their relevant milestone records under
[`dev/records/milestones/`](../dev/records/milestones/); the v1 -> v2 project-config
migrator and its guide ship in release `v0.3.0`, the last that carries them.
