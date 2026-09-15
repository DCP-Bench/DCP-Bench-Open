"""Regression for the model-generator skill's use of `generation.brief`.

Getting the declared output names or an instance field's shape wrong costs an
attempt, and both are mechanical facts about the reference rather than judgement
calls. This check runs `generation.brief` on two problems and requires it to
report those facts — including the ragged field that makes `covering_opl`
impossible on a rectangular binder — and requires the bundle to tell the agent
to use it, so a bundle that leaves the extraction to be done by eye fails.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
PYTHON = str(VENV) if VENV.exists() else sys.executable


def brief(problem):
    finished = subprocess.run([PYTHON, "-W", "ignore::SyntaxWarning", "-m", "generation.brief", problem],
                              cwd=ROOT, capture_output=True, text=True)
    if finished.returncode:
        raise ValueError(f"generation.brief {problem} exited {finished.returncode}: "
                         f"{finished.stderr.strip()[:200]}")
    return json.loads(finished.stdout)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: model_generator_brief_regression.py SKILL_BUNDLE")
    bundle = Path(sys.argv[1])
    skill = (bundle / "SKILL.md").read_text(encoding="utf-8")

    failures = []
    try:
        # An objective problem whose declared output names differ from its
        # variable names, and whose second output is an expression.
        golomb = brief("csplib_006_golomb_rulers")
        if golomb["objective"] != "minimize":
            failures.append(f"golomb objective read as {golomb['objective']}")
        if set(golomb["declared_outputs"]) != {"marks", "length"}:
            failures.append(f"golomb outputs read as {sorted(golomb['declared_outputs'])}")
        if not golomb["declared_outputs"].get("marks", "").endswith("int"):
            failures.append("golomb marks did not come back as an integer array")
        # The ragged field that no rectangular binder can take.
        covering = brief("covering_opl")
        if covering["unbindable_fields"] != ["Qualified"]:
            failures.append(f"covering_opl unbindable fields read as {covering['unbindable_fields']}")
    except (ValueError, KeyError) as error:
        failures.append(f"generation.brief did not produce a usable contract: {error}")

    if "generation.brief" not in skill:
        failures.append(f"{bundle} does not tell the agent to read the contract with generation.brief")

    for failure in failures:
        print(f"FAIL {failure}")
    if failures:
        raise SystemExit(1)
    print(f"ok {bundle}: the contract is produced mechanically, and the skill says to use it")


if __name__ == "__main__":
    main()
