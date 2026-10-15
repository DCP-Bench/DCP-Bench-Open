"""Readiness checks for the Paramita (Python) integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver paramita_python` runs this and
keeps its output as the readiness evidence.

Satisfaction and optimisation follow the contract in run.py: `build` returns
`(subject_to, outputs)` or `(subject_to, outputs, objective)`. `minimization`
and `maximization` check that the optimum the runner proves is the one the
reference computes, in both directions; `optimal_enumeration` that every
enumerated answer is optimal; `suboptimal_rejected` that the evaluator still
catches a model that optimises the wrong direction; `optimization_timeout` that
an EvalMaxSAT search stopped at the budget ends as a timeout, never as an answer.
`wide_output_rejected` checks that a total beyond 32 bits, which wraps, is not
accepted as an answer. `rejects_bad_objective` checks that an objective which is not a linear integer
expression is refused rather than ignored. `stray_stdout` checks that the
`c ...` lines EvalMaxSAT writes to standard output do not break the protocol.

`native_api` guards against a modelling layer shipped beside the runner:
submissions are written against paramita itself.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "paramita_python"

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

# x and y as unary sums of Bools, each with an order constraint so that the
# Bools form a unary number. Every candidate below starts from this prelude.
PRELUDE = '''from paramita.modelling import Bool


def unary(prefix, n):
    bits = [Bool(f"{prefix}{i}") for i in range(n)]
    order = [~bits[i + 1] | bits[i] for i in range(n - 1)]
    return sum(bits), order


def build(instance):
    n = instance["n"]
    x, order_x = unary("x", n)
    y, order_y = unary("y", n)
    subject = order_x + order_y
'''
OUTPUTS = '    outputs = {"x": x, "y": y}\n'

GOOD = PRELUDE + "    subject.append(x + y == n)\n" + OUTPUTS + "    return subject, outputs\n"
# x + y >= n, minimised or maximised. The objective is a linear integer
# expression, and the runner maps each direction onto the MaxSAT solver.
MINIMIZING_MODEL = (PRELUDE + "    subject.append(x + y >= n)\n" + OUTPUTS
                    + '    return subject, outputs, ("minimize", x + y)\n')
MAXIMIZING_MODEL = MINIMIZING_MODEL.replace('("minimize", x + y)', '("maximize", x + y)')
# An objective that is a Boolean rather than an integer expression, which the
# runner must refuse.
BAD_OBJECTIVE = (PRELUDE + "    subject.append(x + y >= n)\n" + OUTPUTS
                 + '    return subject, outputs, ("minimize", x == 1)\n')
# A pigeonhole of 18 pigeons in 17 holes, under the same unary x and y. It is
# unsatisfiable and, unlike 13 in 12, too hard for CaDiCaL to refute in two
# seconds, so the search is stopped at the budget.
PIGEONHOLE = '''
    holes = [[Bool(f"p{i}_{j}") for j in range(17)] for i in range(18)]
    for row in holes:
        subject.append(sum(row) >= 1)
    for j in range(17):
        subject.append(sum(holes[i][j] for i in range(18)) <= 1)
'''
SLOW = PRELUDE + "    subject.append(x + y == n)\n" + PIGEONHOLE + OUTPUTS + "    return subject, outputs\n"
SLOW_OPTIMAL = (PRELUDE + "    subject.append(x + y >= n)\n" + PIGEONHOLE + OUTPUTS
                + '    return subject, outputs, ("minimize", x + y)\n')
# Contradictory hard units. The runner encodes them into the MaxSAT path, where
# EvalMaxSAT writes a `c ...` line to standard output while it loads them.
CONTRADICTION = (PRELUDE + "    a = Bool(\"a\")\n    subject.extend([a, ~a])\n"
                 + "    subject.append(x + y >= n)\n" + OUTPUTS
                 + '    return subject, outputs, ("minimize", x + y)\n')
# A candidate that returns an output the runner cannot read.
MALFORMED = PRELUDE + "    subject.append(x + y == n)\n" + '    outputs = {"x": "not an expression", "y": y}\n    return subject, outputs\n'
# One weighted PB equality over 2000 Bools besides x + y == n. The default
# encoder recurses once per term and overflowed the default stack (signal 11)
# until the runner raised its stack limit.
LARGE_PB = (PRELUDE + "    subject.append(x + y == n)\n"
            "    many = [Bool(f\"m{i}\") for i in range(2000)]\n"
            "    subject.append(sum((1 + i % 10) * b for i, b in enumerate(many)) == 1000)\n"
            + OUTPUTS + "    return subject, outputs\n")
UNSATISFIABLE = PRELUDE + "    subject.extend([x == 0, x == 1])\n" + OUTPUTS + "    return subject, outputs\n"

# Paramita integers are 32 bits wide, and a value beyond that wraps around. This
# candidate forces a total of at least 2**31 from two groups of 31 Bools, so the
# runner reads a wrapped value. The reference asks for 2**33 + n, which is not
# that value, so the evaluator must reject the output rather than accept it.
WIDE_REFERENCE = '''
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2 ** 34, name="x")
model = cp.Model(x == 2 ** 33 + n)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
'''
WIDE = '''from paramita.modelling import Bool


def build(instance):
    low = [Bool(f"a{k}") for k in range(31)]
    high = [Bool(f"c{k}") for k in range(31)]
    total = sum(bit * 2 ** k for k, bit in enumerate(low)) + sum(bit * 2 ** k for k, bit in enumerate(high))
    return [low[30], high[30]], {"x": total}
'''
# Two assignments with the same declared total: the runner must report it once.
REPEAT_REFERENCE = '''
# Data
n = 1
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, name="x")
model = cp.Model(x == n)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
'''
REPEAT = '''from paramita.modelling import Bool


def build(instance):
    a = Bool("a")
    b = Bool("b")
    return [a + b == instance["n"]], {"x": a + b}
'''

ISOLATED = '''from paramita.modelling import Bool


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
    x = sum(Bool(f"x{i}") for i in range(n))
    y = sum(Bool(f"y{i}") for i in range(n))
    return [x + y == n], {"x": x, "y": y}
'''

# The image must carry paramita itself and nothing standing in for it.
NATIVE = '''import paramita
from paramita.modelling import Bool
from paramita.solvers import SatSolver


def build(instance):
    # The classes a submission builds with, all from the framework.
    assert Bool.__module__.startswith("paramita"), Bool.__module__
    assert SatSolver.__module__.startswith("paramita"), SatSolver.__module__
    for absent in ("dcp_sat", "dcp_maxsat", "dcp_pb"):
        try:
            __import__(absent)
            raise AssertionError(f"{absent} is still installed in the image")
        except ImportError:
            pass

    n = instance["n"]
    x = sum(Bool(f"x{i}") for i in range(n))
    y = sum(Bool(f"y{i}") for i in range(n))
    return [x + y == n], {"x": x, "y": y}
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
        check("minimization", MINIMIZING_MODEL, reference=OPTIMIZING)
        check("maximization", MAXIMIZING_MODEL, reference=MAXIMIZING)
        check("optimal_enumeration", MINIMIZING_MODEL, reference=OPTIMIZING, solution_limit=3)
        check("suboptimal_rejected", MAXIMIZING_MODEL, reference=OPTIMIZING,
              expected={"suboptimal_solution"})
        check("rejects_bad_objective", BAD_OBJECTIVE, reference=OPTIMIZING,
              expected={"execution_error", "invalid_output"})
        check("optimization_timeout", SLOW_OPTIMAL, reference=OPTIMIZING,
              expected={"execution_timeout"}, execution_timeout=2)
        check("stray_stdout", CONTRADICTION, reference=OPTIMIZING, expected={"no_solution"})
        check("native_api", NATIVE)
        check("wide_output_rejected", WIDE, reference=WIDE_REFERENCE,
              expected={"invalid_output", "invalid_solution", "no_solution"})
        repeat = check("repeated_output_once", REPEAT, reference=REPEAT_REFERENCE, solution_limit=2)
        results["repeated_output_once"] = (repeat["accepted"] and repeat["solutions_checked"] == 1)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("large_pb_constraint", LARGE_PB, execution_timeout=120)
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
