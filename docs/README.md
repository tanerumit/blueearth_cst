# Documentation map

The [Quarto site](site/index.qmd) publishes the current user guide, setup
instructions, scientific approach, and toolbox reference. Its render list is
explicit in [`site/_quarto.yml`](site/_quarto.yml); other documents remain in
the repository.

| Location | Purpose |
|---|---|
| [`site/`](site/) | Published Quarto site: landing page, user guide, setup, scientific approach, toolbox reference, styles, and assets. |
| [`notebooks/`](notebooks/) | Executable walkthroughs, kept source-only in Git. Repository-only. |
| [`references/`](references/) | Offline upstream guides and the dated 2025 toolbox note. Repository-only. |

For current commands and file layouts, use the guide and toolbox reference.
The external guides describe their own tools; the 2025 note records the original
method and platform design rather than the current workflow contract.
Historical migration guides live with their relevant milestone records under
[`dev/records/milestones/`](../dev/records/milestones/); the v1 -> v2 project-config
migrator and its guide ship in release `v0.3.0`, the last that carries them.
