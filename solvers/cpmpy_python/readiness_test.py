"""Readiness checks for the cpmpy_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver cpmpy_python` runs this and keeps
its output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "cpmpy_python"

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

GOOD = ("import cpmpy as cp\n"
        "def build(instance):\n"
        "    n = instance['n']\n"
        "    x, y = cp.intvar(0, n, shape=2)\n"
        "    return cp.Model(x + y == n), {'x': x, 'y': y}\n")
OPTIMAL = ("import cpmpy as cp\n"
           "def build(instance):\n"
           "    n = instance['n']\n"
           "    x, y = cp.intvar(0, n, shape=2)\n"
           "    model = cp.Model(x + y >= n)\n"
           "    model.OBJECTIVE(x + y)\n"
           "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = ("import cpmpy as cp\n"
                 "def build(instance):\n"
                 "    x = cp.intvar(0, 1)\n"
                 "    return cp.Model(False), {'x': x, 'y': 2}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n"
            "import cpmpy as cp\n"
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    n = instance['n']\n"
            "    x, y = cp.intvar(0, n, shape=2)\n"
            "    return cp.Model(x + y == n), {'x': x, 'y': y}\n")


# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). Each pairs a tiny trusted reference with a
# submission that exercises one class of runner bug the modelling campaigns found.

# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an unrelated Golomb ruler to its objective, so CP-SAT finds a solution at once
# but cannot prove the optimum within the budget. A correct runner emits nothing; a
# runner that leaks its unproven incumbent fails the check whatever the reference says.
EASY_MIN = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
UNPROVABLE = ("import cpmpy as cp\n"
              "def build(instance):\n"
              "    x = cp.intvar(0, 10)\n"
              "    marks = cp.intvar(0, 200, shape=11)\n"
              "    diffs = [marks[j] - marks[i] for i in range(11) for j in range(i + 1, 11)]\n"
              "    model = cp.Model(x >= instance['n'], marks[0] == 0, cp.AllDifferent(diffs),\n"
              "                     [marks[i] < marks[i + 1] for i in range(10)])\n"
              "    model.minimize(1000 * x + marks[10])\n"
              "    return model, {'x': x}\n")
# minimization_step_one: the optimum sits one below an easy solution. CP-SAT proves
# optima itself, so this passes here; for a runner that bounds the objective itself,
# its fixture should make the first solution exactly optimum + 1.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = ("import cpmpy as cp\n"
        "def build(instance):\n"
        "    x = cp.intvar(0, 10)\n"
        "    model = cp.Model(x >= instance['n'] - 1)\n"
        "    model.minimize(x)\n"
        "    return model, {'x': x}\n")
# optimum_enumeration: a compound objective (a sum) with ten optimal solutions.
SUM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""
SUM = ("import cpmpy as cp\n"
       "def build(instance):\n"
       "    x = cp.intvar(0, 2, shape=4)\n"
       "    model = cp.Model(cp.sum(x) >= instance['n'])\n"
       "    model.minimize(cp.sum(x))\n"
       "    return model, {'x': x}\n")
# output_shapes: a three-level integer array, a Boolean matrix and a value beyond 32 bits.
SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}
print(json.dumps(solution))
"""
SHAPES = ("import cpmpy as cp\n"
          "def build(instance):\n"
          "    n = instance['n']\n"
          "    cube = cp.intvar(0, 10, shape=(2, 2, 2))\n"
          "    grid = cp.boolvar(shape=(2, 2))\n"
          "    big = cp.intvar(0, 40000000000)\n"
          "    model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],\n"
          "                     [grid[i, j] == (i == j) for i in range(2) for j in range(2)],\n"
          "                     big == 30000000000 + n)\n"
          "    return model, {'cube': cube, 'grid': grid, 'big': big}\n")
# instance_shapes: ragged rows, rows of mixed types, a string field the model ignores,
# and name/note keys, on two instances with different shapes.
SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}
print(json.dumps(solution))
"""
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}
SHAPED = ("import cpmpy as cp\n"
          "def build(instance):\n"
          "    total = cp.intvar(0, 1000)\n"
          "    key = cp.intvar(0, 1000)\n"
          "    model = cp.Model(total == instance['n'] + sum(sum(row) for row in instance['rows']),\n"
          "                     key == sum(row[0] for row in instance['mixed']))\n"
          "    return model, {'total': total, 'key': key}\n")
# error_detail: the library raises while the model is built; the evaluator must report
# execution_error with the library's own message, not a timeout or a bare exit code.
FAILING = ("import cpmpy as cp\n"
           "def build(instance):\n"
           "    x, y = cp.intvar(0, instance['n'], shape=2)\n"
           "    return cp.Model(0.5 * x + y == instance['n']), {'x': x, 'y': y}\n")
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = ("import cpmpy as cp\n"
          "print('loading the model')\n"
          "def build(instance):\n"
          "    print('building for n =', instance['n'])\n"
          "    x, y = cp.intvar(0, instance['n'], shape=2)\n"
          "    return cp.Model(x + y == instance['n']), {'x': x, 'y': y}\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = ("import cpmpy as cp\n"
             "def build(instance):\n"
             "    x, y = cp.intvar(0, instance['n'], shape=2)\n"
             "    spare = cp.intvar(0, 5)\n"
             "    return cp.Model(x + y == instance['n'], spare >= 0), {'x': x, 'y': y}\n")
# large_model: 3000 Booleans in one sum, reported as an output.
LARGE_REF = """
# Data
n = 1500
# End of data
import cpmpy as cp
import json
b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}
print(json.dumps(solution))
"""
LARGE = ("import cpmpy as cp\n"
         "def build(instance):\n"
         "    b = cp.boolvar(shape=3000)\n"
         "    count = cp.intvar(0, 3000)\n"
         "    return cp.Model(count == cp.sum(b), count == instance['n']), {'b': b, 'count': count}\n")


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

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout.py", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail.py", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "float" in json.dumps(result).lower())
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

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
