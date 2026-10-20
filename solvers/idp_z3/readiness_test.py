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
    n: () -> Int
    x: () -> Int
    y: () -> Int
}
theory {
    0 =< x() & x() =< n().
    0 =< y() & y() =< n().
    x() + y() = n().
}
"""
OPTIMAL = """vocabulary {
    n: () -> Int
    x: () -> Int
    y: () -> Int
    DIRECTION: () -> Int
}
theory {
    0 =< x() & x() =< n().
    0 =< y() & y() =< n().
    x() + y() >= n().
    DIRECTION() = x() + y().
}
"""
MALFORMED = "this is not FO(.) {{{\n"
# A type Range_k declared <: Int is interpreted as {1..k} from the scalar field k.
# The reference has k solutions; it is checked for k=2 and k=4.
REFERENCE_RANGE = '''
# Data
k = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(1, k, name="x")
y = cp.intvar(1, k, name="y")
model = cp.Model(x + y == k + 1)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
'''
RANGE_TYPE = """vocabulary {
    type Range_k <: Int
    k: () -> Int
    x: () -> Range_k
    y: () -> Range_k
}
theory {
    x() + y() = k() + 1.
}
"""
# Range_m names no instance field, and ${k} is not FO(.) syntax: both are errors.
RANGE_UNKNOWN = RANGE_TYPE.replace("Range_k", "Range_m")
PLACEHOLDER = RANGE_TYPE.replace("type Range_k <: Int", "type Range_k := {1..${k}}")
# A type S with S_size: () -> Int is {1..v}, v being what the theory gives S_size
# from the data: here k + 2 entries, exactly one of them 1.
REFERENCE_SIZED = '''
# Data
k = 2
# End of data
import cpmpy as cp
import json
s = cp.intvar(0, 1, shape=k + 2, name="s")
model = cp.Model(cp.sum(s) == 1)
model.solve()
solution = {"s": [int(v) for v in s.value()]}
print(json.dumps(solution))
'''
SIZED_TYPE = """vocabulary {
    k: () -> Int
    type S <: Int
    S_size: () -> Int
    s: S -> Int
}
theory {
    S_size() = k() + 2.
    ! i in S: 0 =< s(i) & s(i) =< 1.
    sum{{ s(i) | i in S }} = 1.
}
"""
# An output declared (domain: gap) is read only where gap holds: all-interval series,
# x a permutation of 1..n and diffs its n-1 distinct successive differences.
REFERENCE_PARTIAL = '''
# Data
n = 3
# End of data
import cpmpy as cp
import json
x = cp.intvar(1, n, shape=n, name="x")
diffs = cp.intvar(1, n - 1, shape=n - 1, name="diffs")
model = cp.Model(cp.AllDifferent(x), cp.AllDifferent(diffs),
                 [diffs[i] == cp.abs(x[i + 1] - x[i]) for i in range(n - 1)])
model.solve()
solution = {"x": [int(v) for v in x.value()], "diffs": [int(v) for v in diffs.value()]}
print(json.dumps(solution))
'''
PARTIAL_OUTPUT = """vocabulary {
    type Range_n <: Int
    n: () -> Int
    gap: Range_n -> Bool
    x: Range_n -> Range_n
    diffs: Range_n -> Int (domain: gap)
}
theory {
    { ! i in Range_n: gap(i) <- i < n(). }
    ! i, j in Range_n: i ~= j => x(i) ~= x(j).
    ! i in Range_n: gap(i) & i < n() => diffs(i) = abs(x(i + 1) - x(i)).
    ! i in Range_n: ! j in Range_n: gap(i) & gap(j) & i ~= j => diffs(i) ~= diffs(j).
}
"""
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
    n: () -> Int
    x: () -> Int
    y: () -> Int
}
theory {
    0 =< x() & x() =< n().
    0 =< y() & y() =< n().
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
                              reference_source=REFERENCE_RANGE)
            return (not result["accepted"] and result["reason"] in {"execution_error", "invalid_output"}
                    and text in result.get("detail", ""))

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("range_type", RANGE_TYPE, reference=REFERENCE_RANGE, instances=[{"k": 4}],
              instance_count=2, solution_limit=5)
        results["range_type_refused"] = (
            refused("range_unknown", RANGE_UNKNOWN, "m is not an integer scalar field")
            and refused("placeholder", PLACEHOLDER, "Expected IDPFLOAT or INT"))
        check("sized_type", SIZED_TYPE, reference=REFERENCE_SIZED, instances=[{"k": 4}],
              instance_count=2, solution_limit=7)
        check("partial_output", PARTIAL_OUTPUT, reference=REFERENCE_PARTIAL, instances=[{"n": 5}],
              instance_count=2, solution_limit=3)
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
