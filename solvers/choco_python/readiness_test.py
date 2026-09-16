"""Readiness checks for the choco_python integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver choco_python` runs this and keeps
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

SOLVER = "choco_python"

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

GOOD = ("from pychoco.model import Model\n"
        "def build(instance):\n"
        "    n = instance['n']\n"
        "    model = Model()\n"
        "    x = model.intvar(0, n, name='x')\n"
        "    y = model.intvar(0, n, name='y')\n"
        "    model.arithm(x, '+', y, '=', n).post()\n"
        "    return model, {'x': x, 'y': y}\n")
OPTIMAL = ("from pychoco.model import Model\n"
           "def build(instance):\n"
           "    n = instance['n']\n"
           "    model = Model()\n"
           "    x = model.intvar(0, n, name='x')\n"
           "    y = model.intvar(0, n, name='y')\n"
           "    total = model.intvar(0, 2 * n, name='total')\n"
           "    model.arithm(x, '+', y, '>=', n).post()\n"
           "    model.scalar([x, y], [1, 1], '=', total).post()\n"
           "    return model, {'x': x, 'y': y}, ('DIRECTION', total)\n")
# Two distinct solutions that share their declared outputs: the runner must
# report one of them, not two, because enumeration counts declared outputs.
DUPLICATES = ("from pychoco.model import Model\n"
              "def build(instance):\n"
              "    n = instance['n']\n"
              "    model = Model()\n"
              "    x = model.intvar(0, n, name='x')\n"
              "    y = model.intvar(0, n, name='y')\n"
              "    hidden = model.intvar(0, 5, name='hidden')\n"
              "    model.arithm(x, '+', y, '=', n).post()\n"
              "    return model, {'x': x, 'y': y}\n")
MALFORMED = "def build(instance):\n    return None, {}\n"
UNSATISFIABLE = ("from pychoco.model import Model\n"
                 "def build(instance):\n"
                 "    model = Model()\n"
                 "    x = model.intvar(0, 1, name='x')\n"
                 "    model.arithm(x, '<', 0).post()\n"
                 "    return model, {'x': x, 'y': 2}\n")
SLOW = "import time\ndef build(instance):\n    time.sleep(120)\n"
ISOLATED = ("import os, socket\n"
            "from pychoco.model import Model\n"
            "def build(instance):\n"
            "    assert os.getuid() != 0, 'container runs as root'\n"
            "    assert sorted(os.listdir('/input')) == ['model.py', 'request.json'], 'unexpected /input'\n"
            "    assert not os.path.exists('/dataset'), 'dataset is visible to the candidate'\n"
            "    probe = socket.socket()\n"
            "    probe.settimeout(0.5)\n"
            "    assert probe.connect_ex(('1.1.1.1', 443)) != 0, 'network reachable'\n"
            "    n = instance['n']\n"
            "    model = Model()\n"
            "    x = model.intvar(0, n, name='x')\n"
            "    y = model.intvar(0, n, name='y')\n"
            "    model.arithm(x, '+', y, '=', n).post()\n"
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
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

        # Enumeration has to do two things: return the distinct solutions asked
        # for, and stop at exhaustion rather than inventing repeats. x+y==2 over
        # 0..2 has exactly three, so asking for three is accepted and asking for
        # ten is accepted with only three checked.
        exact = check("enumeration_exact", GOOD, solution_limit=3)
        beyond = check("enumeration_exhausted", DUPLICATES, solution_limit=10)
        results["enumeration"] = (
            exact["accepted"] and exact["solutions_checked"] == 3
            and beyond["accepted"] and beyond["solutions_checked"] == 3
        )
        del results["enumeration_exact"], results["enumeration_exhausted"]

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
