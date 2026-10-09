"""Exercise the repository temporary-directory policy through real fixtures."""

from pathlib import Path

import pytest


def test_temporary_directories_are_local_writable_and_isolated(
    tmp_path_factory, tmp_path, tmpdir, pytestconfig
):
    root = Path(__file__).resolve().parents[1]
    base = tmp_path_factory.getbasetemp()
    explicit = pytestconfig.getoption("basetemp")
    if explicit is None:
        assert base.is_relative_to(root / ".tmp" / "pytest")
    else:
        assert base == Path(explicit).resolve()
    first = tmp_path_factory.mktemp("same")
    second = tmp_path_factory.mktemp("same")
    assert first != second
    for directory in (
        first,
        second,
        tmp_path_factory.mktemp("plain", numbered=False),
        tmp_path,
        Path(str(tmpdir)),
    ):
        target = directory / "probe.txt"
        target.write_text("writable", encoding="utf-8")
        assert target.read_text(encoding="utf-8") == "writable"
    with pytest.raises(ValueError):
        tmp_path_factory.mktemp("../escape")
