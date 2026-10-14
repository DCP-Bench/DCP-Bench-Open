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
        check("optimum_enumeration", OPTIMAL, reference=OPTIMIZING, solution_limit=5)
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
