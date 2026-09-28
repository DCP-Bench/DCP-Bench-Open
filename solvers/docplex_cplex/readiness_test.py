"""Readiness checks for the docplex_cplex integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver docplex_cplex` runs this and
keeps its output as the readiness evidence.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "docplex_cplex"

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

# A strongly correlated knapsack on which CPLEX's default relative gap (1e-4)
# stops at 12168379 with status 102, "integer optimal, tolerance"; the optimum
# is 12168772. Measured with CPLEX 22.2.0.0, one thread. A runner that left the
# gap at its default would hand the evaluator that suboptimal solution.
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

HEADER = ("from docplex.mp.model import Model\n\n\n"
          "def build(instance):\n    n = instance['n']\n    model = Model()\n")
BOUNDED = ("    x = model.integer_var(0, n, name='x')\n"
           "    y = model.integer_var(0, n, name='y')\n")
GOOD = HEADER + BOUNDED + ("    model.add_constraint(x + y == n)\n"
                           "    return model, {'x': x, 'y': y}\n")
OPTIMAL = HEADER + BOUNDED + ("    model.add_constraint(x + y >= n)\n"
                              "    model.SENSE(x + y)\n"
                              "    return model, {'x': x, 'y': y}\n")
# Integer outputs with no upper bound, so the no-good cannot lean on one.
UNBOUNDED = HEADER + ("    x = model.integer_var(0, model.infinity, name='x')\n"
                      "    y = model.integer_var(0, model.infinity, name='y')\n"
                      "    model.add_constraint(x + y == n)\n"
                      "    return model, {'x': x, 'y': y}\n")
# Outputs that are expressions rather than variables: a monomial and a sum with
# a constant, which docplex represents as two different classes.
EXPRESSION = HEADER + ("    x = model.integer_var(0, n, name='x')\n"
                       "    return model, {'x': 1 * x, 'y': n - x}\n")
KNAPSACK_MODEL = """from docplex.mp.model import Model


def build(instance):
    weights, values = instance["weights"], instance["values"]
    model = Model()
    x = model.binary_var_list(len(weights), name="x")
    model.add_constraint(model.sum(w * x[i] for i, w in enumerate(weights)) <= instance["capacity"])
    model.maximize(model.sum(v * x[i] for i, v in enumerate(values)))
    return model, {"x": x}
"""
# The submission writes to file descriptor 1 and to Python's stdout; neither may
# reach the protocol stream.
NOISY = HEADER.replace("    model = Model()\n",
                       "    import os\n    os.write(1, b'noise on fd 1\\n')\n    print('noise')\n"
                       "    model = Model()\n") + BOUNDED + (
    "    model.add_constraint(x + y == n)\n"
    "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = HEADER + BOUNDED + ("    model.add_constraint(x >= n + 1)\n"
                                    "    return model, {'x': x, 'y': y}\n")
SLOW = "import time\n\n\ndef build(instance):\n    time.sleep(120)\n"
# A declared output that is not integral must be refused rather than rounded.
FRACTIONAL = HEADER + BOUNDED + ("    half = model.continuous_var(0, 1, name='half')\n"
                                 "    model.add_constraint(x + y == n)\n"
                                 "    model.add_constraint(half == 0.5)\n"
                                 "    return model, {'x': x, 'y': half}\n")
# A market-split instance (Cornuejols and Dawande): hard enough that CPLEX
# cannot prove the optimum within a few seconds, so the runner must not report one.
UNPROVEN = HEADER + BOUNDED + (
    "    import random\n"
    "    random.seed(1)\n"
    "    rows = [[random.randint(0, 99) for _ in range(60)] for _ in range(6)]\n"
    "    picks = model.binary_var_list(60)\n"
    "    slack = model.continuous_var_list(12)\n"
    "    for r, row in enumerate(rows):\n"
    "        model.add_constraint(model.sum(a * picks[j] for j, a in enumerate(row))"
    " + slack[2 * r] - slack[2 * r + 1] == sum(row) // 2)\n"
    "    model.add_constraint(x + y == n)\n"
    "    model.minimize(model.sum(slack))\n"
    "    return model, {'x': x, 'y': y}\n")
# 1001 variables: one more than the Community Edition allows.
OVERSIZED = HEADER + BOUNDED + ("    extra = model.binary_var_list(999)\n"
                                "    model.add_constraint(x + y + model.sum(extra) == n)\n"
                                "    return model, {'x': x, 'y': y}\n")
ISOLATED = HEADER + ("    import os, socket\n"
                     "    assert os.getuid() != 0, 'container runs as root'\n"
                     "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
                     "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
                     "    probe = socket.socket()\n"
                     "    probe.settimeout(0.5)\n"
                     "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n") + BOUNDED + (
    "    model.add_constraint(x + y == n)\n"
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
        check("library_stdout", NOISY)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("fractional_output", FRACTIONAL, expected={"execution_error", "invalid_output"})
        check("unproven_optimum", UNPROVEN, expected={"execution_timeout"}, execution_timeout=5)
        oversized = check("size_limit", OVERSIZED, expected={"unsupported_capability"})
        results["size_limit"] = results["size_limit"] and "Community Edition" in oversized.get("detail", "")
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
