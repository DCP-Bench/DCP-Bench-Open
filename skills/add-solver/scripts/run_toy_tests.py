#!/usr/bin/env python3
"""Run a model on every instance of the toy problems and judge each run. Standard library only.

Usage:
  run_toy_tests.py --export DIR
  run_toy_tests.py --cmd 'python models/{problem}.py {instance}' [--public DIR] [--logs DIR]
                   [--problems a,b] [--timeout 120]

--export DIR writes what the agent under test may see: each problem's problem.md and
instances/, plus the README's output convention. Never the answer keys (expected/) or
the checkers (check.py), which stay with this script.

--cmd is a shell command with two placeholders: {problem} is the problem directory
name (e.g. knapsack) and {instance} the absolute path of an instance JSON. It runs in
the current directory, so a model per problem lives wherever the command says. With
--public DIR, {instance} points into that exported copy, so a container only needs
DIR mounted (at the same path) and never sees the answer keys:

  run_toy_tests.py --public /tmp/toy --cmd 'docker run --rm --network none \\
      -v /tmp/toy:/tmp/toy:ro -v "$PWD/models":/m:ro IMAGE python3 /m/{problem}.py {instance}'

Each run gets --timeout seconds (default 120); a run that takes longer is a FAIL.
Prints its own command line first, then one line per instance with its wall time and a
summary; on a failure the line holds the exit code, the first error line and the last
lines of stderr. --logs DIR keeps the command line in DIR/command.txt and every run's
full stdout and stderr in DIR/<problem>/<instance>.log. The exit code is 0 only if every
run passed.
"""
import argparse
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True  # keep the skill folder free of __pycache__

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check_solution import judge  # noqa: E402

TOY = Path(__file__).resolve().parent.parent / "assets" / "toy-problems"
ANSI = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")
ERROR_LINE = re.compile(r"error|exception|traceback|panicked|fatal|undefined|not found", re.I)


def problems_in(root):
    return sorted(p.name for p in root.iterdir() if (p / "instances").is_dir())


def export(target):
    """Copy the tester-visible part of the toy problems to target."""
    target = Path(target).resolve()
    for problem in problems_in(TOY):
        destination = target / problem
        (destination / "instances").mkdir(parents=True, exist_ok=True)
        shutil.copy2(TOY / problem / "problem.md", destination / "problem.md")
        for instance in (TOY / problem / "instances").glob("*.json"):
            shutil.copy2(instance, destination / "instances" / instance.name)
    readme = (TOY / "README.md").read_text(encoding="utf-8")
    convention = readme[readme.find("## Output convention"):] if "## Output convention" in readme else ""
    (target / "README.md").write_text("# Toy problems\n\nOne program per problem directory, taking the "
                                      "instance JSON path as its only argument.\n\n" + convention,
                                      encoding="utf-8")
    return target


def diagnosis(stdout, stderr, width=400):
    """The first error-looking line and the last few lines of stderr (else stdout), on one line."""
    for text in (stderr, stdout):
        lines = [line.strip() for line in ANSI.sub("", text).splitlines() if line.strip()]
        if not lines:
            continue
        first = next((line for line in lines if ERROR_LINE.search(line)), None)
        tail = lines[-4:]
        parts = ([first] if first and first not in tail else []) + tail
        joined = " | ".join(parts)
        return joined if len(joined) <= width else joined[:150] + " ... " + joined[-(width - 155):]
    return "(no output)"


def quote(argument):
    """Quote one argument for the shell that subprocess uses with shell=True (cmd.exe on Windows)."""
    return subprocess.list2cmdline([argument]) if os.name == "nt" else shlex.quote(argument)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--export", metavar="DIR", help="write the tester-visible copy to DIR and exit")
    parser.add_argument("--cmd")
    parser.add_argument("--public", metavar="DIR", help="take {instance} from this exported copy (created if missing)")
    parser.add_argument("--logs", metavar="DIR", help="keep each run's stdout and stderr here")
    parser.add_argument("--problems", help="comma-separated subset (default: all)")
    parser.add_argument("--timeout", type=float, default=120, help="seconds per run (default 120)")
    args = parser.parse_args()

    if args.export:
        print(f"exported to {export(args.export)}")
        return
    if not args.cmd:
        parser.error("--cmd is required unless --export is given")

    instances_root = TOY
    if args.public:
        public = Path(args.public).resolve()
        instances_root = public if (public / "README.md").exists() else export(public)

    problems = problems_in(TOY)
    if args.problems:
        wanted = args.problems.split(",")
        unknown = set(wanted) - set(problems)
        if unknown:
            sys.exit(f"unknown problem(s): {', '.join(sorted(unknown))}; choose from {', '.join(problems)}")
        problems = wanted

    # Record the exact invocation, so a later run can repeat it.
    invocation = " ".join(quote(argument) for argument in [Path(sys.argv[0]).name, *sys.argv[1:]])
    print(f"$ {invocation}", flush=True)
    if args.logs:
        Path(args.logs).mkdir(parents=True, exist_ok=True)
        (Path(args.logs) / "command.txt").write_text(invocation + "\n", encoding="utf-8")

    results = []
    for problem in problems:
        for instance in sorted((instances_root / problem / "instances").glob("*.json")):
            # str.replace, not str.format: a command may contain literal braces.
            cmd = args.cmd.replace("{problem}", problem).replace("{instance}", quote(str(instance)))
            start = time.monotonic()
            stdout = stderr = ""
            try:
                run = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=args.timeout)
                stdout, stderr = run.stdout, run.stderr
                if run.returncode != 0:
                    passed, reason = False, f"exit code {run.returncode}: {diagnosis(stdout, stderr)}"
                else:
                    passed, reason = judge(TOY / problem, TOY / problem / "instances" / instance.name, stdout)
                    if not passed and stderr.strip():  # e.g. a solver that reports an error and exits 0
                        reason += f"; stderr: {diagnosis('', stderr)}"
            except subprocess.TimeoutExpired as error:
                stdout = error.stdout.decode(errors="replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
                stderr = error.stderr.decode(errors="replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
                passed, reason = False, f"timeout after {args.timeout:g}s (raise --timeout for a slow but correct model)"
            seconds = time.monotonic() - start
            if args.logs:
                log = Path(args.logs) / problem / f"{instance.stem}.log"
                log.parent.mkdir(parents=True, exist_ok=True)
                log.write_text(f"$ {cmd}\n# {seconds:.2f}s, {'PASS' if passed else 'FAIL'}: {reason}\n"
                               f"--- stdout\n{stdout}\n--- stderr\n{stderr}\n", encoding="utf-8")
            results.append(passed)
            print(f"{'PASS' if passed else 'FAIL'}  {problem}/{instance.stem} [{seconds:.1f}s]: {reason}", flush=True)

    print(f"\n{sum(results)}/{len(results)} passed")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
