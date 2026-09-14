"""Readiness checks for the ortools_cp_sat_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver ortools_cp_sat_python` runs this
and keeps its output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "ortools_cp_sat_python"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions.
REFERENCE = '''
# Data
n = 2
optimize = False
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y >= n if optimize else x + y == n)
if optimize:
    model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": y.value()}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

GOOD = ("from ortools.sat.python import cp_model\n"
        "def build(instance):\n"
        "    n = instance['n']\n"
        "    model = cp_model.CpModel()\n"
        "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
        "    model.add(x + y == n)\n"
        "    return model, {'x': x, 'y': y}\n")
OPTIMAL = ("from ortools.sat.python import cp_model\n"
           "def build(instance):\n"
           "    n = instance['n']\n"
           "    model = cp_model.CpModel()\n"
           "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
           "    model.add(x + y >= n)\n"
           "    model.OBJECTIVE(x + y)\n"
           "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = ("from ortools.sat.python import cp_model\n"
                 "def build(instance):\n"
                 "    model = cp_model.CpModel()\n"
                 "    x = model.new_int_var(0, 1, 'x')\n"
                 "    model.add(x == 0)\n"
                 "    model.add(x == 1)\n"
                 "    return model, {'x': x, 'y': 2}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n"
            "from ortools.sat.python import cp_model\n"
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    try:\n"
            "        open('/input/written', 'w')\n"
            "        raise AssertionError('input is writable')\n"
            "    except OSError:\n"
            "        pass\n"
            "    n = instance['n']\n"
            "    model = cp_model.CpModel()\n"
            "    x, y = model.new_int_var(0, n, 'x'), model.new_int_var(0, n, 'y')\n"
            "    model.add(x + y == n)\n"
            "    return model, {'x': x, 'y': y}\n")


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.py", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("OBJECTIVE", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "maximize"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

    try:
        image_identity({"id": SOLVER, "image": "dcp-eval/definitely-absent:readiness"})
        results["missing_image"] = False
    except EvaluationError as error:
        results["missing_image"] = error.reason == "infrastructure_error"

    print(json.dumps(results, sort_keys=True))
    if not all(results.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
