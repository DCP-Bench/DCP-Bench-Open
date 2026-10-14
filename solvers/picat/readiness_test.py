"""Readiness checks for the picat integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver picat` runs this and keeps its
output as the readiness evidence.

Every check runs the cp module; the sat_* checks repeat satisfaction,
enumeration and minimisation with `import sat.`, because the driver reaches
the solver through whichever module the submission imported and the two must
both work.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity
from evaluation.results import EvaluationError

SOLVER = "picat"

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

GOOD = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].
"""
# The objective is an expression, so the driver's own objective variable is
# exercised as well as the direction.
OPTIMAL = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #>= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [$OBJECTIVE(X + Y)].
"""
# A free auxiliary variable doubles every solution unless distinctness is
# measured over the declared outputs only.
AUXILIARY = """import cp.

model(Data, Vars, Outputs, Options) =>
    N = Data.get(n),
    [X, Y] :: 0..N,
    Z :: 0..1,
    X + Y #= N,
    Vars = [X, Y, Z],
    Outputs = [x = X, y = Y],
    Options = [].
"""
# Outputs that are not Name = Value pairs: the driver must refuse them rather
# than print something the evaluator would have to guess at.
MALFORMED = """import cp.

model(_Data, Vars, Outputs, Options) =>
    Vars = [],
    Outputs = not_a_pair_list,
    Options = [].
"""
UNSATISFIABLE = """import cp.

model(_Data, Vars, Outputs, Options) =>
    X :: 0..1,
    X #= 5,
    Vars = [X],
    Outputs = [x = X, y = 2],
    Options = [].
"""
SLOW = """import cp.

model(_Data, Vars, Outputs, Options) =>
    spin(0),
    X :: 0..1,
    Vars = [X],
    Outputs = [x = X, y = 0],
    Options = [].

spin(N) => spin(N + 1).
"""
# Every claim the evaluator makes about the sandbox, asserted from inside it:
# an unprivileged user, no dataset, only the two staged files, a read-only root
# and no network. Picat has no sockets, so the network probe runs through the
# image's Python, started with command/1.
ISOLATED = r"""import cp.
import os.

model(Data, Vars, Outputs, Options) =>
    Status = read_file_lines("/proc/self/status"),
    membchk("Uid:\t65534\t65534\t65534\t65534", Status),
    not exists("/dataset"),
    sort(listdir("/input")) == sort([".", "..", "model.pi", "request.json"]),
    not writable("/probe.txt"),
    command("python -c \"import socket, sys; s = socket.socket(); s.settimeout(0.5); sys.exit(0 if s.connect_ex(('1.1.1.1', 443)) else 1)\"") == 0,
    N = Data.get(n),
    [X, Y] :: 0..N,
    X + Y #= N,
    Vars = [X, Y],
    Outputs = [x = X, y = Y],
    Options = [].

writable(Path) => catch((FD = open(Path, write), close(FD)), _, fail).
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
            result = evaluate(candidate(f"{name}.pi", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        def exhausted(name, source, solutions):
            result = check(name, source, solution_limit=5)
            results[name] = (results[name]
                             and result["instances"][0]["solutions_received"] == solutions
                             and result["instances"][0]["runner_status"]["status"] == "complete")

        sat = lambda source: source.replace("import cp.", "import sat.")

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back
        # as exhaustion rather than as a shortfall the evaluator would reject.
        exhausted("exhausted_enumeration", GOOD, 3)
        exhausted("distinct_declared_outputs", AUXILIARY, 3)
        check("minimization", OPTIMAL.replace("OBJECTIVE", "min"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("OBJECTIVE", "max"), reference=MAXIMIZING)
        check("sat_satisfaction", sat(GOOD), instances=[{"n": 3, "optimize": False}], instance_count=2)
        exhausted("sat_exhausted_enumeration", sat(AUXILIARY), 3)
        check("sat_minimization", sat(OPTIMAL.replace("OBJECTIVE", "min")), reference=OPTIMIZING)
        check("sat_maximization", sat(OPTIMAL.replace("OBJECTIVE", "max")), reference=MAXIMIZING)
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
