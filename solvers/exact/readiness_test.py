"""Readiness checks for the exact integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver exact` runs this and keeps its
output as the readiness evidence.

The optimisation checks carry the weight here. `toOptimum` answers `"SAT"` when
it proved the optimum and `"TIMEOUT"` when it stopped short, and in the second
case Exact still has a solution in hand: `hasSolution()` is true either way. So
a runner that read the solution without reading the status would hand the
evaluator an unproven answer to compare against the reference optimum.
`timeout_cleanup` below is the check that a search which cannot finish is
reported as a timeout rather than answered.
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

HEAD = '''from dcp_pb import Pb


def build(instance):
    n = instance["n"]
    pb = Pb()
    x = pb.int(0, n)
    y = pb.int(0, n)
'''
EXPORT = '    return pb, {"x": x, "y": y}\n'

GOOD = HEAD + "    pb.sum_eq([x, y], n)\n" + EXPORT
# `n` is a maximum here, so the objective has room to move in both directions.
OPTIMAL = (HEAD + "    pb.sum_ge([x, y], n)\n"
           "    pb.DIRECTION([(1, x), (1, y)])\n" + EXPORT)
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + "    pb.sum_eq([x, y], n)\n"
             "    import os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = (HEAD + "    pb.eq([(1, x)], 0)\n    pb.eq([(1, x)], 1)\n" + EXPORT)
# Exact is strong enough that pigeonhole is no obstacle to it, so the slow case
# is a knapsack big enough that proving the optimum takes about 25 seconds.
# The numbers are generated from a fixed seed rather than written out.
SLOW = (HEAD + "    pb.sum_eq([x, y], n)\n"
        "    import random\n"
        "    random.seed(7)\n"
        "    size = 200\n"
        "    weights = [random.randint(10000000, 99999999) for _ in range(size)]\n"
        "    values = [random.randint(10000000, 99999999) for _ in range(size)]\n"
        "    picks = pb.bools(size)\n"
        "    pb.weighted_sum_le(weights, picks, sum(weights) // 2)\n"
        "    pb.maximise(list(zip(values, picks)))\n" + EXPORT)

ISOLATED = '''from dcp_pb import Pb


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
    pb = Pb()
    x = pb.int(0, n)
    y = pb.int(0, n)
    pb.sum_eq([x, y], n)
    return pb, {"x": x, "y": y}
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
        check("minimization", OPTIMAL.replace("DIRECTION", "minimise"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximise"), reference=MAXIMIZING)
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
