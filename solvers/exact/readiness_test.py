"""Readiness checks for the exact integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver exact` runs this and keeps its
output as the readiness evidence.

The optimisation checks carry the weight here. Exact answers `"SAT"` when it
proved the optimum and `"TIMEOUT"` when it did not, while `hasSolution()` stays
true either way, so a runner that read the solution without reading the state
would hand over an unproven answer for the evaluator to compare against the
reference optimum. Maximisation also comes back negated. minimization and
maximization below are what hold both of those.

`native_api` guards the mistake this integration was rebuilt to fix:
submissions call `exact.Exact` directly, not a modelling layer shipped beside
the runner.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "exact"

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

HEAD = '''from exact import Exact


def build(instance):
    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
'''
EXPORT = '    return solver, {"x": "x", "y": "y"}\n'

GOOD = HEAD + '    solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)\n' + EXPORT
# `n` is a maximum here, so the objective has room to move in both directions.
OPTIMAL = (HEAD + '    solver.addConstraint([(1, "x"), (1, "y")], True, n)\n'
           '    return solver, {"x": "x", "y": "y"}, ("DIRECTION", [(1, "x"), (1, "y")])\n')
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + '    solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)\n'
             "    import os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = (HEAD + '    solver.addConstraint([(1, "x")], True, 0, True, 0)\n'
                 '    solver.addConstraint([(1, "x")], True, 1, True, 1)\n' + EXPORT)
# Proving a knapsack optimum is what Exact is slow at; pigeonhole is no
# obstacle to it at all. The weights are generated from a fixed recurrence so
# the instance is the same on every run.
SLOW = (HEAD + '    solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)\n'
        "    seed, weights = 7, []\n"
        "    for i in range(160):\n"
        "        seed = (seed * 1103515245 + 12345) % 9999991\n"
        "        weights.append(seed % 8999999 + 1000000)\n"
        '        solver.addVariable(f"k{i}", 0, 1)\n'
        '    picks = [(weights[i], f"k{i}") for i in range(160)]\n'
        "    solver.addConstraint(picks, False, 0, True, sum(weights) // 2)\n"
        '    return solver, {"x": "x", "y": "y"}, ("maximize", picks)\n')

ISOLATED = '''from exact import Exact


def build(instance):
    import os
    import socket

    assert os.getuid() != 0, "container runs as root"
    assert not os.path.exists("/dataset"), "dataset is visible to the candidate"
    assert sorted(os.listdir("/input")) == ["model.py", "request.json"], "unexpected /input"
    try:
        open("/input/written", "w")
        raise AssertionError("input is writable")
    except OSError:
        pass
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.5)
    try:
        probe.connect(("1.1.1.1", 443))
        raise AssertionError("network reachable")
    except OSError:
        pass
    finally:
        probe.close()

    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
    solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)
    return solver, {"x": "x", "y": "y"}
'''

# The image must carry Exact itself and nothing standing in for it.
NATIVE = '''import exact
from exact import Exact


def build(instance):
    assert Exact.__module__.startswith("exact"), Exact.__module__
    for absent in ("dcp_pb", "dcp_sat", "dcp_maxsat"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass
    # The native calls a submission is built from.
    for method in ("addVariable", "addConstraint", "setObjective", "toOptimum",
                   "runFull", "getLastSolutionFor", "invalidateLastSol",
                   "addReification", "addMultiplication"):
        assert hasattr(Exact, method), method

    n = instance["n"]
    solver = Exact()
    solver.addVariable("x", 0, n)
    solver.addVariable("y", 0, n)
    solver.addConstraint([(1, "x"), (1, "y")], True, n, True, n)
    return solver, {"x": "x", "y": "y"}
'''


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.py"
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("native_api", NATIVE)
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
