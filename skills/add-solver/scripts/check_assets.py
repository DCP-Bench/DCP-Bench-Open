#!/usr/bin/env python3
"""Run every example in a skill's assets/ and check its output. Standard library only.

Usage: check_assets.py SKILL_FOLDER [--timeout 120]
       check_assets.py SKILL_FOLDER --image IMAGE [--env K=V ...] [--mount SRC:DST[:ro] ...] [--network none]

Each example is a folder assets/<example>/ with a README.md containing:

    **Run:** `python model.py`
    **Expected:** `Objective: 70`        (optional, may repeat; each must appear in stdout)

The examples run from a temporary copy of the skill, so compiled binaries and caches
never land in the skill folder. The Run command is executed with a shell inside the
example folder: on this machine by default, or with --image inside a fresh container
of that image, as the current user, with no network unless --network says otherwise
(the copy is mounted at /skill). Run is what a user types on their own machine, so an
image that needs a binary on PATH or an environment variable gets it with --env.
An example passes when the command exits 0 and every Expected string occurs in its
stdout. Prints one line per example and a summary; exit code 0 only if all passed.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

RUN = re.compile(r"\*\*Run:\*\*\s*`([^`]+)`")
EXPECTED = re.compile(r"\*\*Expected:\*\*\s*`([^`]+)`")


def command(example, run, args, skill_copy):
    """The process to start for one example: the Run line itself, or a container running it."""
    if not args.image:
        return run, example
    inside = "/skill/" + example.relative_to(skill_copy).as_posix()
    docker = ["docker", "run", "--rm", "--network", args.network, "-e", "HOME=/tmp",
              "-v", f"{skill_copy}:/skill", "-w", inside, "--entrypoint", "sh"]
    if hasattr(os, "getuid"):
        docker += ["--user", f"{os.getuid()}:{os.getgid()}"]
    for pair in args.env:
        docker += ["-e", pair]
    for mount in args.mount:
        docker += ["-v", mount]
    return docker + [args.image, "-c", run], None


def check(example, args, skill_copy):
    """Return (passed, reason) for one example folder."""
    readme = example / "README.md"
    if not readme.exists():
        return False, "no README.md"
    text = readme.read_text()
    run = RUN.search(text)
    if not run:
        return False, "README.md has no **Run:** `command` line"
    process, cwd = command(example, run.group(1), args, skill_copy)
    try:
        proc = subprocess.run(process, shell=isinstance(process, str), cwd=cwd, capture_output=True,
                              text=True, timeout=args.timeout)
    except subprocess.TimeoutExpired:
        return False, f"timeout after {args.timeout:g}s"
    if proc.returncode != 0:
        tail = (proc.stderr.strip().splitlines() or proc.stdout.strip().splitlines() or ["(no output)"])[-1]
        return False, f"exit code {proc.returncode}: {tail[:200]}"
    missing = [e for e in EXPECTED.findall(text) if e not in proc.stdout]
    if missing:
        return False, f"expected output not found: {missing[0]!r}"
    return True, run.group(1)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("skill", type=Path)
    parser.add_argument("--timeout", type=float, default=120, help="seconds per example (default 120)")
    parser.add_argument("--image", help="run each example in a container of this image")
    parser.add_argument("--env", action="append", default=[], metavar="K=V", help="environment for --image")
    parser.add_argument("--mount", action="append", default=[], metavar="SRC:DST[:ro]", help="extra mount for --image")
    parser.add_argument("--network", default="none", help="container network for --image (default none)")
    args = parser.parse_args()

    assets = args.skill / "assets"
    examples = sorted(p.name for p in assets.iterdir() if p.is_dir()) if assets.is_dir() else []
    if not examples:
        sys.exit(f"no example folders in {assets}")
    results = []
    with tempfile.TemporaryDirectory(prefix="check_assets_") as directory:
        skill_copy = Path(directory) / args.skill.resolve().name
        shutil.copytree(args.skill, skill_copy, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        for name in examples:
            passed, reason = check(skill_copy / "assets" / name, args, skill_copy)
            results.append(passed)
            print(f"{'PASS' if passed else 'FAIL'}  {name}: {reason}", flush=True)
    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
