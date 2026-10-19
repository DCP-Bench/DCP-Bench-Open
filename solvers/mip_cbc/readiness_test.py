"""Readiness checks for the mip_cbc integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver mip_cbc` runs this and keeps its
output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "mip_cbc"

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

HEADER = "import mip\n\n\ndef build(instance):\n    n = instance['n']\n"
BOUNDED = ("    x = m.add_var('x', lb=0, ub=n, var_type=mip.INTEGER)\n"
           "    y = m.add_var('y', lb=0, ub=n, var_type=mip.INTEGER)\n")
GOOD = HEADER + ("    m = mip.Model(solver_name='CBC')\n" + BOUNDED +
                 "    m += x + y == n\n"
                 "    return m, {'x': x, 'y': y}\n")
# The objective is set with m.objective, the direction with the model's sense.
OPTIMAL = HEADER + ("    m = mip.Model(sense=mip.SENSE, solver_name='CBC')\n" + BOUNDED +
                    "    m += x + y >= n\n"
                    "    m.objective = x + y\n"
                    "    return m, {'x': x, 'y': y}\n")
# A declared output that is a linear expression rather than a variable. Its value
# comes from the expression, not from its coefficients.
EXPRESSION = HEADER + ("    m = mip.Model(solver_name='CBC')\n"
                       "    x = m.add_var('x', lb=0, ub=n, var_type=mip.INTEGER)\n"
                       "    return m, {'x': x, 'y': n - x}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = HEADER + ("    m = mip.Model(solver_name='CBC')\n" + BOUNDED +
                          "    m += x >= n + 1\n"
                          "    return m, {'x': x, 'y': y}\n")
SLOW = "import time\n\n\ndef build(instance):\n    time.sleep(120)\n"
# A declared output that is not integral must be refused rather than rounded.
FRACTIONAL = HEADER + ("    m = mip.Model(solver_name='CBC')\n" + BOUNDED +
                       "    half = m.add_var('half', lb=0, ub=1, var_type=mip.CONTINUOUS)\n"
                       "    m += x + y == n\n"
                       "    m += half == 0.5\n"
                       "    return m, {'x': x, 'half': half}\n")
# CBC with the default max_mip_gap stops at a gap of 1e-4 and reports OPTIMAL, so a
# runner that trusted that status would emit an unproven incumbent. The subset-sum
# below cannot be proven within 5 s with a zero gap; it finds an incumbent first.
UNPROVEN = HEADER + ("    import random\n"
                     "    random.seed(1)\n"
                     "    m = mip.Model(sense=mip.MAXIMIZE, solver_name='CBC')\n"
                     "    weights = [random.randint(10 ** 6, 4 * 10 ** 6) for _ in range(150)]\n"
                     "    picks = [m.add_var(f'b{i}', var_type=mip.BINARY) for i in range(150)]\n"
                     "    load = mip.xsum(w * b for w, b in zip(weights, picks))\n"
                     "    x = m.add_var('x', var_type=mip.BINARY)\n"
                     "    y = m.add_var('y', var_type=mip.BINARY)\n"
                     "    m += x + y == n\n"
                     "    m += load <= sum(weights) // 2\n"
                     "    m.objective = load\n"
                     "    return m, {'x': x, 'y': y}\n")
ISOLATED = HEADER + ("    import os, socket\n"
                     "    assert os.getuid() != 0, 'container runs as root'\n"
                     "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
                     "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
                     "    probe = socket.socket()\n"
                     "    probe.settimeout(0.5)\n"
                     "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
                     "    m = mip.Model(solver_name='CBC')\n" + BOUNDED +
                     "    m += x + y == n\n"
                     "    return m, {'x': x, 'y': y}\n")

# optimization_timeout: the reference is easy (minimise x, optimum n). The submission
# adds an unrelated 11-mark Golomb ruler to its objective, which CBC cannot prove in 3 s.
# A correct runner emits nothing: the status is a timeout with zero solutions.
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
UNPROVABLE = ("import mip\n\n\ndef build(instance):\n"
              "    m = mip.Model(sense=mip.MINIMIZE, solver_name='CBC')\n"
              "    x = m.add_var('x', lb=0, ub=10, var_type=mip.INTEGER)\n"
              "    marks = [m.add_var(f'm{i}', lb=0, ub=200, var_type=mip.INTEGER) for i in range(11)]\n"
              "    m += x >= instance['n']\n"
              "    m += marks[0] == 0\n"
              "    for i in range(10):\n"
              "        m += marks[i + 1] >= marks[i] + 1\n"
              "    pairs = [(i, j) for i in range(11) for j in range(i + 1, 11)]\n"
              "    diffs = {p: m.add_var(f'd{p[0]}_{p[1]}', lb=1, ub=200, var_type=mip.INTEGER) for p in pairs}\n"
              "    for (i, j), d in diffs.items():\n"
              "        m += d == marks[j] - marks[i]\n"
              "    for s in range(len(pairs)):\n"
              "        for t in range(s + 1, len(pairs)):\n"
              "            u, w = diffs[pairs[s]], diffs[pairs[t]]\n"
              "            o = m.add_var(f'o{s}_{t}', var_type=mip.BINARY)\n"
              "            m += u <= w - 1 + 201 * (1 - o)\n"
              "            m += u >= w + 1 - 201 * o\n"
              "    m.objective = 1000 * x + marks[10]\n"
              "    return m, {'x': x}\n")
# minimization_step_one: the optimum sits one below an easy solution.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = ("import mip\n\n\ndef build(instance):\n"
        "    m = mip.Model(sense=mip.MINIMIZE, solver_name='CBC')\n"
        "    x = m.add_var('x', lb=0, ub=10, var_type=mip.INTEGER)\n"
        "    m += x >= instance['n'] - 1\n"
        "    m.objective = x\n"
        "    return m, {'x': x}\n")
# optimum_enumeration: a sum over four integers in 0..2 with ten optimal solutions.
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
SUM = ("import mip\n\n\ndef build(instance):\n"
       "    m = mip.Model(sense=mip.MINIMIZE, solver_name='CBC')\n"
       "    x = [m.add_var(f'x{i}', lb=0, ub=2, var_type=mip.INTEGER) for i in range(4)]\n"
       "    m += mip.xsum(x) >= instance['n']\n"
       "    m.objective = mip.xsum(x)\n"
       "    return m, {'x': x}\n")
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
SHAPES = ("import mip\n\n\ndef build(instance):\n"
          "    n = instance['n']\n"
          "    m = mip.Model(solver_name='CBC')\n"
          "    cube = [[[m.add_var(f'c{i}{j}{k}', lb=0, ub=10, var_type=mip.INTEGER) for k in range(2)]\n"
          "             for j in range(2)] for i in range(2)]\n"
          "    grid = [[m.add_var(f'g{i}{j}', var_type=mip.BINARY) for j in range(2)] for i in range(2)]\n"
          "    big = m.add_var('big', lb=0, ub=40000000000, var_type=mip.INTEGER)\n"
          "    for i in range(2):\n"
          "        for j in range(2):\n"
          "            for k in range(2):\n"
          "                m += cube[i][j][k] == i + j + k + n\n"
          "            m += grid[i][j] == (1 if i == j else 0)\n"
          "    m += big == 30000000000 + n\n"
          "    return m, {'cube': cube, 'grid': grid, 'big': big}\n")
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
SHAPED = ("import mip\n\n\ndef build(instance):\n"
          "    m = mip.Model(solver_name='CBC')\n"
          "    total = m.add_var('total', lb=0, ub=1000, var_type=mip.INTEGER)\n"
          "    key = m.add_var('key', lb=0, ub=1000, var_type=mip.INTEGER)\n"
          "    m += total == instance['n'] + sum(sum(row) for row in instance['rows'])\n"
          "    m += key == sum(row[0] for row in instance['mixed'])\n"
          "    return m, {'total': total, 'key': key}\n")
# error_detail: a product of two variables is not linear. Python-MIP raises while the
# model is built; the runner must report error with that message, not a timeout.
FAILING = ("import mip\n\n\ndef build(instance):\n"
           "    m = mip.Model(solver_name='CBC')\n"
           "    x = m.add_var('x', lb=0, ub=instance['n'], var_type=mip.INTEGER)\n"
           "    y = m.add_var('y', lb=0, ub=instance['n'], var_type=mip.INTEGER)\n"
           "    m += x * y == instance['n']\n"
           "    return m, {'x': x, 'y': y}\n")
# stray_stdout: the model prints while it loads and builds; the protocol stream must survive.
CHATTY = ("import mip\n"
          "print('loading the model')\n\n\n"
          "def build(instance):\n"
          "    print('building for n =', instance['n'])\n"
          "    m = mip.Model(solver_name='CBC')\n"
          "    x = m.add_var('x', lb=0, ub=instance['n'], var_type=mip.INTEGER)\n"
          "    y = m.add_var('y', lb=0, ub=instance['n'], var_type=mip.INTEGER)\n"
          "    m += x + y == instance['n']\n"
          "    return m, {'x': x, 'y': y}\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = ("import mip\n\n\ndef build(instance):\n"
             "    n = instance['n']\n"
             "    m = mip.Model(solver_name='CBC')\n"
             "    x = m.add_var('x', lb=0, ub=n, var_type=mip.INTEGER)\n"
             "    y = m.add_var('y', lb=0, ub=n, var_type=mip.INTEGER)\n"
             "    spare = m.add_var('spare', lb=0, ub=5, var_type=mip.INTEGER)\n"
             "    m += x + y == n\n"
             "    m += spare >= 0\n"
             "    return m, {'x': x, 'y': y}\n")
# large_model: 3000 binaries in one sum, reported as an output.
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
LARGE = ("import mip\n\n\ndef build(instance):\n"
         "    m = mip.Model(solver_name='CBC')\n"
         "    b = [m.add_var(f'b{i}', var_type=mip.BINARY) for i in range(3000)]\n"
         "    count = m.add_var('count', lb=0, ub=3000, var_type=mip.INTEGER)\n"
         "    m += mip.xsum(b) == count\n"
         "    m += count == instance['n']\n"
         "    return m, {'b': b, 'count': count}\n")

# objective_offset: a constant term and negative values, in both directions. Minimum -28 at
# (-4, 3); maximum 2 at (2, -3). Both optima are unique.
OFFSET_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(-4, 2, name="x")
y = cp.intvar(-3, 3, name="y")
model = cp.Model(x + y >= -5)
model.minimize(2 * x - 3 * y - 11)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
OFFSET_MAX_REF = OFFSET_REF.replace("model.minimize", "model.maximize")
OFFSET = ("import mip\n\n\ndef build(instance):\n"
          "    m = mip.Model(sense=mip.SENSE, solver_name='CBC')\n"
          "    x = m.add_var('x', lb=-4, ub=2, var_type=mip.INTEGER)\n"
          "    y = m.add_var('y', lb=-3, ub=3, var_type=mip.INTEGER)\n"
          "    m += x + y >= -5\n"
          "    m.objective = 2 * x - 3 * y + (-11)\n"
          "    return m, {'x': x, 'y': y}\n")
# negative_and_zero: negative integers come back as negative integers; a continuous value of
# -1e-7 is within tolerance of 0 and must come back as 0, never as a float or -0.
ROUND_REF = """
# Data
n = 3
# End of data
import cpmpy as cp
import json
x = cp.intvar(-5, -1, name="x")
z = cp.intvar(0, 0, name="z")
model = cp.Model(x == -n)
model.solve()
solution = {"x": int(x.value()), "z": int(z.value())}
print(json.dumps(solution))
"""
ROUND = ("import mip\n\n\ndef build(instance):\n"
         "    m = mip.Model(solver_name='CBC')\n"
         "    x = m.add_var('x', lb=-5, ub=-1, var_type=mip.INTEGER)\n"
         "    z = m.add_var('z', lb=-1e-7, ub=1e-7, var_type=mip.CONTINUOUS)\n"
         "    m += x == -instance['n']\n"
         "    m += z == -1e-7\n"
         "    return m, {'x': x, 'z': z}\n")
# unbounded_objective: a maximisation with no upper bound is error, not unsat.
UNBOUNDED = ("import mip\n\n\ndef build(instance):\n"
             "    m = mip.Model(sense=mip.MAXIMIZE, solver_name='CBC')\n"
             "    x = m.add_var('x', lb=0, var_type=mip.INTEGER)\n"
             "    m.objective = x\n"
             "    return m, {'x': x}\n")


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
        # x+y==2 has exactly three solutions, so asking for more must come back as
        # exhaustion rather than as a shortfall the evaluator would reject.
        exhausted = check("exhausted_enumeration", GOOD, solution_limit=5)
        results["exhausted_enumeration"] = (
            results["exhausted_enumeration"]
            and exhausted["instances"][0]["solutions_received"] == 3
            and exhausted["instances"][0]["runner_status"]["status"] == "complete")
        check("minimization", OPTIMAL.replace("SENSE", "MINIMIZE"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("SENSE", "MAXIMIZE"), reference=MAXIMIZING)
        check("expression_output", EXPRESSION, solution_limit=2)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("fractional_output", FRACTIONAL, expected={"execution_error", "invalid_output"})
        check("unproven_optimum", UNPROVEN, expected={"execution_timeout"}, execution_timeout=5)
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
                                   and "Can not multiply" in json.dumps(result))
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
        check("objective_offset_minimization", OFFSET.replace("SENSE", "MINIMIZE"), reference=OFFSET_REF)
        check("objective_offset_maximization", OFFSET.replace("SENSE", "MAXIMIZE"), reference=OFFSET_MAX_REF)
        check("negative_and_zero", ROUND, reference=ROUND_REF)
        check("unbounded_objective", UNBOUNDED, expected={"execution_error"})

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
