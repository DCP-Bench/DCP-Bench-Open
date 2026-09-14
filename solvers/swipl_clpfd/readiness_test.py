"""Readiness checks for the swipl_clpfd integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver swipl_clpfd` runs this and keeps
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

SOLVER = "swipl_clpfd"

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

HEADER = ":- use_module(library(clpfd)).\n"
GOOD = HEADER + ("model(Instance, [X, Y], [x-X, y-Y]) :-\n"
                 "    N = Instance.n,\n"
                 "    [X, Y] ins 0..N,\n"
                 "    X + Y #= N.\n")
OPTIMAL = HEADER + ("model(Instance, [X, Y], [x-X, y-Y], OBJECTIVE(X + Y)) :-\n"
                    "    N = Instance.n,\n"
                    "    [X, Y] ins 0..N,\n"
                    "    X + Y #>= N.\n")
# Outputs that are not Name-Value pairs: the driver must refuse them rather than
# print something the evaluator would have to guess at.
MALFORMED = HEADER + "model(_, [], not_a_pair_list).\n"
UNSATISFIABLE = HEADER + ("model(_, [X], [x-X, y-2]) :-\n"
                          "    X in 0..1,\n"
                          "    X #= 5.\n")
SLOW = HEADER + ("model(_, [X], [x-X, y-0]) :-\n"
                 "    sleep(120),\n"
                 "    X in 0..1.\n")
# Every claim the evaluator makes about the sandbox, asserted from inside it:
# an unprivileged user, no dataset, only the two staged files, a read-only root
# and no network.
ISOLATED = HEADER + (
    ":- use_module(library(socket)).\n"
    "model(Instance, [X, Y], [x-X, y-Y]) :-\n"
    "    read_file_to_string('/proc/self/status', Status, []),\n"
    "    split_string(Status, '\\n', '', Lines),\n"
    "    memberchk(\"Uid:\\t65534\\t65534\\t65534\\t65534\", Lines),\n"
    "    \\+ exists_directory('/dataset'),\n"
    "    directory_files('/input', Files),\n"
    "    msort(Files, ['.', '..', 'model.pl', 'request.json']),\n"
    "    \\+ catch(open('/probe.txt', write, _), _, fail),\n"
    "    \\+ catch(tcp_connect('1.1.1.1':443, _, []), _, fail),\n"
    "    N = Instance.n,\n"
    "    [X, Y] ins 0..N,\n"
    "    X + Y #= N.\n")


def main():
    results = {}
    with tempfile.TemporaryDirectory(prefix="dcp_readiness_") as directory:
        temp = Path(directory)

        def candidate(name, source):
            path = temp / name
            path.write_text(source, encoding="utf-8")
            return path

        def check(name, source, reference=REFERENCE, expected=None, **kwargs):
            result = evaluate(candidate(f"{name}.pl", source), "readiness", SOLVER,
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
