"""Readiness checks for the cvc5_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver cvc5_python` runs this and keeps
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

SOLVER = "cvc5_python"

# Trusted references, kept here so this script does not depend on the test
# suite. n=2 gives x+y==2 exactly three solutions.
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
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
OPTIMIZING = REFERENCE.replace("optimize = False", "optimize = True")
MAXIMIZING = OPTIMIZING.replace("model.minimize", "model.maximize")

GOOD = ("import cvc5.pythonic as cz\n"
        "def build(instance):\n"
        "    n = instance['n']\n"
        "    x, y = cz.Ints('x y')\n"
        "    s = cz.Solver()\n"
        "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y == n)\n"
        "    return s, {'x': x, 'y': y}\n")
OPTIMAL = ("import cvc5.pythonic as cz\n"
           "def build(instance):\n"
           "    n = instance['n']\n"
           "    x, y = cz.Ints('x y')\n"
           "    s = cz.Solver()\n"
           "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y >= n)\n"
           "    return s, {'x': x, 'y': y}, ('DIRECTION', x + y)\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = ("import cvc5.pythonic as cz\n"
                 "def build(instance):\n"
                 "    x = cz.Int('x')\n"
                 "    s = cz.Solver()\n"
                 "    s.add(cz.BoolVal(False))\n"
                 "    return s, {'x': x, 'y': 2}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n"
            "import cvc5.pythonic as cz\n"
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    n = instance['n']\n"
            "    x, y = cz.Ints('x y')\n"
            "    s = cz.Solver()\n"
            "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y == n)\n"
            "    return s, {'x': x, 'y': y}\n")

# Bug-class checks (readiness_level 2). Each one is accepted only when the runner
# does what the contract says; see CONTRACT.md.
NEGATIVE_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
model = cp.Model(x + y >= 1)
model.DIRECTION(-2 * x - y + 5)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
NEGATIVE_SUBMISSION = ("import cvc5.pythonic as cz\n"
                       "def build(instance):\n"
                       "    x, y = cz.Ints('x y')\n"
                       "    s = cz.Solver()\n"
                       "    s.add(x >= 0, x <= 2, y >= 0, y <= 2, x + y >= 1)\n"
                       "    return s, {'x': x, 'y': y}, ('DIRECTION', -2 * x - y + 5)\n")
# cvc5's first model here has objective 21 (checked by hand in the image); the optimum is 8 at (0, 4).
# The runner must tighten the objective to prove it.
PROOF_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 9, name="x")
y = cp.intvar(0, 9, name="y")
model = cp.Model(x + 2 * y >= 7)
model.minimize(3 * x + 2 * y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
PROOF_SUBMISSION = ("import cvc5.pythonic as cz\n"
                    "def build(instance):\n"
                    "    x, y = cz.Ints('x y')\n"
                    "    s = cz.Solver()\n"
                    "    s.add(x >= 0, x <= 9, y >= 0, y <= 9, x + 2 * y >= 7)\n"
                    "    return s, {'x': x, 'y': y}, ('minimize', 3 * x + 2 * y)\n")
# Ten optima (x+y==4 over five pairs, times two values of z), solution_limit 3.
OPTIMA_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 4, name="x")
y = cp.intvar(0, 4, name="y")
z = cp.intvar(0, 1, name="z")
model = cp.Model(x + y == 4)
model.minimize(x + y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value()), "z": int(z.value())}
print(json.dumps(solution))
'''
OPTIMA_SUBMISSION = ("import cvc5.pythonic as cz\n"
                     "def build(instance):\n"
                     "    x, y, z = cz.Ints('x y z')\n"
                     "    s = cz.Solver()\n"
                     "    s.add(x >= 0, x <= 4, y >= 0, y <= 4, z >= 0, z <= 1, x + y == 4)\n"
                     "    return s, {'x': x, 'y': y, 'z': z}, ('minimize', x + y)\n")
NESTED_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
y = cp.intvar(0, 2, name="y")
model = cp.Model(x + y == 2)
model.solve()
solution = {"m": [[int(x.value()), int(y.value())], [int(y.value()), int(x.value())]],
            "v": [int(x.value()), int(y.value())]}
print(json.dumps(solution))
'''
NESTED_SUBMISSION = ("import cvc5.pythonic as cz\n"
                     "def build(instance):\n"
                     "    x, y = cz.Ints('x y')\n"
                     "    s = cz.Solver()\n"
                     "    s.add(x >= 0, x <= 2, y >= 0, y <= 2, x + y == 2)\n"
                     "    return s, {'m': [[x, y], [y, x]], 'v': [x, y]}\n")
BOOL_REFERENCE = '''
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
model = cp.Model(x >= 1)
model.solve()
solution = {"x": int(x.value()), "b": bool(x.value() >= 1), "c": True}
print(json.dumps(solution))
'''
BOOL_SUBMISSION = ("import cvc5.pythonic as cz\n"
                   "def build(instance):\n"
                   "    x = cz.Int('x')\n"
                   "    b = cz.Bool('b')\n"
                   "    s = cz.Solver()\n"
                   "    s.add(x >= 1, x <= 2, b == (x >= 1))\n"
                   "    return s, {'x': x, 'b': b, 'c': True}\n")
ERROR_SUBMISSION = ("import cvc5.pythonic as cz\n"
                    "def build(instance):\n"
                    "    x = cz.Int('x')\n"
                    "    s = cz.Solver()\n"
                    "    s.add(x == 'abc')\n"
                    "    return s, {'x': x}\n")
STDOUT_SUBMISSION = ("import cvc5.pythonic as cz\n"
                     "print('model noise on stdout')\n"
                     "def build(instance):\n"
                     "    x, y = cz.Ints('x y')\n"
                     "    s = cz.Solver()\n"
                     "    s.add(x >= 0, x <= 2, y >= 0, y <= 2, x + y == 2)\n"
                     "    print('more noise')\n"
                     "    return s, {'x': x, 'y': y}\n")
AUX_SUBMISSION = ("import cvc5.pythonic as cz\n"
                  "def build(instance):\n"
                  "    x, y, a = cz.Ints('x y a')\n"
                  "    s = cz.Solver()\n"
                  "    s.add(x >= 0, x <= 2, y >= 0, y <= 2, x + y == 2, a >= 0, a <= 2)\n"
                  "    return s, {'x': x, 'y': y}\n")
LARGE_REFERENCE = '''
import cpmpy as cp
import json
bs = cp.boolvar(shape=3000, name="b")
model = cp.Model(cp.sum(bs) == 1500)
model.solve()
solution = {"total": 1500}
print(json.dumps(solution))
'''
LARGE_SUBMISSION = ("import cvc5.pythonic as cz\n"
                    "def build(instance):\n"
                    "    bs = cz.Bools(' '.join('b%d' % i for i in range(3000)))\n"
                    "    total = cz.Sum([cz.If(b, 1, 0) for b in bs])\n"
                    "    s = cz.Solver()\n"
                    "    s.add(total == 1500)\n"
                    "    return s, {'total': total}\n")
# Golomb ruler on 10 marks with an easy reference: the submission's objective
# includes the ruler length, whose optimality is far too hard for 3 s.
TIMEOUT_REFERENCE = REFERENCE
TIMEOUT_SUBMISSION = ("import cvc5.pythonic as cz\n"
                      "def build(instance):\n"
                      "    x, y = cz.Ints('x y')\n"
                      "    marks = cz.Ints(' '.join('m%d' % i for i in range(10)))\n"
                      "    s = cz.Solver()\n"
                      "    s.add(x >= 0, x <= 2, y >= 0, y <= 2, x + y >= 1)\n"
                      "    s.add(marks[0] == 0)\n"
                      "    s.add([marks[i] < marks[i + 1] for i in range(9)])\n"
                      "    s.add([m <= 60 for m in marks])\n"
                      "    diffs = [marks[j] - marks[i] for i in range(10) for j in range(i + 1, 10)]\n"
                      "    s.add(cz.Distinct(diffs))\n"
                      "    return s, {'x': x, 'y': y}, ('minimize', x + y + marks[9])\n")
# The runner solves on fresh solvers; these check that it keeps the returned
# Solver's logic and options. A SolverFor("QF_LIA") Solver with an option set
# still gets the proven optimum.
LOGIC_SUBMISSION = ("import cvc5.pythonic as cz\n"
                    "def build(instance):\n"
                    "    n = instance['n']\n"
                    "    x, y = cz.Ints('x y')\n"
                    "    s = cz.SolverFor('QF_LIA')\n"
                    "    s.set('sat-random-seed', 7)\n"
                    "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y >= n)\n"
                    "    return s, {'x': x, 'y': y}, ('minimize', x + y)\n")
# x * y is nonlinear: accepted under the default logic, refused by cvc5 under QF_LIA.
NONLINEAR = ("import cvc5.pythonic as cz\n"
             "def build(instance):\n"
             "    n = instance['n']\n"
             "    x, y = cz.Ints('x y')\n"
             "    s = cz.SOLVER\n"
             "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y == n, x * y >= 0)\n"
             "    return s, {'x': x, 'y': y}\n")
# rlimit-per 1 stops the first check: only a copied option can give RESOURCEOUT.
RESOURCE_SUBMISSION = ("import cvc5.pythonic as cz\n"
                       "def build(instance):\n"
                       "    n = instance['n']\n"
                       "    x, y = cz.Ints('x y')\n"
                       "    marks = cz.Ints(' '.join('m%d' % i for i in range(10)))\n"
                       "    s = cz.Solver()\n"
                       "    s.set('rlimit-per', 1)\n"
                       "    s.add(x >= 0, x <= n, y >= 0, y <= n, x + y == n)\n"
                       "    s.add(marks[0] == 0)\n"
                       "    s.add([marks[i] < marks[i + 1] for i in range(9)])\n"
                       "    s.add(cz.Distinct([marks[j] - marks[i] for i in range(10) for j in range(i + 1, 10)]))\n"
                       "    return s, {'x': x, 'y': y}\n")
# The runner owns tlimit-per: a 1 ms value on the returned Solver must not end the run.
OWNED_SUBMISSION = GOOD.replace("    s = cz.Solver()\n",
                                "    s = cz.Solver()\n    s.set('tlimit-per', 1)\n"
                                "    s.set('incremental', False)\n")
PIGEONHOLE = ("import cvc5.pythonic as cz\n"
              "def build(instance):\n"
              "    xs = cz.Ints(' '.join('p%d' % i for i in range(14)))\n"
              "    s = cz.Solver()\n"
              "    s.add([x >= 0 for x in xs] + [x <= 12 for x in xs])\n"
              "    s.add(cz.Distinct(xs))\n"
              "    return s, {'p0': xs[0]}\n")


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
        # instance_shapes: extra keys, a string and ragged data are ignored by the
        # submission (it reads only `n`), on two instances of different shapes.
        check("instance_shapes", GOOD,
              instances=[{"n": 2, "optimize": False, "name": "a", "note": "b", "label": "s",
                          "ragged": [[1], [2, 3]]},
                         {"n": 3, "optimize": False, "name": "c", "note": "d", "label": "t",
                          "ragged": [[4, 5, 6]]}],
              instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

        # optimization_timeout: a proof that cannot finish in 3 s returns no solution
        check("optimization_timeout", TIMEOUT_SUBMISSION, expected={"execution_timeout"},
              execution_timeout=3)
        # optimization_timeout_unknown: a hard unsat-free instance still times out, never errors
        check("timeout_classification", PIGEONHOLE, expected={"execution_timeout"},
              execution_timeout=2, reference=REFERENCE)
        check("minimization_step_one", PROOF_SUBMISSION,
              reference=PROOF_REFERENCE, solution_limit=1)
        check("negative_offset_minimize", NEGATIVE_SUBMISSION.replace("DIRECTION", "minimize"),
              reference=NEGATIVE_REFERENCE.replace("DIRECTION", "minimize"))
        check("negative_offset_maximize", NEGATIVE_SUBMISSION.replace("DIRECTION", "maximize"),
              reference=NEGATIVE_REFERENCE.replace("DIRECTION", "maximize"))
        check("optimum_enumeration", OPTIMA_SUBMISSION, reference=OPTIMA_REFERENCE, solution_limit=3)
        check("output_shapes", NESTED_SUBMISSION, reference=NESTED_REFERENCE)
        check("bool_leaves", BOOL_SUBMISSION, reference=BOOL_REFERENCE)
        check("auxiliary_free_distinct", AUX_SUBMISSION, solution_limit=3)
        check("stray_stdout", STDOUT_SUBMISSION, reference=REFERENCE)
        check("large_model", LARGE_SUBMISSION, reference=LARGE_REFERENCE, execution_timeout=120)
        check("logic_and_option_kept", LOGIC_SUBMISSION, reference=OPTIMIZING, solution_limit=3)
        check("nonlinear_default_logic", NONLINEAR.replace("SOLVER", "Solver()"))
        logic = check("logic_honoured", NONLINEAR.replace("SOLVER", "SolverFor('QF_LIA')"),
                      expected={"execution_error"})
        results["logic_honoured"] = (results["logic_honoured"]
                                     and "non-linear term" in json.dumps(logic))
        resource = check("option_honoured", RESOURCE_SUBMISSION, expected={"execution_error"})
        results["option_honoured"] = (results["option_honoured"]
                                      and "RESOURCEOUT" in json.dumps(resource))
        check("runner_owned_options", OWNED_SUBMISSION, solution_limit=3)
        error = check("error_detail", ERROR_SUBMISSION, expected={"execution_error"})
        results["error_detail"] = (not error["accepted"] and error["reason"] == "execution_error"
                                   and "invalid argument" in json.dumps(error))

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
