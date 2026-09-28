"""Demonstrate that the boundary checker rejects an actual half-P90 mutant."""

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    assert output.is_relative_to(Path.cwd().resolve())
    output.mkdir(parents=True, exist_ok=False)
    for name in ("check-rescore.py", "criteria.json"):
        (output / name).write_bytes((source / name).read_bytes())
    text = (source / "rescore.py").read_text(encoding="utf-8")
    needle = '- summary["p90_absolute"]'
    assert text.count(needle) == 1
    (output / "rescore.py").write_text(
        text.replace(needle, '- 0.5 * summary["p90_absolute"]'), encoding="utf-8"
    )
    result = subprocess.run(
        [sys.executable, "-B", str(output / "check-rescore.py")],
        capture_output=True,
        text=True,
        check=False,
    )
    print(result.stdout + result.stderr)
    assert result.returncode != 0 and "AssertionError" in result.stderr
    print(f"PASS: actual half-P90 reducer mutation rejected (exit {result.returncode})")


if __name__ == "__main__":
    main()
