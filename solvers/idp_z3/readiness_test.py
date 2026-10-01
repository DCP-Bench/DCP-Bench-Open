"""Readiness checks for the idp_z3 integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver idp_z3` runs this and keeps its
output as the readiness evidence.

A submission here is an FO(.) knowledge base, not a program, so the slow
fixture cannot sleep: it is a nonlinear integer theory z3 cannot decide, which
runs until the solver's own budget expires. The container sandbox itself is
the evaluator's and is the same for every integration; `isolation` here checks
the property specific to this one, that a submission cannot execute code.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "idp_z3"

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

GOOD = """vocabulary {
    type V := {0..${n}}
    n: () -> Int
    x: () -> V
    y: () -> V
}
theory {
    x() + y() = n().
}
"""
OPTIMAL = """vocabulary {
    type V := {0..${n}}
    n: () -> Int
    x: () -> V
    y: () -> V
    DIRECTION: () -> Int
}
theory {
    x() + y() >= n().
    DIRECTION() = x() + y().
}
"""
MALFORMED = "this is not FO(.) {{{\n"
UNSATISFIABLE = """vocabulary {
    type V := {0..${n}}
    n: () -> Int
    x: () -> V
    y: () -> V
}
theory {
    x() + y() > 2 * n().
}
"""
SLOW = """vocabulary {
    x: () -> Int
    y: () -> Int
    z: () -> Int
}
theory {
    x() * x() * x() + y() * y() * y() + z() * z() * z() = 33.
}
"""
# A knowledge base cannot probe the container the way a program can; the code it
# could carry is a `procedure` block, which IDP-Z3 runs only on an explicit
# IDP.execute(). The runner never calls it, so this procedure must not run: if it
# did, its line on stdout would break the JSONL protocol and fail the check.
# (Procedure strings take no escapes, so it cannot print a JSON record anyway.)
ISOLATED = GOOD + """
procedure main() {
    print("PROCEDURE EXECUTED")
}
"""


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.idp", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
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
