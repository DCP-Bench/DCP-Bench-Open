#!/usr/bin/env python3
"""Run a model on every instance of the toy problems and judge each run. Standard library only.

Usage: run_toy_tests.py --cmd 'python models/{problem}.py {instance}' [--problems a,b] [--timeout 120]

--cmd is a shell command with two placeholders: {problem} is the problem
directory name (e.g. knapsack) and {instance} the absolute path of the
instance JSON. It runs in the current directory, so a model per problem lives
wherever the command says. Prints one line per instance and a summary; the
exit code is 0 only if every run passed.
"""
import argparse
import shlex
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill folder free of __pycache__

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_solution import judge  # noqa: E402

TOY = Path(__file__).resolve().parent.parent / "assets" / "toy-problems"


def message(*streams, lines=3, width=300):
    """The last few non-empty lines of the first stream that has any, on one line."""
    for text in streams:
        tail = [line.strip() for line in text.splitlines() if line.strip()][-lines:]
        if tail:
            joined = " | ".join(tail)
            return joined if len(joined) <= width else "..." + joined[-width:]
    return "(no output)"


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cmd", required=True)
    parser.add_argument("--problems", help="comma-separated subset (default: all)")
    parser.add_argument("--timeout", type=float, default=120, help="seconds per run")
    args = parser.parse_args()

    problems = sorted(p.name for p in TOY.iterdir() if (p / "check.py").exists())
    if args.problems:
        wanted = args.problems.split(",")
        unknown = set(wanted) - set(problems)
        if unknown:
            sys.exit(f"unknown problem(s): {', '.join(sorted(unknown))}; choose from {', '.join(problems)}")
        problems = wanted

    results = []
    for problem in problems:
        for instance in sorted((TOY / problem / "instances").glob("*.json")):
            cmd = args.cmd.format(problem=problem, instance=shlex.quote(str(instance)))
            try:
                run = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=args.timeout)
                if run.returncode != 0:
                    passed, reason = False, f"exit code {run.returncode}: {message(run.stderr, run.stdout)}"
                else:
                    passed, reason = judge(TOY / problem, instance, run.stdout)
                    if not passed and run.stderr.strip():  # e.g. a solver that reports an error and exits 0
                        reason += f"; stderr: {message(run.stderr)}"
            except subprocess.TimeoutExpired:
                passed, reason = False, f"timeout after {args.timeout:g}s"
            results.append(passed)
            print(f"{'PASS' if passed else 'FAIL'}  {problem}/{instance.stem}: {reason}", flush=True)

    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
