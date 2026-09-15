"""Regression for the model-generator skill's commit-cadence guidance.

The rule this replaces committed one model at a time, and justified itself with
resume: "an interrupted run always resumes from a clean state". That reason does
not depend on git. This check demonstrates it does not, by driving the real
helpers: a run whose attempt has never been committed is still reported by
`generation.manage status`, so commit granularity and resumability are
independent, and the batch that suits the run can be chosen freely.

It also requires the bundle to say commits are batched, so a bundle carrying the
old one-commit-per-model rule fails.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# The helpers need the repository environment, which is not necessarily the
# interpreter this script was started with.
VENV = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PYTHON = str(VENV) if VENV.exists() else sys.executable
PROBLEM = "csplib_054_n_queens"
SOLVER = "cpmpy_python"
SKILL = "solvers/cpmpy_python/skills/cpmpy-python"


def helper(*arguments):
    finished = subprocess.run([PYTHON, "-m", "generation.manage", *arguments],
                              cwd=ROOT, capture_output=True, text=True)
    return finished.returncode, finished.stdout, finished.stderr


def tracked(path):
    """Whether git has this path committed on the current branch."""
    finished = subprocess.run(["git", "ls-files", "--error-unmatch", str(path)],
                              cwd=ROOT, capture_output=True, text=True)
    return finished.returncode == 0


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: model_generator_resume_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    run = "resume-regression-" + tempfile.mkdtemp(prefix="", dir=tempfile.gettempdir()).rsplit("\\", 1)[-1][-8:]
    directory = ROOT / "generation" / "runs" / run
    try:
        code, out, err = helper("init", "--run", run)
        if code:
            failures.append(f"could not create a run: {err.strip()[:200]}")
        else:
            code, out, err = helper("attempt", "--run", run, "--problem", PROBLEM,
                                    "--solver", SOLVER, "--skill", SKILL)
            if code:
                failures.append(f"could not create an attempt: {err.strip()[:200]}")
            else:
                attempt = Path(json.loads(out)["attempt"])
                # Nothing here has been committed, which is the whole point.
                if tracked(attempt.relative_to(ROOT) / "attempt.json"):
                    failures.append("the attempt was already committed; the check proves nothing")
                code, out, err = helper("status", "--run", run)
                if code:
                    failures.append(f"status refused to read the run back: {err.strip()[:200]}")
                elif PROBLEM not in out:
                    failures.append("status did not report the uncommitted attempt, so resume "
                                    "really would depend on committing each one")
    finally:
        shutil.rmtree(directory, ignore_errors=True)

    batched = [line for line in skill.splitlines()
               if "commit" in line.lower() and "batch" in line.lower()]
    if not batched:
        failures.append(f"{bundle} does not say commits are batched")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: an uncommitted run is still resumable, and the skill batches commits")


if __name__ == "__main__":
    main()
