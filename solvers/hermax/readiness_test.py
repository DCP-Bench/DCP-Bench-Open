"""Readiness checks for the hermax integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver hermax` runs this and keeps its
output as the readiness evidence.

The optimisation checks are the ones that matter here. A MaxSAT solver reaches
an answer long before it proves that answer best, and hermax reports the
difference through the solve status: `optimum` against `interrupted_sat`. The
runner emits a solution only on the former, so minimization and maximization
below are really checking that the objective the reference computes is the one
this integration reaches, in both directions.

`native_api` and `rejects_objective_tuple` guard the mistake this integration
was rebuilt to fix: submissions have to be written against `hermax.model`, and
the objective belongs on `model.obj` rather than in the value returned.

`memory_limit` checks that a solver worker killed at the memory limit ends as
`memory_limit`, not as a solver error blamed on the model: hermax solves in a
subprocess and reports that subprocess's death as a bare `error` status.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "hermax"

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

HEAD = '''from hermax.model import Model


def build(instance):
    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
'''
EXPORT = '    return m, {"x": x, "y": y}\n'

GOOD = HEAD + "    m &= (x + y == n)\n" + EXPORT
# `n` is a maximum here, so the objective has room to move in both directions.
OPTIMAL = HEAD + "    m &= (x + y >= n)\n    m.obj += OBJECTIVE\n" + EXPORT
# The contract this integration used before it was rebuilt on hermax.model. It
# has to fail loudly rather than be silently ignored.
OBJECTIVE_TUPLE = (HEAD + "    m &= (x + y >= n)\n"
                   '    return m, {"x": x, "y": y}, ("minimize", x + y)\n')
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + "    m &= (x + y == n)\n"
             "    import os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = HEAD + "    m &= (x == 0)\n    m &= (x == 1)\n" + EXPORT
# A pigeonhole big enough that the solver cannot refute it in two seconds.
# EvalMaxSAT is much faster at this than the SAT integration's Glucose: it
# refutes 13 into 12 in under a second, where 16 into 15 runs past a minute.
SLOW = (HEAD + "    m &= (x + y == n)\n"
        '    birds = m.int_vector("birds", 16, 1, 15)\n'
        "    m &= birds.all_different()\n" + EXPORT)

# A thousand distinctly weighted soft units under a cardinality bound. RC2
# stratifies on the weights and builds totalizers until its worker passes a
# 256 MB limit, about two seconds in, while the runner itself stays well under.
HUNGRY = (HEAD + "    m &= (x + y == n)\n"
          '    b = m.bool_vector("b", 1000)\n'
          "    m &= (sum(b[i] for i in range(1000)) <= 500)\n"
          "    for i in range(1000):\n"
          "        m.obj[i + 1] += b[i]\n" + EXPORT)

ISOLATED = '''from hermax.model import Model


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
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    m &= (x + y == n)
    return m, {"x": x, "y": y}
'''

# The image must carry the framework itself and nothing standing in for it.
NATIVE = '''import hermax
from hermax.model import BoolVector, IntVector, Model


def build(instance):
    assert hermax.__version__ == "1.2.5", hermax.__version__
    # The modelling layer the submissions are written against, not a wrapper
    # shipped alongside the runner.
    assert Model.__module__.startswith("hermax."), Model.__module__
    for absent in ("dcp_maxsat", "dcp_sat", "dcp_pb"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass
    probe = Model()
    assert isinstance(probe.int_vector("probe", 2, 0, 1), IntVector)
    assert isinstance(probe.bool_vector("flags", 2), BoolVector)

    n = instance["n"]
    m = Model()
    x = m.int("x", 0, n)
    y = m.int("y", 0, n)
    m &= (x + y == n)
    return m, {"x": x, "y": y}
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
        check("minimization", OPTIMAL.replace("OBJECTIVE", "x + y"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "(2 * n) - (x + y)"),
              reference=MAXIMIZING)
        check("native_api", NATIVE)
        check("isolation", ISOLATED)
        check("rejects_objective_tuple", OBJECTIVE_TUPLE,
              reference=OPTIMIZING, expected={"execution_error", "invalid_output"})
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        # hermax reports a worker the kernel killed for memory as a plain solver
        # error; the evaluator has to see through that to the memory limit.
        check("memory_limit", HUNGRY, expected={"memory_limit"}, memory_mb=256)

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
