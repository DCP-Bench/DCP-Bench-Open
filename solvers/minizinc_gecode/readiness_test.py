"""Readiness checks for the minizinc_gecode integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver minizinc_gecode` runs this and
keeps its output as the readiness evidence.

Every instance field is bound as a model parameter, so each candidate below
declares `n` and `optimize` even where it only uses one of them.

`ragged_field`, `mixed_type_rows` and `unbindable_field_refused` cover the
reshaping run.py applies to fields MiniZinc's data interface cannot take as
they are: padded ragged rows with `<field>_len`, one array per column of
mixed-type rows, and a clear refusal for a shape neither rule covers.

The isolation check differs from the Python integrations by necessity. MiniZinc
is declarative and cannot inspect its own container, so that check drives the
image directly under the evaluator's own container flags instead of through a
submission. It tests the same guarantees on the same image; it just cannot route
them through the MiniZinc entrypoint.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "minizinc_gecode"

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

OUTPUT = r'output ["{\"x\":", show(x), ",\"y\":", show(y), "}"];' + "\n"
HEAD = "int: n;\nbool: optimize;\nvar 0..n: x;\nvar 0..n: y;\n"

GOOD = HEAD + "constraint if optimize then x+y >= n else x+y = n endif;\nsolve satisfy;\n" + OUTPUT
# The integration convention for optimization: a named integer `objective` and
# an unannotated solve item on its own line, which is what lets the runner
# re-solve at the proven optimum to enumerate.
OPTIMAL = (HEAD + "constraint x+y >= n;\nvar int: objective = x+y;\nsolve DIRECTION objective;\n" + OUTPUT)
# Compiles and solves, but its output is not the JSON object the runner parses.
MALFORMED = HEAD + "constraint x+y = n;\nsolve satisfy;\noutput [\"not json\"];\n"
UNSATISFIABLE = HEAD + "constraint x+y = n;\nconstraint x = n;\nconstraint y = n;\nsolve satisfy;\n" + OUTPUT
# Pigeonhole with plain disequalities rather than a global: no propagator sees
# the contradiction, so Gecode searches until the budget is gone.
SLOW = (HEAD + "array[1..16] of var 1..15: p;\n"
        "constraint forall(i, j in 1..16 where i < j)(p[i] != p[j]);\n"
        "constraint x+y = n;\nsolve satisfy;\n" + OUTPUT)

# The binding run.py adds for fields MiniZinc's data interface cannot take as
# they are. A ragged list of rows binds padded, with `<field>_len` beside it;
# the last instance is rectangular, where `<field>_len` is bound all the same.
RAGGED_REFERENCE = """
# Data
rows = [[1, 2], [3]]
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 100, shape=len(rows), name="total")
last = cp.intvar(0, 100, shape=len(rows), name="last")
model = cp.Model([total[i] == sum(row) for i, row in enumerate(rows)],
                 [last[i] == row[-1] for i, row in enumerate(rows)])
model.solve()
solution = {"total": total.value(), "last": last.value()}
print(json.dumps(solution))
"""
RAGGED = ("array[int,int] of int: rows;\narray[int] of int: rows_len;\n"
          "set of int: R = index_set(rows_len);\n"
          "array[R] of var 0..100: total;\narray[R] of var 0..100: last;\n"
          "constraint forall(i in R)(total[i] = sum(j in 1..rows_len[i])(rows[i,j]));\n"
          "constraint forall(i in R)(last[i] = rows[i, rows_len[i]]);\n"
          "solve satisfy;\n"
          r'output ["{\"total\":", show(total), ",\"last\":", show(last), "}"];' + "\n")
RAGGED_INSTANCES = [{"rows": [[4], [5, 6, 7], [8]]}, {"rows": [[1, 2], [3, 4]]}]

# Rows of one length whose columns differ in type bind as one array per
# column; here the third column is itself ragged, so it binds padded too.
MIXED_REFERENCE = """
# Data
items = [["a", 3, [[1, 2]]], ["b", 5, [[2, 2], [3, 1]]]]
# End of data
import cpmpy as cp
import json
score = cp.intvar(0, 1000, shape=len(items), name="score")
named = cp.boolvar(shape=len(items), name="named")
model = cp.Model([score[i] == value + sum(r * c for r, c in cells)
                  for i, (title, value, cells) in enumerate(items)],
                 [named[i] == (title == "b") for i, (title, value, cells) in enumerate(items)])
model.solve()
solution = {"score": score.value(), "named": named.value()}
print(json.dumps(solution))
"""
MIXED = ("array[int] of string: items_1;\narray[int] of int: items_2;\n"
         "array[int,int,int] of int: items_3;\narray[int] of int: items_3_len;\n"
         "set of int: I = index_set(items_2);\n"
         "array[I] of var 0..1000: score;\narray[I] of var bool: named;\n"
         "constraint forall(i in I)(score[i] = items_2[i]"
         " + sum(k in 1..items_3_len[i])(items_3[i,k,1] * items_3[i,k,2]));\n"
         "constraint forall(i in I)(named[i] <-> items_1[i] = \"b\");\n"
         "solve satisfy;\n"
         r'output ["{\"score\":", show(score), ",\"named\":", show(named), "}"];' + "\n")
MIXED_INSTANCES = [{"items": [["b", 1, [[3, 3]]], ["c", 0, [[1, 1], [2, 1], [1, 4]]], ["a", 2, []]]}]

# A row that is ragged and mixes types at once fits neither rule; the runner
# refuses it rather than guessing a layout.
REFUSED_REFERENCE = """
# Data
rows = [[1, 2], [3, [4]]]
# End of data
import cpmpy as cp
import json
total = cp.intvar(0, 100, shape=len(rows), name="total")
last = cp.intvar(0, 100, shape=len(rows), name="last")
model = cp.Model([total[i] == len(row) for i, row in enumerate(rows)],
                 [last[i] == len(row) for i, row in enumerate(rows)])
model.solve()
solution = {"total": total.value(), "last": last.value()}
print(json.dumps(solution))
"""

ISOLATION_PROBE = """import os, socket
probe = socket.socket(); probe.settimeout(0.5)
assert os.getuid() != 0, "container runs as root"
assert sorted(os.listdir("/input")) == ["model.mzn", "request.json"], "unexpected /input"
assert not os.path.exists("/dataset"), "dataset is visible to the candidate"
assert probe.connect_ex(("1.1.1.1", 443)) != 0, "network reachable"
try:
    open("/input/written", "w"); raise AssertionError("input is writable")
except OSError:
    pass
print("isolated")
"""


def isolation(temp):
    """Drive the image under the evaluator's container flags, without a submission."""
    staging = temp / "isolation"
    staging.mkdir()
    (staging / "model.mzn").write_text("solve satisfy;\n", encoding="utf-8")
    (staging / "request.json").write_text("{}", encoding="utf-8")
    staging.chmod(0o755)
    for path in staging.iterdir():
        path.chmod(0o644)
    code, out, err = run_process([
        "docker", "run", "--rm", "--pull=never", "--network=none", "--read-only",
        "--user=65534:65534", "--cap-drop=ALL", "--security-opt=no-new-privileges",
        "--pids-limit=128", "--log-driver=none", "--memory", "2048m", "--memory-swap", "2048m",
        "--cpus", "1", "--tmpfs", "/tmp:rw,exec,nosuid,size=536870912,mode=1777",
        "--mount", f"type=bind,source={staging},target=/input,readonly",
        "--workdir=/tmp", "--env=HOME=/tmp", "--entrypoint", "python",
        integration(SOLVER)["image"], "-c", ISOLATION_PROBE], 120)
    if code:
        print(err[-400:], file=sys.stderr)
    return code == 0 and "isolated" in out


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / f"{name}.mzn"
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
        check("minimization", OPTIMAL.replace("DIRECTION", "minimize"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximize"), reference=MAXIMIZING)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        # Each instance must have been checked, not merely the first.
        ragged = check("ragged_field", RAGGED, reference=RAGGED_REFERENCE,
                       instances=RAGGED_INSTANCES, instance_count=3)
        results["ragged_field"] &= ragged["instances_checked"] == 3
        mixed = check("mixed_type_rows", MIXED, reference=MIXED_REFERENCE,
                      instances=MIXED_INSTANCES, instance_count=2)
        results["mixed_type_rows"] &= mixed["instances_checked"] == 2
        # The refusal names the field, so a model author can tell why it failed.
        refused = check("unbindable_field_refused", RAGGED, reference=REFUSED_REFERENCE,
                        expected={"execution_error"})
        results["unbindable_field_refused"] &= "Instance field `rows`" in refused.get("detail", "")
        for name, result in (("ragged_field", ragged), ("mixed_type_rows", mixed),
                             ("unbindable_field_refused", refused)):
            print(name, json.dumps({key: result.get(key) for key in
                                    ("accepted", "reason", "detail", "instances_checked")}),
                  file=sys.stderr)
        results["isolation"] = isolation(temp)

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
