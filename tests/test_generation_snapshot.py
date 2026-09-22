"""WF3 consumes a content pin instead of a mutable external source path."""

import hashlib
import os

import pytest

from blueearth_cst.experiment.generation_plan import snapshot_generation_input


def test_snapshot_is_independent_of_live_source_and_refuses_changed_bytes(tmp_path):
    source = tmp_path / "external" / "extract_historical.nc"
    source.parent.mkdir()
    source.write_bytes(b"first")
    project = tmp_path / "project"
    pinned, digest, size = snapshot_generation_input(project, source)
    assert (digest, size) == (hashlib.sha256(b"first").hexdigest(), 5)
    assert pinned.read_bytes() == b"first"
    stat = source.stat()
    source.write_bytes(b"later")
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    assert pinned.read_bytes() == b"first"
    assert snapshot_generation_input(project, source)[0] != pinned
    assert pinned.read_bytes() == b"first"
    pinned.chmod(0o666)
    pinned.write_bytes(b"wrong")
    source.write_bytes(b"first")
    os.utime(source, ns=(stat.st_atime_ns, stat.st_mtime_ns))
    with pytest.raises(ValueError, match="snapshot bytes differ"):
        snapshot_generation_input(project, source.parent / source.name)
