"""Readiness checks for the pulp_cbc integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver pulp_cbc` runs this and keeps its
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

SOLVER = "pulp_cbc"

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

HEADER = "import pulp\n\n\ndef build(instance):\n    n = instance['n']\n"
BOUNDED = ("    x = pulp.LpVariable('x', 0, n, cat='Integer')\n"
           "    y = pulp.LpVariable('y', 0, n, cat='Integer')\n")
GOOD = HEADER + ("    problem = pulp.LpProblem('good', pulp.LpMinimize)\n" + BOUNDED +
                 "    problem += x + y == n\n"
                 "    return problem, {'x': x, 'y': y}\n")
OPTIMAL = HEADER + ("    problem = pulp.LpProblem('optimal', pulp.SENSE)\n" + BOUNDED +
                    "    problem += x + y >= n\n"
                    "    problem += x + y\n"
                    "    return problem, {'x': x, 'y': y}\n")
# A declared output that is an expression rather than a variable. PuLP's
# LpAffineExpression is a dict subclass, so a runner that walks outputs naively
# serialises its coefficients instead of its value.
EXPRESSION = HEADER + ("    problem = pulp.LpProblem('expression', pulp.LpMinimize)\n"
                       "    x = pulp.LpVariable('x', 0, n, cat='Integer')\n"
                       "    return problem, {'x': x, 'y': n - x}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = HEADER + ("    problem = pulp.LpProblem('unsat', pulp.LpMinimize)\n" + BOUNDED +
                          "    problem += x >= n + 1\n"
                          "    return problem, {'x': x, 'y': y}\n")
SLOW = "import time\n\n\ndef build(instance):\n    time.sleep(120)\n"
# A declared output that is not integral must be refused rather than rounded.
FRACTIONAL = HEADER + ("    problem = pulp.LpProblem('fractional', pulp.LpMinimize)\n" + BOUNDED +
                       "    half = pulp.LpVariable('half', 0, 1, cat='Continuous')\n"
                       "    problem += x + y == n\n"
                       "    problem += half == 0.5\n"
                       "    return problem, {'x': x, 'y': half}\n")
# CBC reports status Optimal when it stops on the time limit. A runner that read
# status instead of sol_status would accept this unproven optimum.
UNPROVEN = HEADER + ("    import random\n"
                     "    problem = pulp.LpProblem('unproven', pulp.LpMaximize)\n" + BOUNDED +
                     "    problem += x + y == n\n"
                     "    random.seed(1)\n"
                     "    weights = [random.randint(10 ** 6, 4 * 10 ** 6) for _ in range(150)]\n"
                     "    picks = [pulp.LpVariable(f'b{i}', cat='Binary') for i in range(150)]\n"
                     "    load = pulp.lpSum(w * b for w, b in zip(weights, picks))\n"
                     "    problem += load <= sum(weights) // 2\n"
                     "    problem += load\n"
                     "    return problem, {'x': x, 'y': y}\n")
ISOLATED = HEADER + ("    import os, socket\n"
                     "    assert os.getuid() != 0, 'container runs as root'\n"
                     "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
                     "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
                     "    probe = socket.socket()\n"
                     "    probe.settimeout(0.5)\n"
                     "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
                     "    problem = pulp.LpProblem('isolated', pulp.LpMinimize)\n" + BOUNDED +
                     "    problem += x + y == n\n"
                     "    return problem, {'x': x, 'y': y}\n")


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
        check("minimization", OPTIMAL.replace("SENSE", "LpMinimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("SENSE", "LpMaximize"), reference=MAXIMIZING)
        check("expression_output", EXPRESSION, solution_limit=2)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("fractional_output", FRACTIONAL, expected={"execution_error", "invalid_output"})
        check("unproven_optimum", UNPROVEN, expected={"execution_timeout"}, execution_timeout=5)
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
