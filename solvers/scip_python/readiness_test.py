"""Readiness checks for the scip_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver scip_python` runs this and keeps
its output as the readiness evidence.

Candidates are pyscipopt modules with `build(instance)`. The crash and exit checks
use the three ways the worker can die without a status: a SIGSEGV from an
indicator constraint without a binary, a SIGABRT, and a sys.exit.
The isolation check drives the image directly under the evaluator's container
flags instead of through a submission.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "scip_python"

# A tiny trusted reference, kept here so this script does not depend on the
# test suite. n=2 gives x+y==2 exactly three solutions, and x+y>=2 under
# minimization exactly three optima.
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

# A strongly correlated knapsack on which a solver with a relative gap of 1e-4
# stops short of the optimum 12168772. The runner must not report that solution.
KNAPSACK_DATA = '''weights = [647339, 534286, 945876, 418162, 483384, 403694, 283173, 903321, 839395, 838428, 666425, 793510, 391794, 215513, 128245, 360993, 502832, 954784, 882652, 539947, 364643, 625968, 941350, 432854, 771638, 987439, 817681, 859454, 521098, 244222, 677958, 165213, 246676, 952082, 930078, 306113, 258246, 839842, 658741, 686040]
values = [650779, 539709, 954722, 420185, 484517, 408759, 289885, 904662, 847706, 846195, 676254, 795830, 398489, 223804, 133756, 361285, 509922, 960882, 892018, 540793, 370453, 626792, 949169, 438995, 781141, 987523, 824324, 863368, 523016, 253344, 681461, 169285, 255309, 957975, 931030, 310490, 259298, 844355, 661898, 695934]
capacity = 12010544
'''
KNAPSACK = f'''
# Data
{KNAPSACK_DATA}# End of data
import cpmpy as cp
import json
x = cp.boolvar(shape=len(weights), name="x")
model = cp.Model(cp.sum(x * weights) <= capacity)
model.maximize(cp.sum(x * values))
model.solve()
solution = {{"x": x.value().tolist()}}
print(json.dumps(solution))
'''

HEADER = ("from pyscipopt import Model, quicksum\n\n\n"
          "def build(instance):\n    n = instance['n']\n    model = Model()\n")
BOUNDED = ("    x = model.addVar(name='x', vtype='I', lb=0, ub=n)\n"
           "    y = model.addVar(name='y', vtype='I', lb=0, ub=n)\n")
GOOD = HEADER + BOUNDED + ("    model.addCons(x + y == n)\n"
                           "    return model, {'x': x, 'y': y}\n")
OPTIMAL = HEADER + BOUNDED + ("    model.addCons(x + y >= n)\n"
                              "    model.setObjective(x + y, 'SENSE')\n"
                              "    return model, {'x': x, 'y': y}\n")
# Integer outputs with no upper bound, so the no-good cannot lean on one.
UNBOUNDED = HEADER + ("    x = model.addVar(name='x', vtype='I', lb=0)\n"
                      "    y = model.addVar(name='y', vtype='I', lb=0)\n"
                      "    model.addCons(x + y == n)\n"
                      "    return model, {'x': x, 'y': y}\n")
# A declared output that is an expression rather than a variable.
EXPRESSION = HEADER + ("    x = model.addVar(name='x', vtype='I', lb=0, ub=n)\n"
                       "    return model, {'x': x, 'y': n - x}\n")
KNAPSACK_MODEL = f'''from pyscipopt import Model, quicksum


def build(instance):
    weights, values = instance["weights"], instance["values"]
    model = Model()
    x = [model.addVar(name=f"x{{i}}", vtype="B") for i in range(len(weights))]
    model.addCons(quicksum(w * x[i] for i, w in enumerate(weights)) <= instance["capacity"])
    model.setObjective(quicksum(v * x[i] for i, v in enumerate(values)), "maximize")
    return model, {{"x": x}}
'''
# Rows of different lengths: the model reads the last item of every row.
RAGGED_MODEL = ("from pyscipopt import Model\n\n\n"
                "def build(instance):\n    rows = instance['rows']\n    model = Model()\n"
                "    x = model.addVar(name='x', vtype='I', lb=0, ub=100)\n"
                "    model.addCons(x == sum(row[-1] for row in rows))\n"
                "    return model, {'x': x}\n")
RAGGED_REFERENCE = """
# Data
rows = [[1, 2, 3], [4], [5, 6]]
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 100, name="x")
model = cp.Model(x == sum(row[-1] for row in rows))
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
RAGGED_INSTANCES = [{"rows": [[1, 2, 3], [4], [5, 6]]}, {"rows": [[7], [8, 9]]}, {"rows": [[2, 2], [3]]}]
# Only the fields a model reads reach it, and a one-key instance is still an object.
ONE_KEY = HEADER + BOUNDED + "    model.addCons(x + y == n)\n    return model, {'x': x, 'y': y}\n"
ONE_KEY_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y == n)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
ONE_KEY_INSTANCES = [{"n": 3}, {"n": 4}]
# Metadata strings that no model reads must not reach the model or break it.
NAMED_REFERENCE = REFERENCE.replace("optimize = False", 'optimize = False\nname = "first"\nnote = "a"')
NAMED_INSTANCES = [{"n": 2, "optimize": False, "name": "first", "note": "a"},
                   {"n": 3, "optimize": False, "name": "second", "note": "b"}]
# A free auxiliary variable that no output depends on: distinct outputs must still come back.
AUXILIARY = HEADER + BOUNDED + ("    model.addCons(x + y == n)\n"
                                "    model.addVar(name='aux', vtype='I', lb=0, ub=5)\n"
                                "    return model, {'x': x, 'y': y}\n")
# General constraints: an AND over free binaries and an indicator with an explicit binary.
GENERAL = HEADER + BOUNDED + (
    "    p = model.addVar(name='p', vtype='B')\n"
    "    q = model.addVar(name='q', vtype='B')\n"
    "    both = model.addVar(name='both', vtype='B')\n"
    "    model.addConsAnd([p, q], both)\n"
    "    model.addCons(both == 1)\n"
    "    selector = model.addVar(name='selector', vtype='B')\n"
    "    model.addCons(x + y <= n)\n"
    "    model.addConsIndicator(x + y >= n, binvar=selector)\n"
    "    model.addCons(selector == 1)\n"
    "    return model, {'x': x, 'y': y}\n")
# The worker dies on an indicator without a binary (SIGSEGV in SCIP 10.0.2).
SEGFAULT = HEADER + BOUNDED + ("    model.addConsIndicator(x + y <= n)\n"
                               "    return model, {'x': x, 'y': y}\n")
ABORT = "import os\n\n\ndef build(instance):\n    os.abort()\n"
EXIT = "import sys\n\n\ndef build(instance):\n    sys.exit(3)\n"
# The library and the submission both write to file descriptor 1; neither may
# reach the protocol stream.
NOISY = HEADER.replace("    model = Model()\n",
                       "    import os\n    os.write(1, b'noise on fd 1\\n')\n    print('noise')\n"
                       "    model = Model()\n") + BOUNDED + (
    "    model.addCons(x + y == n)\n"
    "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = HEADER + BOUNDED + ("    model.addCons(x >= n + 1)\n"
                                    "    return model, {'x': x, 'y': y}\n")
SLOW = "import time\n\n\ndef build(instance):\n    time.sleep(120)\n"
# A declared output that is not integral must be refused rather than rounded.
FRACTIONAL = HEADER + BOUNDED + ("    half = model.addVar(name='half', vtype='C', lb=0, ub=1)\n"
                                 "    model.addCons(x + y == n)\n"
                                 "    model.addCons(half == 0.5)\n"
                                 "    return model, {'x': x, 'y': half}\n")
# A market-split instance (Cornuejols and Dawande): hard enough that SCIP cannot
# prove the optimum within a few seconds, so the runner must not report one.
UNPROVEN = HEADER + BOUNDED + (
    "    import random\n"
    "    random.seed(1)\n"
    "    rows = [[random.randint(0, 99) for _ in range(60)] for _ in range(6)]\n"
    "    picks = [model.addVar(name=f'p{j}', vtype='B') for j in range(60)]\n"
    "    slack = [[model.addVar(name=f's{r}_{k}', vtype='C', lb=0) for k in range(2)] for r in range(6)]\n"
    "    for r, row in enumerate(rows):\n"
    "        model.addCons(quicksum(a * picks[j] for j, a in enumerate(row))"
    " + slack[r][0] - slack[r][1] == sum(row) // 2)\n"
    "    model.addCons(x + y == n)\n"
    "    model.setObjective(quicksum(s for pair in slack for s in pair), 'minimize')\n"
    "    return model, {'x': x, 'y': y}\n")
ISOLATED = HEADER + ("    import os, socket\n"
                     "    assert os.getuid() != 0, 'container runs as root'\n"
                     "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
                     "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
                     "    probe = socket.socket()\n"
                     "    probe.settimeout(0.5)\n"
                     "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n") + BOUNDED + (
    "    model.addCons(x + y == n)\n"
    "    return model, {'x': x, 'y': y}\n")


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

        def detail_of(name, source, expected_text, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=REFERENCE, **kwargs)
            results[name] = result["reason"] == "execution_error" and expected_text in result.get("detail", "")
            return result

        def exhausts(name, result, count):
            first = result["instances"][0] if result["instances"] else {}
            results[name] = (results[name] and first.get("solutions_received") == count
                             and first.get("runner_status", {}).get("status") == "complete")

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back as
        # exhaustion rather than as a shortfall the evaluator would reject.
        exhausts("exhausted_enumeration", check("exhausted_enumeration", GOOD, solution_limit=5), 3)
        exhausts("unbounded_enumeration", check("unbounded_enumeration", UNBOUNDED, solution_limit=5), 3)
        check("minimization", OPTIMAL.replace("SENSE", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("SENSE", "maximize"), reference=MAXIMIZING)
        # Three optima; enumeration past them must stay at the optimum and then stop.
        exhausts("optimal_enumeration", check("optimal_enumeration", OPTIMAL.replace("SENSE", "minimize"),
                                              reference=OPTIMIZING, solution_limit=5), 3)
        check("proven_optimum", KNAPSACK_MODEL, reference=KNAPSACK)
        check("expression_output", EXPRESSION, solution_limit=2)
        check("general_constraints", GENERAL, solution_limit=3)
        check("auxiliary_free_distinct", AUXILIARY, solution_limit=2)
        check("library_stdout", NOISY)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("fractional_output", FRACTIONAL, expected={"execution_error", "invalid_output"})
        unproven = check("unproven_optimum", UNPROVEN, expected={"execution_timeout"}, execution_timeout=5)
        results["unproven_optimum"] &= not unproven.get("solutions_checked")
        detail_of("crash_reported", SEGFAULT, "SIGSEGV")
        detail_of("abort_reported", ABORT, "SIGABRT")
        detail_of("exit_reported", EXIT, "status 3")
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        named = check("metadata_fields_ignored", GOOD, reference=NAMED_REFERENCE,
                      instances=NAMED_INSTANCES, instance_count=2)
        results["metadata_fields_ignored"] &= named["instances_checked"] == 2
        one = check("one_key_instance", ONE_KEY, reference=ONE_KEY_REFERENCE,
                    instances=ONE_KEY_INSTANCES, instance_count=2)
        results["one_key_instance"] &= one["instances_checked"] == 2
        ragged = check("ragged_data", RAGGED_MODEL, reference=RAGGED_REFERENCE,
                       instances=RAGGED_INSTANCES, instance_count=3)
        results["ragged_data"] &= ragged["instances_checked"] == 3

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
