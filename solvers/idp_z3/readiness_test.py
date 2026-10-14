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
# A placeholder takes an integer expression over the instance; here 2*k sizes a
# type, and the reference below computes the same solutions for k=2 and k=3.
REFERENCE_SIZE = '''
# Data
k = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2 * k, name="x")
y = cp.intvar(0, 2 * k, name="y")
model = cp.Model(x + y == 2 * k)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
SIZE_EXPRESSION = """vocabulary {
    k: () -> Int
    type V := {0..${2*k}}
    x: () -> V
    y: () -> V
}
theory {
    x() + y() = 2 * k().
}
"""
SIZE_IMPORT = SIZE_EXPRESSION.replace("${2*k}", "${__import__}")
SIZE_ATTRIBUTE = SIZE_EXPRESSION.replace("${2*k}", "${k.real}")
# k**2 in a placeholder, with the reference's 2 * k written as k * k.
SIZE_POWER = (SIZE_EXPRESSION.replace("${2*k}", "${k**2}")
              .replace("x() + y() = 2 * k().", "x() + y() = k() * k()."))
REFERENCE_POWER = REFERENCE_SIZE.replace("2 * k", "k * k")
# max over a list of pairs, sized from the flattened entries of a 2-D field.
SIZE_EDGES = """vocabulary {
    k: () -> Int
    type V := {0..${max(edges)}}
    x: () -> V
    y: () -> V
}
theory {
    x() + y() = k().
}
"""
REFERENCE_EDGES = '''
# Data
k = 2
edges = [[0, 1], [1, 2]]
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, k, name="x")
y = cp.intvar(0, k, name="y")
model = cp.Model(x + y == k)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
# A ground sentence whose argument is a data-defined function application.
GROUND_OUTPUT = """vocabulary {
    type Idx := {0..3}
    type Val := {0..3}
    pos: Idx -> Idx
    x: Idx -> Val
}
theory {
    x(pos(0)) = 1.
}
"""
REFERENCE_GROUND = '''
# Data
pos = [1, 2, 3, 0]
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 3, shape=4, name="x")
model = cp.Model(x[pos[0]] == 1)
model.solve()
solution = {"x": [int(value) for value in x.value()]}
print(json.dumps(solution))
'''
# A quantifier with ?=1 under an implication makes idp-engine 0.12.1 raise an
# internal TypeError while annotating; the runner must report it as an error.
ENGINE_ERROR = """vocabulary {
    type Bkt := {1..3}
    A: () -> Bool
    link: Int * Bkt -> Bool
    s: () -> Int
}
theory {
    A() => (?=1 b in Bkt: link(s(), b)).
}
"""
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
# A ragged list of rows binds padded to the longest row, with `rows_len` beside it.
# The model reads each row's last real entry, which is cell rows(r, rows_len(r)-1).
REFERENCE_RAGGED = '''
# Data
rows = [[1, 2, 3], [4]]
# End of data
import cpmpy as cp
import json
last = cp.intvar(0, 9, shape=len(rows), name="last")
model = cp.Model([last[i] == row[-1] for i, row in enumerate(rows)])
model.solve()
solution = {"last": [int(value) for value in last.value()]}
print(json.dumps(solution))
'''
RAGGED = """vocabulary {
    type Row <: Int
    type Col <: Int
    rows: Row * Col -> Int
    rows_len: Row -> Int
    last: Row -> Int
}
theory {
    ! r in Row : last(r) = rows(r, rows_len(r) - 1).
}
"""
# Rows of one length whose columns differ in type bind one piece per column: `cage_1`
# is the target and `cage_2` the padded list of cells. Rows of unequal length whose
# first item is a scalar bind as `clue_1` (the first items) and `clue_2` (the rest).
REFERENCE_MIXED = '''
# Data
cage = [[3, [[1, 1], [1, 2]]], [5, [[2, 2]]]]
clue = [[16, [1, 1], [1, 2]], [24, [1, 5], [1, 6], [1, 7]]]
# End of data
import cpmpy as cp
import json
value = cp.intvar(0, 99, shape=len(cage), name="value")
score = cp.intvar(0, 99, shape=len(clue), name="score")
model = cp.Model([value[i] == target + len(cells) for i, (target, cells) in enumerate(cage)],
                 [score[i] == target + len(cells) for i, (target, *cells) in enumerate(clue)])
model.solve()
solution = {"value": [int(v) for v in value.value()], "score": [int(s) for s in score.value()]}
print(json.dumps(solution))
'''
MIXED = """vocabulary {
    type Cage <: Int
    type Cell <: Int
    type Coord <: Int
    type Line <: Int
    type Slot <: Int
    type Pos <: Int
    cage_1: Cage -> Int
    cage_2: Cage * Cell * Coord -> Int
    cage_2_len: Cage -> Int
    clue_1: Line -> Int
    clue_2: Line * Slot * Pos -> Int
    clue_2_len: Line -> Int
    value: Cage -> Int
    score: Line -> Int
}
theory {
    ! g in Cage : value(g) = cage_1(g) + cage_2_len(g).
    ! l in Line : score(l) = clue_1(l) + clue_2_len(l).
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

        def check(name, source, reference=REFERENCE, expected=None, detail=None, **kwargs):
            result = evaluate(candidate(f"{name}.idp", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            if detail is not None:
                results[name] = results[name] and detail in result.get("detail", "")
            return result

        def refused(name, source, text):
            result = evaluate(candidate(f"{name}.idp", source), "readiness", SOLVER,
                              reference_source=REFERENCE_SIZE)
            return (not result["accepted"] and result["reason"] in {"execution_error", "invalid_output"}
                    and text in result.get("detail", ""))

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("size_expression", SIZE_EXPRESSION, reference=REFERENCE_SIZE, instances=[{"k": 3}],
              instance_count=2)
        results["size_expression_refused"] = (
            refused("size_import", SIZE_IMPORT, "__import__ is not an instance field")
            and refused("size_attribute", SIZE_ATTRIBUTE, "Attribute is not allowed here"))
        check("size_expression_power", SIZE_POWER, reference=REFERENCE_POWER, instances=[{"k": 3}],
              instance_count=2)
        check("size_expression_2d", SIZE_EDGES, reference=REFERENCE_EDGES,
              instances=[{"k": 3, "edges": [[0, 2], [2, 3], [1, 3]]}], instance_count=2)
        check("ground_output_sentence", GROUND_OUTPUT, reference=REFERENCE_GROUND,
              instances=[{"pos": [2, 0, 1, 3]}], instance_count=2)
        check("engine_error_reported", ENGINE_ERROR, expected={"execution_error"},
              detail="NoneType")
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)
        check("ragged_binding", RAGGED, reference=REFERENCE_RAGGED,
              instances=[{"rows": [[4, 5], [6, 7, 8]]}], instance_count=2)
        check("mixed_row_binding", MIXED, reference=REFERENCE_MIXED,
              instances=[{"cage": [[7, [[1, 1]]], [2, [[2, 2], [2, 3]]]],
                          "clue": [[9, [1, 1], [1, 2], [1, 3]], [12, [1, 4]]]}],
              instance_count=2)

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
