"""Readiness checks for the essence_prime_minion integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver essence_prime_minion` runs this
and keeps its output as the readiness evidence.

Every instance field is bound as a `given`, so each candidate below declares `n`
and `optimize`, even where it only uses one of them (a field no `given` names
is ignored by Savile Row, but a model that reads it must declare it).

`ragged_field`, `mixed_type_rows` and `unbindable_field_refused` cover the
reshaping run.py applies to fields an Essence' parameter file cannot take as
they are: padded ragged rows with `<field>_len`, one matrix per column of
mixed-type rows, and a clear refusal for a shape neither rule covers. Essence'
fixes a matrix's index domains in the model, so these candidates give every
instance the same row count and the same longest row.

`optimum_unproven_timeout` is an optimisation whose proof cannot finish within the
budget. Savile Row's Minion path has no optimality flag, so the runner must give
`execution_timeout` and emit no solution, not the best one found so far.

The isolation check drives the image directly under the evaluator's own
container flags instead of through a submission, as minizinc_gecode does.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "essence_prime_minion"

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

LANG = "language ESSENCE' 1.0\n"
HEAD = LANG + "given n : int(0..100)\ngiven optimize : bool\nfind x : int(0..n)\nfind y : int(0..n)\n"

GOOD = HEAD + "such that (optimize -> x + y >= n) /\\ (!optimize -> x + y = n)\n"
# The objective sits on its own line, which is what lets the runner re-solve at
# the proven optimum to enumerate.
OPTIMAL = HEAD + "DIRECTION x + y\nsuch that x + y >= n\n"
# Does not parse: Savile Row exits with an error.
MALFORMED = HEAD + "such that x + y = n blah\n"
UNSATISFIABLE = HEAD + "such that x + y = n, x = n, y = n, n > 0\n"
# Golomb rulers with 14 marks. The shortest is 127 long, so in 0..126 there is
# none, and Minion cannot show that within the budget (propagation alone proves
# it for smaller bounds). In the optimisation variant the domain admits rulers
# and Minion cannot prove the shortest one in the budget.
GOLOMB = ("find m : matrix indexed by [int(1..14)] of int(0..HIGH)\n"
          "OBJECTIVEsuch that x + y = n, m[1] = 0,\n"
          " forAll i : int(1..13) . m[i] < m[i+1],\n"
          " allDiff([m[j] - m[i] | i : int(1..13), j : int(i+1..14)])\n")
SLOW = HEAD + GOLOMB.replace("HIGH", "126").replace("OBJECTIVE", "")
SLOW_OPTIMISATION = HEAD + GOLOMB.replace("HIGH", "200").replace("OBJECTIVE", "minimising m[14]\n")

# The binding run.py adds for fields an Essence' parameter file cannot take as
# they are. A ragged list of rows binds padded, with `<field>_len` beside it.
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
RAGGED = (LANG + "given rows : matrix indexed by [int(1..2), int(1..3)] of int(0..100)\n"
          "given rows_len : matrix indexed by [int(1..2)] of int(1..3)\n"
          "find total : matrix indexed by [int(1..2)] of int(0..100)\n"
          "find last : matrix indexed by [int(1..2)] of int(0..100)\n"
          "such that\n"
          "forAll i : int(1..2) . total[i] = sum j : int(1..rows_len[i]) . rows[i, j],\n"
          "forAll i : int(1..2) . last[i] = rows[i, rows_len[i]]\n")
RAGGED_INSTANCES = [{"rows": [[4, 5], [6, 7, 8]]}, {"rows": [[9], [1, 2, 3]]}]

# Rows of one length whose columns differ in type bind as one matrix per
# column; here the third column is itself ragged, so it binds padded too.
MIXED_REFERENCE = """
# Data
items = [[True, 3, [[1, 2]]], [False, 5, [[2, 2], [3, 1]]], [True, 0, [[1, 1]]]]
# End of data
import cpmpy as cp
import json
score = cp.intvar(0, 1000, shape=len(items), name="score")
named = cp.boolvar(shape=len(items), name="named")
model = cp.Model([score[i] == value + sum(r * c for r, c in cells)
                  for i, (flag, value, cells) in enumerate(items)],
                 [named[i] == flag for i, (flag, value, cells) in enumerate(items)])
model.solve()
solution = {"score": score.value(), "named": named.value()}
print(json.dumps(solution))
"""
MIXED = (LANG + "given items_1 : matrix indexed by [int(1..3)] of bool\n"
         "given items_2 : matrix indexed by [int(1..3)] of int(0..100)\n"
         "given items_3 : matrix indexed by [int(1..3), int(1..2), int(1..2)] of int(0..100)\n"
         "given items_3_len : matrix indexed by [int(1..3)] of int(1..2)\n"
         "find score : matrix indexed by [int(1..3)] of int(0..1000)\n"
         "find named : matrix indexed by [int(1..3)] of bool\n"
         "such that\n"
         "forAll i : int(1..3) . score[i] = items_2[i]"
         " + sum k : int(1..items_3_len[i]) . items_3[i, k, 1] * items_3[i, k, 2],\n"
         "forAll i : int(1..3) . named[i] = items_1[i]\n")
MIXED_INSTANCES = [{"items": [[False, 1, [[3, 3]]], [True, 0, [[1, 1], [2, 1]]], [False, 2, [[5, 4], [1, 1]]]]}]

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
assert sorted(os.listdir("/input")) == ["model.eprime", "request.json"], "unexpected /input"
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
    (staging / "model.eprime").write_text("language ESSENCE' 1.0\n", encoding="utf-8")
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
            path = temp / f"{name}.eprime"
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
        check("minimization", OPTIMAL.replace("DIRECTION", "minimising"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("DIRECTION", "maximising"), reference=MAXIMIZING)
        # Enumeration of an optimisation goes through the fixed-objective re-run.
        check("optimum_enumeration", OPTIMAL.replace("DIRECTION", "minimising"), reference=OPTIMIZING,
              solution_limit=5)
        check("malformed_output", MALFORMED, expected={"execution_error", "invalid_output"})
        check("empty_output", UNSATISFIABLE, expected={"no_solution"})
        check("timeout_cleanup", SLOW, expected={"execution_timeout"}, execution_timeout=3)
        # Without proof the best solution found is not reported: no solution, a timeout.
        unproven = check("optimum_unproven_timeout", SLOW_OPTIMISATION, reference=OPTIMIZING,
                         expected={"execution_timeout"}, execution_timeout=6)
        results["optimum_unproven_timeout"] &= not unproven.get("solutions_checked")
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
