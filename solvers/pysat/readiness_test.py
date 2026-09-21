"""Readiness checks for the pysat integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver pysat` runs this and keeps its
output as the readiness evidence.

This integration declares `optimization: false`, so the required set swaps
minimization and maximization for `unsupported_optimization`. That check matters
more here than the name suggests: the evaluator does not consult the metadata
flag, so if the runner quietly ignored an objective, a merely feasible answer
could be reported as if it were optimal. The runner refuses instead, and this
proves the refusal reaches the evaluator as `unsupported_capability`.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "pysat"

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

HEAD = '''from dcp_sat import Sat


def build(instance):
    n = instance["n"]
    sat = Sat()
    x = sat.int(0, n)
    y = sat.int(0, n)
'''
EXPORT = '    return sat, {"x": x, "y": y}\n'

GOOD = HEAD + "    sat.sum_eq([x, y], n)\n" + EXPORT
# Declaring an objective is the one thing this integration refuses outright.
OPTIMIZED = (HEAD + "    sat.sum_ge([x, y], n)\n"
             '    return sat, {"x": x, "y": y}, ("minimize", x)\n')
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + "    sat.sum_eq([x, y], n)\n"
             "    import sys, os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = (HEAD + "    sat.linear_eq([(1, x)], 0)\n"
                 "    sat.linear_eq([(1, x)], 1)\n" + EXPORT)
# A pigeonhole big enough that the SAT solver cannot refute it in two seconds.
SLOW = (HEAD + "    sat.sum_eq([x, y], n)\n"
        "    birds = sat.ints(13, 1, 12)\n"
        "    sat.all_different(birds)\n" + EXPORT)

ISOLATED = '''from dcp_sat import Sat


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
    sat = Sat()
    x = sat.int(0, n)
    y = sat.int(0, n)
    sat.sum_eq([x, y], n)
    return sat, {"x": x, "y": y}
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
        check("unsupported_optimization", OPTIMIZED, reference=OPTIMIZING,
              expected={"unsupported_capability"})
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
