# Build the publications

The [manifest](manifest.json) selects canonical sources in reading order.
Edit those sources, this manifest or [format metadata](format.yml); do not edit generated chapters.
The technical manual consumes all six complete sources declared in
[`local-source-appendix.yml`](../technical-manual/local-source-appendix.yml).
No notebook, model or data acquisition runs during publication.

## Full HTML and PDF build

Run from the toolbox root with the locked environment installed:

```powershell
pixi run python dev/scripts/build_publications.py --source-root . --output .tmp/publications/build
New-Item -ItemType Directory -Force docs/site/manuals | Out-Null
Copy-Item .tmp/publications/build/manuals/*.html docs/site/manuals/
Copy-Item .tmp/publications/build/manuals/*.pdf docs/site/manuals/
pixi run docs-build
```

The first command stages the selected chapters and renders the two complete volumes with Quarto HTML
and Typst PDF. After copying the downloads, `pixi run docs-build` renders the navigable website
and retained compatibility routes.
Both explicitly disable computation. Quarto and its Typst engine must already be installed.
Neither command installs packages, starts workflows or acquires external datasets.

For a session borrowing a compatible main runtime, use its helper instead of installing an environment:

```powershell
$runtime = '<stable-toolbox-checkout>'
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime -- python dev/scripts/build_publications.py --source-root . --output .tmp/publications/build
New-Item -ItemType Directory -Force docs/site/manuals | Out-Null
Copy-Item .tmp/publications/build/manuals/*.html docs/site/manuals/
Copy-Item .tmp/publications/build/manuals/*.pdf docs/site/manuals/
& "$runtime/.pixi/envs/default/python.exe" -B dev/scripts/session_runtime.py --runtime-root $runtime -- quarto render docs/site --no-execute
```

Windows Quarto/Sass rendering may require normal user permissions rather than a restricted agent token.
Use the existing runtime; do not change permissions or install another toolchain to mask an access error.
For staging without rendering, add `--stage-only` to the builder command.

## Generated outputs

- `docs/site/guide/`: derived guide chapters and workflow assets.
- `docs/site/technical-manual/`: derived reference chapters and six complete appendices.
- `docs/site/manuals/user-guide.html` and `.pdf`: complete user guide.
- `docs/site/manuals/technical-manual.html` and `.pdf`: complete reference and appendices.
- `docs/site/_site/`: navigable website, retained routes and downloadable volumes after the site build.

The intermediate complete publication tree is `.tmp/publications/build/`.
Its `manuals/` directory contains the volume sources and rendered outputs; copy only HTML/PDF downloads
to the site, not generated Quarto sources or caches.

The generated directories are ignored. Do not commit them or edit their prose independently.
Keep both volumes of your chosen format together for offline reading; the PDFs need no HTML companions.
Links between PDFs may open the volume without jumping to the section, depending on your PDF reader.
Use the contents if needed.
The workflow diagram's static SVG and all five descriptions come from the same interactive asset.
Required inputs must exist; a successful smaller publication is not an acceptable missing-source fallback.

## Source identity and external material

`source-hashes.json` records consumed input hashes; retain it with review artifacts.
The manifest's source label describes a local candidate based on its recorded checkout revision.
Its repository URL is a locator for external source evidence, not proof that an unpushed candidate
exists online. Network availability is not verified by rendering.

Only the selected guide/manual chapters and module/set sources are included in the complete volumes.
Other linked repository evidence, configuration files, optional notebooks and upstream references require
a separate checkout or network access. Existing scientific pages remain available on the website;
this publication does not claim a completed new scientific-approach volume or a supported
response-surface construction tutorial.

The retained [P3 pilot](../publishing-pilot/README.md) remains a separate review fixture.
Full publication assembly does not replace its source or retained review evidence.
