"""Readiness checks for the pycsp3_ace integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver pycsp3_ace` runs this and keeps
its output as the readiness evidence.

Candidates are plain PyCSP3 scripts: `data` holds the instance and the declared
outputs are module-level names. `optimum_unproven_timeout` is an optimisation
whose proof cannot finish in the budget: the runner must report a timeout with no
solution, not the incumbent ACE found. `optimum_enumeration` checks that the
solutions reported for an optimisation all have the proven optimum.
`metadata_fields_ignored` and `one_key_instance` cover the instance binding, and
`ragged_data` a list of rows whose lengths differ.
`ace_error_reported` uses a reserved identifier (ACE stops with "is a keyword"),
`compile_error_surfaced` a pycsp3 declaration error, and `invalid_tuple_guard` a
Product over four variables that ACE 2.6 solves with invalid tuples.

The isolation check drives the image directly under the evaluator's own
container flags instead of through a submission.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "pycsp3_ace"

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

HEAD = ("from pycsp3 import *\n"
        "n = data.n\n"
        "x = Var(range(n + 1))\n"
        "y = Var(range(n + 1))\n")
GOOD = HEAD + "satisfy(x + y == n)\n"
OPTIMAL = HEAD + "satisfy(x + y >= n)\nminimize(x + y)\n"
MAXIMAL = HEAD + "satisfy(x + y >= n)\nmaximize(x + y)\n"
# Does not parse: the runner reports an error and no solution.
MALFORMED = HEAD + "satisfy(x + y == n\n"
UNSATISFIABLE = HEAD + "satisfy(x == 1, x == 0)\n"
# Golomb rulers with 14 marks. The shortest is 127 long, so in 0..126 there is
# none, and ACE cannot show that within the budget. In the optimisation variant
# the domain admits rulers and ACE cannot prove the shortest one in the budget.
GOLOMB = ("m = VarArray(size=14, dom=range(HIGH + 1), id='m')\n"
          "satisfy(m[0] == 0, [m[i] < m[i + 1] for i in range(13)],\n"
          "        AllDifferent([m[j] - m[i] for i in range(14) for j in range(i + 1, 14)]))\n")
# The declared outputs x and y must exist even where the search never gets to them.
PROBLEM_HEAD = "from pycsp3 import *\nx = Var(range(3))\ny = Var(range(3))\nsatisfy(x + y == 2)\n"
SLOW = PROBLEM_HEAD + GOLOMB.replace("HIGH", "126")
SLOW_OPTIMISATION = PROBLEM_HEAD + GOLOMB.replace("HIGH", "200") + "minimize(m[13])\n"

# Only the fields a model reads reach it, and a one-key instance is still an object.
ONE_KEY_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, name="x")
y = cp.intvar(0, n, name="y")
model = cp.Model(x + y == n)
model.solve()
solution = {"x": int(x.value()), "y": int(y.value())}
print(json.dumps(solution))
"""
ONE_KEY = HEAD + "satisfy(x + y == n)\n"
ONE_KEY_INSTANCES = [{"n": 3}, {"n": 4}]

# Metadata strings that no model reads must not reach the model or break it.
NAMED_REFERENCE = REFERENCE.replace("optimize = False", 'optimize = False\nname = "first"\nnote = "a"')
NAMED_INSTANCES = [{"n": 2, "optimize": False, "name": "first", "note": "a"},
                   {"n": 3, "optimize": False, "name": "second", "note": "b"}]

# Rows of different lengths: the model reads `data.rows[i]` and its last item.
RAGGED_REFERENCE = """
# Data
rows = [[1, 2, 3], [4]]
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
RAGGED = ("from pycsp3 import *\n"
          "rows = data.rows\n"
          "total = VarArray(size=len(rows), dom=range(100), id='total')\n"
          "last = VarArray(size=len(rows), dom=range(100), id='last')\n"
          "satisfy([total[i] == sum(row) for i, row in enumerate(rows)],\n"
          "        [last[i] == row[-1] for i, row in enumerate(rows)])\n")
RAGGED_INSTANCES = [{"rows": [[4, 5], [6, 7, 8]]}, {"rows": [[9], [1, 2, 3]]}]

# A reserved identifier: ACE stops with "The id E is a keyword". The runner must say so.
VECTOR_REFERENCE = """
# Data
n = 2
# End of data
import cpmpy as cp
import json
x = cp.intvar(0, n, shape=2, name="x")
model = cp.Model(x[0] + x[1] == n)
model.solve()
solution = {"x": [int(v) for v in x.value()]}
print(json.dumps(solution))
"""
RESERVED_ID = ("from pycsp3 import *\n"
               "n = data.n\n"
               "x = VarArray(size=2, dom=range(n + 1), id='E')\n"
               "satisfy(x[0] + x[1] == n)\n")
# A declaration error: pycsp3 prints "The identifier z is used twice" and exits.
DECLARATION_ERROR = ("from pycsp3 import *\n"
                     "n = data.n\n"
                     "x = Var(range(n + 1))\n"
                     "y = Var(range(n + 1))\n"
                     "for i in range(2):\n"
                     "    z = Var(range(2))\n"
                     "satisfy(x + y == n)\n")
# ACE 2.6 accepts invalid tuples for Product over four variables: 100*50*1*1 = 5000, not 5040.
# The guard must reject those and emit only tuples that multiply to 5040.
PRODUCT_REFERENCE = """
# Data
# End of data
import cpmpy as cp
import json
x = cp.intvar(1, 100, shape=4, name="x")
model = cp.Model(x[0] * x[1] * x[2] * x[3] == 5040)
model.solve()
solution = {"x": [int(v) for v in x.value()]}
print(json.dumps(solution))
"""
PRODUCT = ("from pycsp3 import *\n"
           "x = VarArray(size=4, dom=range(1, 101), id='x')\n"
           "satisfy(Product(x) == 5040)\n")
SMALL_PRODUCT_REFERENCE = PRODUCT_REFERENCE.replace("intvar(1, 100", "intvar(1, 10").replace("5040", "24")
SMALL_PRODUCT = PRODUCT.replace("range(1, 101)", "range(1, 11)").replace("5040", "24")

ISOLATION_PROBE = """import os, socket
probe = socket.socket(); probe.settimeout(0.5)
assert os.getuid() != 0, "container runs as root"
assert sorted(os.listdir("/input")) == ["model.py", "request.json"], "unexpected /input"
assert not os.path.exists("/dataset"), "dataset is visible to the candidate"
assert probe.connect_ex(("1.1.1.1", 443)) != 0, "network reachable"
try:
    open("/input/written", "w"); raise AssertionError("input is writable")
except OSError:
    pass
print("isolated")
"""


# ---------------------------------------------------------------------------
# Bug-class checks (readiness level 2). The trusted references are the CPMpy ones of
# solvers/cpmpy_python/readiness_test.py, copied verbatim; only the PyCSP3 submissions
# are written for this integration, mirroring the cpmpy submission's model.

# optimization_timeout: the reference is easy (minimise x, optimum n); the submission
# adds an unrelated Golomb ruler to its objective, so ACE finds a solution at once but
# cannot prove the optimum within the budget. A correct runner emits nothing.
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
UNPROVABLE = ("from pycsp3 import *\n"
              "x = Var(range(11))\n"
              "marks = VarArray(size=11, dom=range(201), id='marks')\n"
              "satisfy(x >= data.n, marks[0] == 0, [marks[i] < marks[i + 1] for i in range(10)],\n"
              "        AllDifferent([marks[j] - marks[i] for i in range(11) for j in range(i + 1, 11)]))\n"
              "minimize(1000 * x + marks[10])\n")
# minimization_step_one: the optimum sits one below an easy solution (see the cpmpy file).
STEP_REF = EASY_MIN.replace("x >= n", "x >= n - 1")
# ACE branches on the smallest value first and would find the optimum at once, so y picks
# the first solution x = n (optimum + 1) and only later the optimum n - 1.
STEP = ("from pycsp3 import *\n"
        "y = Var(range(2))\n"
        "x = Var(range(11))\n"
        "satisfy(x == data.n - y)\n"
        "minimize(x)\n")
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
SUM = ("from pycsp3 import *\n"
       "x = VarArray(size=4, dom=range(3), id='x')\n"
       "satisfy(Sum(x) >= data.n)\n"
       "minimize(Sum(x))\n")
# output_shapes: a three-level integer array, a Boolean matrix and a value beyond 32 bits.
# ACE refuses integers beyond 32 bits when it parses the XCSP3 file; the runner surfaces
# that refusal as an execution_error naming it (CONTRACT.md ## Outputs).
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
SHAPES = ("from pycsp3 import *\n"
          "n = data.n\n"
          "cube = VarArray(size=[2, 2, 2], dom=range(11), id='cube')\n"
          "grid = VarArray(size=[2, 2], dom={0, 1}, id='grid')\n"
          "big = Var(range(40000000001))\n"
          "satisfy([cube[i][j][k] == i + j + k + n for i in range(2) for j in range(2) for k in range(2)],\n"
          "        [grid[i][j] == int(i == j) for i in range(2) for j in range(2)],\n"
          "        big == 30000000000 + n)\n")
# instance_shapes: ragged rows, rows of mixed types, a string field the model ignores,
# and name/note keys, on two instances with different shapes.
SHAPED_REF = """
# Data
n = 2
rows = [[1], [2, 3]]
mixed = [[1, "a"], [2, "b"]]
label = "first"
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
SHAPED_INSTANCE = {"n": 3, "rows": [[4, 5, 6], [], [1]], "mixed": [[3, "c"]], "label": "second",
                   "name": "readiness", "note": "ragged rows, mixed rows, an unused string"}
SHAPED = ("from pycsp3 import *\n"
          "total = Var(range(1001))\n"
          "key = Var(range(1001))\n"
          "satisfy(total == data.n + sum(sum(row) for row in data.rows),\n"
          "        key == sum(row[0] for row in data.mixed))\n")
# error_detail: the library raises while the model is built; the evaluator must report
# execution_error with the library's own message, not a timeout or a bare exit code.
FAILING = ("from pycsp3 import *\n"
           "x = Var(range(data.n + 1))\n"
           "y = Var(range(data.n + 1))\n"
           "satisfy(0.5 * x + y == data.n)\n")
# stray_stdout: the model prints; the protocol stream must survive it.
CHATTY = ("from pycsp3 import *\n"
          "print('loading the model')\n"
          "x = Var(range(data.n + 1))\n"
          "y = Var(range(data.n + 1))\n"
          "print('building for n =', data.n)\n"
          "satisfy(x + y == data.n)\n")
# auxiliary_free_distinct: a free auxiliary variable must not repeat output solutions.
AUXILIARY = ("from pycsp3 import *\n"
             "x = Var(range(data.n + 1))\n"
             "y = Var(range(data.n + 1))\n"
             "spare = Var(range(6))\n"
             "satisfy(x + y == data.n, spare >= 0)\n")
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
LARGE = ("from pycsp3 import *\n"
         "b = VarArray(size=3000, dom={0, 1}, id='b')\n"
         "count = Var(range(3001))\n"
         "satisfy(Sum(b) == count, count == data.n)\n")


def isolation(temp):
    """Drive the image under the evaluator's container flags, without a submission."""
    staging = temp / "isolation"
    staging.mkdir()
    (staging / "model.py").write_text("from pycsp3 import *\n", encoding="utf-8")
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
        check("minimization", OPTIMAL, reference=OPTIMIZING)
        check("maximization", MAXIMAL, reference=MAXIMIZING)
        check("optimum_solutions_proven", OPTIMAL, reference=OPTIMIZING, solution_limit=5)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=8)
        unproven = check("optimum_unproven_timeout", SLOW_OPTIMISATION, reference=OPTIMIZING,
                         expected={"execution_timeout"}, execution_timeout=8)
        results["optimum_unproven_timeout"] &= not unproven.get("solutions_checked")
        named = check("metadata_fields_ignored", GOOD, reference=NAMED_REFERENCE,
                      instances=NAMED_INSTANCES, instance_count=2)
        results["metadata_fields_ignored"] &= named["instances_checked"] == 2
        one = check("one_key_instance", ONE_KEY, reference=ONE_KEY_REFERENCE,
                    instances=ONE_KEY_INSTANCES, instance_count=3)
        results["one_key_instance"] &= one["instances_checked"] == 3
        ragged = check("ragged_data", RAGGED, reference=RAGGED_REFERENCE,
                       instances=RAGGED_INSTANCES, instance_count=3)
        results["ragged_data"] &= ragged["instances_checked"] == 3
        def detail_of(name, source, reference, expected_text, **kwargs):
            result = evaluate(candidate(name, source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["reason"] == "execution_error" and expected_text in result.get("detail", "")
            return result

        detail_of("ace_error_reported", RESERVED_ID, VECTOR_REFERENCE, "keyword")
        detail_of("compile_error_surfaced", DECLARATION_ERROR, REFERENCE, "identifier z is used twice")
        # Three solutions take ACE 60 to 90 s here; the budget leaves room for a busy host.
        check("invalid_tuple_guard", PRODUCT, reference=PRODUCT_REFERENCE, solution_limit=3,
              execution_timeout=180)
        check("invalid_tuple_guard_small", SMALL_PRODUCT, reference=SMALL_PRODUCT_REFERENCE, solution_limit=3)

        # Bug-class checks (readiness level 2), with the cpmpy_python assertions.
        result = evaluate(candidate("optimization_timeout.py", UNPROVABLE), "readiness", SOLVER,
                          reference_source=EASY_MIN, execution_timeout=8)
        results["optimization_timeout"] = (result["reason"] == "execution_timeout"
                                           and all(item.get("solutions_received", 0) == 0
                                                   for item in result["instances"]))
        check("minimization_step_one", STEP, reference=STEP_REF)
        result = check("optimum_enumeration", SUM, reference=SUM_REF, solution_limit=3)
        results["optimum_enumeration"] = result["accepted"] and result["solutions_checked"] == 3
        result = evaluate(candidate("output_shapes", SHAPES), "readiness", SOLVER,
                          reference_source=SHAPES_REF)
        results["output_shapes"] = (result["reason"] == "execution_error"
                                    and "Too big integer value" in json.dumps(result))
        check("instance_shapes", SHAPED, reference=SHAPED_REF, instances=[SHAPED_INSTANCE], instance_count=2)
        detail_of("error_detail", FAILING, REFERENCE, "bad form of predicate")
        check("stray_stdout", CHATTY)
        result = check("auxiliary_free_distinct", AUXILIARY, solution_limit=3)
        results["auxiliary_free_distinct"] = result["accepted"] and result["solutions_checked"] == 3
        check("large_model", LARGE, reference=LARGE_REF, execution_timeout=120, reference_timeout=120)
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
