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

`native_api` guards the mistake this integration was rebuilt to fix:
submissions are written against PySAT itself, not a modelling layer shipped
beside the runner.
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

HEAD = '''from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
'''
EXPORT = '    return engine.clausify(), {"x": x, "y": y}\n'

GOOD = HEAD + "    engine.add_linear(x + y == n)\n" + EXPORT
# Declaring an objective is the one thing this integration refuses outright.
OPTIMIZED = (HEAD + "    engine.add_linear(x + y >= n)\n"
             '    return engine.clausify(), {"x": x, "y": y}, ("minimize", x)\n')
# Solves, then corrupts the protocol stream the runner owns.
MALFORMED = (HEAD + "    engine.add_linear(x + y == n)\n"
             "    import os\n"
             "    os.write(1, b'this is not a protocol record\\n')\n" + EXPORT)
UNSATISFIABLE = (HEAD + "    engine.add_linear(x == 0)\n"
                 "    engine.add_linear(x == 1)\n" + EXPORT)
# A pigeonhole big enough that the SAT solver cannot refute it in two seconds.
SLOW = (HEAD + "    engine.add_linear(x + y == n)\n"
        '    birds = [Integer(f"b{i}", 1, 12, vpool=pool) for i in range(13)]\n'
        "    for bird in birds:\n"
        "        engine.add_var(bird)\n"
        "    engine.add_alldifferent(birds)\n" + EXPORT)

ISOLATED = '''from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


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
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    engine.add_linear(x + y == n)
    return engine.clausify(), {"x": x, "y": y}
'''

# The image must carry PySAT itself and nothing standing in for it.
NATIVE = '''import pysat
from pysat.card import CardEnc
from pysat.formula import CNF, IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    # The encoders a submission builds clauses with, all from the framework.
    assert CardEnc.__module__.startswith("pysat."), CardEnc.__module__
    assert PBEnc.__module__.startswith("pysat."), PBEnc.__module__
    for absent in ("dcp_sat", "dcp_maxsat", "dcp_pb"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass

    n = instance["n"]
    pool = IDPool()
    x = Integer("x", 0, n, vpool=pool)
    y = Integer("y", 0, n, vpool=pool)
    engine = IntegerEngine(vars=[x, y], vpool=pool)
    engine.add_linear(x + y == n)
    formula = engine.clausify()
    assert isinstance(formula, CNF), type(formula).__name__
    return formula, {"x": x, "y": y}
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
        check("native_api", NATIVE)
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
