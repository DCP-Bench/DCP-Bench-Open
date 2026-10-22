#!/usr/bin/env python3
"""Run every example in a skill's assets/ and check its output. Standard library only.

Usage: check_assets.py SKILL_FOLDER [--timeout 120]

Each example is a folder assets/<example>/ with a README.md containing:

    **Run:** `python model.py`
    **Expected:** `Objective: 70`        (optional, may repeat; each must appear in stdout)

The Run command is executed with a shell inside the example folder. An example
passes when the command exits 0 and every Expected string occurs in its stdout.
Prints one line per example and a summary; exit code 0 only if all passed.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

RUN = re.compile(r"\*\*Run:\*\*\s*`([^`]+)`")
EXPECTED = re.compile(r"\*\*Expected:\*\*\s*`([^`]+)`")


def check(example, timeout):
    """Return (passed, reason) for one example folder."""
    readme = example / "README.md"
    if not readme.exists():
        return False, "no README.md"
    text = readme.read_text()
    run = RUN.search(text)
    if not run:
        return False, "README.md has no **Run:** `command` line"
    try:
        proc = subprocess.run(run.group(1), shell=True, cwd=example, capture_output=True,
                              text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return False, f"timeout after {timeout:g}s"
    if proc.returncode != 0:
        tail = (proc.stderr.strip().splitlines() or ["(no stderr)"])[-1]
        return False, f"exit code {proc.returncode}: {tail[:160]}"
    missing = [e for e in EXPECTED.findall(text) if e not in proc.stdout]
    if missing:
        return False, f"expected output not found: {missing[0]!r}"
    return True, run.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--timeout", type=float, default=120, help="seconds per example")
    args = parser.parse_args()

    assets = args.skill / "assets"
    examples = sorted(p for p in assets.iterdir() if p.is_dir()) if assets.is_dir() else []
    if not examples:
        sys.exit(f"no example folders in {assets}")
    results = []
    for example in examples:
        passed, reason = check(example, args.timeout)
        results.append(passed)
        print(f"{'PASS' if passed else 'FAIL'}  {example.name}: {reason}", flush=True)
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
