# Documentation guidelines

These guidelines apply to new and revised BlueEarth CST documentation.

## Write for the reader

- Write the user guide for water resources, hydrology, and climate-risk
  specialists. Use domain terms such as *forcing*, *natural variability*,
  *response surface*, and *return level* where they carry useful meaning.
  Explain a term briefly when its meaning in this toolbox may be unclear.
- Use plain language for software operations. Tell readers what to choose, what
  command to run, where to find the result, and how to check it. Introduce file
  names and configuration keys when the reader needs them to act.
- State the intended use and limits of an output. Distinguish a screening
  indicator from a design estimate, and a climate-projection plausibility
  comparison from a stress-test input. Avoid claiming that the toolbox makes a
  decision or validates a model when it only supplies evidence to assess.

## Put information in the right place

- `docs/index.qmd` introduces the assessment approach and directs readers to
  tasks. `docs/guide/` explains setup choices, running workflows, and
  interpreting outputs. Keep each page focused on a reader's task and link to
  detail instead of repeating it.
- `docs/` holds user-facing instructions and references. Put implementation
  rationale, review history, milestone status, test evidence, and maintainer
  procedures under `dev/`. Do not place development commentary in the user
  guide.
- `config/templates/` is the source for configuration examples users copy;
  `config/defaults/` contains settings read by runs. Refer to these files rather
  than maintaining a second, divergent configuration specification in prose.

## Keep instructions current

- Check workflow order, prerequisites, commands, config keys, and output paths
  against the current runners, example project files, and output contracts.
  The five workflows are separate: historical climate, model build, projections,
  scenario generation, and simulation. Projections provide context; they do not
  drive scenario generation.
- Use examples that a reader can adapt. State external data-access requirements
  and important limits of the example. Mark placeholders clearly and never
  present a machine-specific path as generally available.
- When behavior or a path changes, update every live user-facing reference in
  the same task. Keep historical migration records as records rather than
  silently rewriting their past instructions.

## Check a revision

Read the page as a practitioner following its links and commands. Confirm that
local links resolve and that the page renders with `pixi run docs-build`; use
`pixi run docs-preview` for visual review. If rendering is blocked by the
environment, report the error and perform the remaining text, link, and command
checks. Do not claim a rendered page was reviewed when it was not.
