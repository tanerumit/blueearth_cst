"""Record the config an artifact-scoped workflow ran under, beside the artifact.

WF0-WF2 are singletons per project, so each writes one overwritable record
under ``config/runs/<workflow>/``. WF3 and WF4 are not: a project holds one
directory per scenario collection and one per experiment, so a single
``config/runs/<workflow>/`` slot would be claimed by whichever ran last and
would describe the others wrongly. Their snapshot therefore lives INSIDE the
identified directory, which is the only placement that stays true when a
second collection is generated.

**The snapshot is UNREFERENCED on purpose.** ``simulation_id`` and
``collection_id`` hash digests and never path strings, and neither
``simulation.json`` nor ``collection.json`` carries a directory listing -- so a
file the identity documents do not name changes no identity and invalidates no
retained metric set. Recording these fields INSIDE ``collection_intent.json``
or ``simulation.json`` would have been the tidier shape, and would have
rewritten every existing experiment's identity to buy provenance. It would also
fail closed rather than silently: ``read_simulation`` compares the record's key
set against an exact expected set and raises on any extra field.

What it closes, none of which the digest documents carried:

* **which SOURCE file the settings came from**, and whether it has changed
  since. The collection records the resolved VALUES -- which is the stronger
  fact for reproducing numbers -- but nothing anywhere in the scenario or
  experiment trees named the file they were resolved from, so the audit
  question "is this still the config that produced it?" had no answer;
* **``operation:``**, a WF4 config key that reached no record at all;
* a view in the same vocabulary and format as the source config, rather than
  settings split across two JSON provenance documents in a different one.

It is a RECORD, not a re-run button. The collection also depends on the staged
forcing and the generator template, which ``source_inventory.json`` pins by
sha256 and this file does not carry -- the same limit the WF1 snapshot has.
"""

from pathlib import Path
from typing import Any, Mapping, Union

import yaml

from blueearth_cst.shared.provenance import file_sha256

SCHEMA_VERSION = 1

#: The snapshot's filename, in every bin that holds one. Deliberately the same
#: name WF0-WF2 use under ``config/runs/<workflow>/``: a reader who has learned
#: one has learned all five, and the directory already says which workflow and
#: which artifact it belongs to. Spelling the workflow into the name as well
#: would restate the directory and stutter in the per-workflow bins.
SNAPSHOT_NAME = "composed_config.yml"

#: Header planted at the top of every snapshot. ``yaml.safe_dump`` drops
#: comments from the document, so a reader who opens this file without having
#: read the bin's README would have no way to tell a record from a source they
#: may edit -- which is exactly the mistake the two-tier config split exists to
#: prevent.
_HEADER = (
    "# Written by the run. Editing this file changes nothing: the next\n"
    "# execution of this workflow overwrites it, and a retained collection or\n"
    "# experiment is immutable. To change what a run does, edit the config you\n"
    "# pass to --configfile and run the workflow again.\n"
)


def snapshot_document(
    workflow: str,
    source_config_path: Union[str, Path],
    workflow_config_path: Union[str, Path, None],
    composed_config: Mapping[str, Any],
) -> dict:
    """Assemble the snapshot for one artifact-scoped workflow run.

    Parameters
    ----------
    workflow
        The workflow key, as it appears under ``workflows:``.
    source_config_path
        The project file the user passed to ``--configfile``. Hashed as
        invoked, so the record names the file a reader would go back to.
    workflow_config_path
        That workflow's own settings file, as ``compose_config`` resolved it.
        ``None`` when the project declared no ``config_path`` for it, which is
        legal and must not be mistaken for a missing record.
    composed_config
        The composed config the workflow is running under -- the WHOLE
        composed mapping, not a projection of it. That is what the WF0-WF2
        snapshots hold, and the point of this file is that a reader who has
        learned one snapshot has learned all five. A projection belongs to a
        DIGEST, whose job is to not move when another workflow's section
        changes; this is a record, whose job is to say what ran.
    """
    source_path = Path(source_config_path)
    document: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "workflow": workflow,
        "source_config": {
            "path": str(source_path),
            "sha256": file_sha256(source_path),
        },
    }
    if workflow_config_path is None:
        # Recorded as an explicit null rather than an absent key: "this project
        # declared no settings file for this workflow" and "this record predates
        # the field" must not read the same way.
        document["workflow_config"] = None
    else:
        workflow_path = Path(workflow_config_path)
        document["workflow_config"] = {
            "path": str(workflow_path),
            "sha256": file_sha256(workflow_path),
        }
    document["effective_config"] = dict(composed_config)
    return document


def render_snapshot(document: Mapping[str, Any]) -> str:
    """Render the snapshot as the bytes written into the artifact directory.

    ``sort_keys=True`` for the same reason the WF0-WF2 snapshots use it: two
    runs of the same configuration must produce the same bytes, or a byte
    comparison between two projects reports a difference that is only key order.
    """
    return _HEADER + yaml.safe_dump(dict(document), sort_keys=True)


def snapshot_bytes(
    workflow: str,
    source_config_path: Union[str, Path],
    workflow_config_path: Union[str, Path, None],
    composed_config: Mapping[str, Any],
) -> bytes:
    """Build and render in one step, for a caller that writes bytes.

    WF3 writes its snapshot through ``write_collection_payload``, which takes
    bytes and refuses to write at all once the collection is sealed -- so the
    snapshot has to be a value the caller can hand over, not a path this module
    writes to itself.
    """
    document = snapshot_document(
        workflow,
        source_config_path,
        workflow_config_path,
        composed_config,
    )
    return render_snapshot(document).encode("utf-8")


def composed_workflow_section(
    project: Mapping[str, Any], workflow: str, settings: Mapping[str, Any]
) -> dict:
    """Rebuild ``compose_config``'s shape for an entry point that does not use it.

    WF4 reads the project file and its own settings file directly
    (``simulation_settings``), so there is no composed mapping to snapshot. This
    reproduces the one ``compose_config`` would have produced: ``config_path``
    dropped from every stanza -- it is a pointer to a file, not a setting, and
    the composed document has already followed it -- and this workflow's
    settings merged into its own stanza beside ``enabled``.

    Without this the WF4 snapshot would be a different shape from the other
    four, and the promise that one snapshot teaches you all five would be false
    exactly where a reader is least able to check it.
    """
    stanzas = {
        name: {
            key: value for key, value in dict(stanza).items() if key != "config_path"
        }
        for name, stanza in dict(project.get("workflows") or {}).items()
    }
    stanzas.setdefault(workflow, {}).update(dict(settings))
    composed = {key: value for key, value in project.items() if key != "workflows"}
    composed["workflows"] = stanzas
    return composed


def write_snapshot(
    directory: Union[str, Path],
    workflow: str,
    source_config_path: Union[str, Path],
    workflow_config_path: Union[str, Path, None],
    composed_config: Mapping[str, Any],
) -> Path:
    """Write the snapshot into ``directory`` and return the path written."""
    target = Path(directory) / SNAPSHOT_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(
        snapshot_bytes(
            workflow,
            source_config_path,
            workflow_config_path,
            composed_config,
        )
    )
    return target
