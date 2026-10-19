"""Readiness checks for the eclipse_clp integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver eclipse_clp` runs this and keeps
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

SOLVER = "eclipse_clp"

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

HEADER = ":- lib(ic).\n"
GOOD = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                 "    memberchk(n-N, Instance),\n"
                 "    [X, Y] #:: 0..N,\n"
                 "    X + Y #= N.\n")
OPTIMAL = HEADER + ("model(Instance, [X, Y], [x-X, y-Y], OBJECTIVE(X + Y)) :-\n"
                    "    memberchk(n-N, Instance),\n"
                    "    [X, Y] #:: 0..N,\n"
                    "    X + Y #>= N.\n")
# Outputs that are not Name-Value pairs: the driver must refuse them rather than
# print something the evaluator would have to guess at.
MALFORMED = HEADER + "model(_, [], not_a_pair_list).\n"
UNSATISFIABLE = HEADER + ("model(_, [X], [x-X, y-2]) :-\n"
                          "    X #:: 0..1,\n"
                          "    X #= 5.\n")
SLOW = HEADER + ("model(_, [X], [x-X, y-0]) :-\n"
                 "    X #:: 0..1,\n"
                 "    loop.\n"
                 "loop :- loop.\n")
# Every claim the evaluator makes about the sandbox, asserted from inside it:
# an unprivileged user, no dataset, only the two staged files, a read-only root
# and no network.
ISOLATED = HEADER + (
    "model(Instance, [X, Y], [x-X, y-Y]) :-\n"
    "    open('/proc/self/status', read, S),\n"
    "    read_string(S, \"\", _, Status),\n"
    "    close(S),\n"
    "    substring(Status, \"Uid:\\t65534\\t65534\\t65534\\t65534\", _),\n"
    "    \\+ exists('/dataset'),\n"
    "    read_directory('/input', \"*\", _, Files),\n"
    "    msort(Files, [First, Second]),\n"
    "    First == \"model.ecl\",\n"
    "    Second == \"request.json\",\n"
    "    \\+ catch(open('/probe.txt', write, _), _, fail),\n"
    "    \\+ catch((socket(internet, stream, Socket), connect(Socket, '1.1.1.1'/443)), _, fail),\n"
    "    memberchk(n-N, Instance),\n"
    "    [X, Y] #:: 0..N,\n"
    "    X + Y #= N.\n")


# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). Each pairs a tiny trusted reference with a
# submission that exercises one class of runner bug the modelling campaigns found.

# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an unrelated Golomb ruler to its objective, so branch and bound finds
# solutions but cannot prove the optimum within the budget. A correct runner emits
# nothing; a runner that leaks its unproven incumbent fails the check.
EASY_MIN = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 10, name="x")
model = cp.Model(x >= n)
model.minimize(x)
model.solve()
solution = {"x": int(x.value())}
print(json.dumps(solution))
"""
UNPROVABLE = HEADER + (
    ":- lib(lists).\n"
    "model(Instance, [X|Marks], [x-X], min(1000 * X + Last)) :-\n"
    "    memberchk(n-N, Instance),\n"
    "    X #:: 0..10,\n"
    "    X #>= N,\n"
    "    length(Marks, 11),\n"
    "    Marks #:: 0..200,\n"
    "    Marks = [0|_],\n"
    "    ascending(Marks),\n"
    "    differences(Marks, Diffs),\n"
    "    alldifferent(Diffs),\n"
    "    last_mark(Marks, Last).\n"
    "ascending([_]).\n"
    "ascending([A, B|Rest]) :- A #< B, ascending([B|Rest]).\n"
    "differences([], []).\n"
    "differences([A|Rest], Diffs) :-\n"
    "    ( foreach(B, Rest), foreach(D, Here), param(A) do D #= B - A ),\n"
    "    differences(Rest, More),\n"
    "    append(Here, More, Diffs).\n"
    "last_mark([X], X).\n"
    "last_mark([_, Y|Rest], X) :- last_mark([Y|Rest], X).\n")
# minimization_step_one: the optimum sits one below the first solution the search
# reaches (the submission labels in descending order), so a runner that bounds the
# objective itself and skips the next improvement would report optimum + 1.
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
STEP = HEADER + ("search_goal(Vars) :- search(Vars, 0, input_order, indomain_max, complete, []).\n"
                 "model(Instance, [X], [x-X], min(X)) :-\n"
                 "    memberchk(n-N, Instance),\n"
                 "    X #:: 0..10,\n"
                 "    X #>= N - 1.\n")
# optimum_enumeration: a compound objective (a sum) with ten optimal solutions.
SUM_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, 2, shape=4, name="x")
model = cp.Model(cp.sum(x) >= n)
model.minimize(cp.sum(x))
model.solve()
solution = {"x": x.value().tolist()}
print(json.dumps(solution))
"""
SUM = HEADER + ("model(Instance, Xs, [x-Xs], min(sum(Xs))) :-\n"
                "    memberchk(n-N, Instance),\n"
                "    length(Xs, 4),\n"
                "    Xs #:: 0..2,\n"
                "    sum(Xs) #>= N.\n")
# negative_offset_objective: a negative objective with an offset, minimised and
# maximised, in gfd as well as ic.
NEGATIVE_REF = """
# Data
n = 3
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y <= n)
model.maximize(-100 - x + 2 * y)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
NEGATIVE_MIN_REF = NEGATIVE_REF.replace("model.maximize(-100 - x + 2 * y)", "model.minimize(-100 - x + 2 * y)")
NEGATIVE = ("model(Instance, [X, Y], [x-X, y-Y], OBJECTIVE(-100 - X + 2 * Y)) :-\n"
            "    memberchk(n-N, Instance),\n"
            "    [X, Y] #:: 0..N,\n"
            "    X + Y #=< N.\n")
# output_shapes: a three-level integer array, a Boolean matrix and a value beyond 32 bits.
SHAPES_REF = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
cube = cp.intvar(0, 10, shape=(2, 2, 2), name="cube")
grid = cp.boolvar(shape=(2, 2), name="grid")
big = cp.intvar(0, 40000000000, name="big")
model = cp.Model([cube[i, j, k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],
                 [grid[i, j] == (i == j) for i in range(2) for j in range(2)],
                 big == 30000000000 + n)
model.solve()
solution = {"cube": cube.value().tolist(), "grid": grid.value().tolist(), "big": int(big.value())}
print(json.dumps(solution))
"""
SHAPES = HEADER + ("model(Instance, [], [cube-[[[A, B], [B, C]], [[B, C], [C, D]]], grid-[[true, false], [0, 1]], big-Big]) :-\n"
                   "    memberchk(n-N, Instance),\n"
                   "    A is N, B is N + 1, C is N + 2, D is N + 3,\n"
                   "    Big is 30000000000 + N.\n")
# instance_shapes: ragged rows, rows of mixed types, an unused string field, null,
# a nested object and name/note keys, on two instances with different shapes.
SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
nothing = None
nested = {"k": [1, 2]}
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 1000, name="total")
key = cp.intvar(0, 1000, name="key")
model = cp.Model(total == n + sum(sum(row) for row in rows), key == sum(row[0] for row in mixed))
model.solve()
solution = {"total": int(total.value()), "key": int(key.value())}
print(json.dumps(solution))
"""
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "it's \"second\"\\",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string",
                   "nothing": None, "nested": {"k": [1, 2]}}
SHAPED = HEADER + ("model(Instance, [], [total-Total, key-Key]) :-\n"
                   "    memberchk(n-N, Instance),\n"
                   "    memberchk(rows-Rows, Instance),\n"
                   "    memberchk(mixed-Mixed, Instance),\n"
                   "    memberchk(label-Label, Instance),\n"
                   "    string(Label),\n"
                   "    memberchk(nothing-null, Instance),\n"
                   "    memberchk(nested-[k-[1, 2]], Instance),\n"
                   "    sum_rows(Rows, N, Total),\n"
                   "    first_items(Mixed, 0, Key).\n"
                   "sum_rows([], Sum, Sum).\n"
                   "sum_rows([Row|Rows], Sum0, Sum) :-\n"
                   "    sum_row(Row, Sum0, Sum1),\n"
                   "    sum_rows(Rows, Sum1, Sum).\n"
                   "sum_row([], Sum, Sum).\n"
                   "sum_row([X|Xs], Sum0, Sum) :- Sum1 is Sum0 + X, sum_row(Xs, Sum1, Sum).\n"
                   "first_items([], Sum, Sum).\n"
                   "first_items([[F|_]|Rows], Sum0, Sum) :- Sum1 is Sum0 + F, first_items(Rows, Sum1, Sum).\n")
# error_detail: ECLiPSe raises while the model is built; the evaluator must report
# execution_error with ECLiPSe's own message, not a timeout or a bare exit code.
FAILING = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                    "    memberchk(n-N, Instance),\n"
                    "    [X, Y] #:: 0..N,\n"
                    "    atom_length(_, _),\n"
                    "    X + Y #= N.\n")
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                   "    memberchk(n-N, Instance),\n"
                   "    writeln(\"building the model\"),\n"
                   "    printf(\"n is %w\", [N]),\n"
                   "    [X, Y] #:: 0..N,\n"
                   "    X + Y #= N.\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = HEADER + ("model(Instance, [X, Y, Spare], [x-X, y-Y]) :-\n"
                      "    memberchk(n-N, Instance),\n"
                      "    [X, Y] #:: 0..N,\n"
                      "    Spare #:: 0..5,\n"
                      "    X + Y #= N.\n")
# large_model: 3000 Booleans in one sum, reported as an output.
LARGE_REF = """
# Data
n = 1500
# End of data
import cpmpy as cp
import json
b = cp.boolvar(shape=3000, name="b")
count = cp.intvar(0, 3000, name="count")
model = cp.Model(count == cp.sum(b), count == n)
model.solve()
solution = {"b": b.value().tolist(), "count": int(count.value())}
print(json.dumps(solution))
"""
LARGE = HEADER + ("model(Instance, Bs, [b-Bs, count-Count]) :-\n"
                  "    memberchk(n-N, Instance),\n"
                  "    length(Bs, 3000),\n"
                  "    Bs #:: 0..1,\n"
                  "    Count #:: 0..3000,\n"
                  "    Count #= sum(Bs),\n"
                  "    Count #= N.\n")
# objective_only_output: the only output is the optimum, and eight unit jobs on one
# machine have 40320 optimal start vectors. Asking for two solutions must end at once
# with one solution and `complete`, not walk the whole tree at the optimum.
MAKESPAN_REF = """
# Data
n = 8
# End of data
import cpmpy as cp
import json
start = cp.intvar(0, 2 * n, shape=n, name="start")
makespan = cp.intvar(0, 2 * n, name="makespan")
model = cp.Model([cp.max(start + 1) == makespan],
                 [cp.NoOverlap(start, [1] * n, start + 1)])
model.minimize(makespan)
model.solve()
solution = {"makespan": int(makespan.value())}
print(json.dumps(solution))
"""
MAKESPAN = HEADER + (
    ":- lib(lists).\n"
    "model(Instance, [Makespan|Starts], [makespan-Makespan], min(Makespan)) :-\n"
    "    memberchk(n-N, Instance),\n"
    "    length(Starts, N),\n"
    "    H is 2 * N,\n"
    "    Starts #:: 0..H,\n"
    "    Makespan #:: 0..H,\n"
    "    no_overlap(Starts),\n"
    "    ( foreach(S, Starts), param(Makespan) do S + 1 #=< Makespan ),\n"
    "    Makespan #= max(Starts) + 1.\n"
    "no_overlap([]).\n"
    "no_overlap([S|Rest]) :-\n"
    "    ( foreach(T, Rest), param(S) do ( S + 1 #=< T ) or ( T + 1 #=< S ) ),\n"
    "    no_overlap(Rest).\n")


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.ecl", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back
        # as exhaustion rather than as a shortfall the evaluator would reject.
        exhausted = check("exhausted_enumeration", GOOD, solution_limit=5)
        results["exhausted_enumeration"] = (
            results["exhausted_enumeration"]
            and exhausted["instances"][0]["solutions_received"] == 3
            and exhausted["instances"][0]["runner_status"]["status"] == "complete")
        check("minimization", OPTIMAL.replace("OBJECTIVE", "min"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "max"), reference=MAXIMIZING)
        check("isolation", ISOLATED)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=2)

        # Bug-class checks (readiness level 2).
        result = evaluate(candidate("optimization_timeout.ecl", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=3)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        result = check("objective_only_output", MAKESPAN, reference=MAKESPAN_REF, solution_limit=2,
                       execution_timeout=20, reference_timeout=60)
        results["objective_only_output"] = (
            result["accepted"]
            and result["instances"][0]["solutions_received"] == 1
            and result["instances"][0]["runner_status"]["status"] == "complete")
        check("negative_objective_min",HEADER + NEGATIVE.replace("OBJECTIVE", "min"),
              reference=NEGATIVE_MIN_REF)
        check("negative_objective_max", HEADER + NEGATIVE.replace("OBJECTIVE", "max"),
              reference=NEGATIVE_REF)
        check("negative_objective_gfd", ":- lib(gfd).\n" + NEGATIVE.replace("OBJECTIVE", "max"),
              reference=NEGATIVE_REF)
        check("output_shapes", SHAPES, reference=SHAPES_REF)
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        result = evaluate(candidate("error_detail.ecl", FAILING), "readiness", SOLVER, reference_source=REFERENCE)
        results["error_detail"] = (result["reason"] == "execution_error"
                                   and "instantiation fault" in json.dumps(result).lower())
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)

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
