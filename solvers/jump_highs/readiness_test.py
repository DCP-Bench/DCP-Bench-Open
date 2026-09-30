"""Readiness checks for the jump_highs integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver jump_highs` runs this and keeps
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

SOLVER = "jump_highs"

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

GOOD = """using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    @constraint(model, x + y == n)
    return model, Dict("x" => x, "y" => y)
end
"""
OPTIMAL = """using JuMP

function build(instance)
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    @constraint(model, x + y >= n)
    @objective(model, SENSE, x + y)
    return model, Dict("x" => x, "y" => y)
end
"""
# A free auxiliary variable doubles every solution unless distinctness is
# measured over the declared outputs only.
AUXILIARY = GOOD.replace("    @constraint(model, x + y == n)\n",
                         "    @constraint(model, x + y == n)\n    @variable(model, z, Bin)\n")
# Outputs that are not a dictionary: the driver must refuse them rather than
# print something the evaluator would have to guess at.
MALFORMED = """using JuMP

function build(instance)
    return Model(), "not a dictionary"
end
"""
UNSATISFIABLE = """using JuMP

function build(instance)
    model = Model()
    @variable(model, 0 <= x <= 1, Int)
    @constraint(model, x == 5)
    return model, Dict("x" => x, "y" => 2)
end
"""
SLOW = """using JuMP

function build(instance)
    while true
    end
end
"""
# Every claim the evaluator makes about the sandbox, asserted from inside it: an
# unprivileged user, no dataset, only the two staged files, a read-only root and
# no network. A failed claim throws, which the evaluator reports as an error.
ISOLATED = """using JuMP
using Sockets

function build(instance)
    status = read("/proc/self/status", String)
    occursin("Uid:\\t65534\\t65534\\t65534\\t65534", status) || error("not the unprivileged user")
    isdir("/dataset") && error("the dataset is visible")
    sort(readdir("/input")) == ["model.jl", "request.json"] || error("unexpected files in /input")
    writable = try
        open(io -> nothing, "/probe.txt", "w")
        true
    catch
        false
    end
    writable && error("the root file system is writable")
    reachable = try
        close(connect(ip"1.1.1.1", 443))
        true
    catch
        false
    end
    reachable && error("the network is reachable")
    n = instance["n"]
    model = Model()
    @variable(model, 0 <= x <= n, Int)
    @variable(model, 0 <= y <= n, Int)
    @constraint(model, x + y == n)
    return model, Dict("x" => x, "y" => y)
end
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
            result = evaluate(candidate(f"{name}.jl", source), "readiness", SOLVER,
                              reference_source=reference, **kwargs)
            results[name] = result["accepted"] if expected is None else (
                not result["accepted"] and result["reason"] in expected)
            return result

        def exhausted(name, source, solutions):
            result = check(name, source, solution_limit=5)
            results[name] = (results[name]
                             and result["instances"][0]["solutions_received"] == solutions
                             and result["instances"][0]["runner_status"]["status"] == "complete")

        check("satisfaction", GOOD)
        check("changed_instances", GOOD, instances=[{"n": 3, "optimize": False}], instance_count=2)
        check("enumeration", GOOD, solution_limit=3)
        # x+y==2 has exactly three solutions, so asking for more must come back
        # as exhaustion rather than as a shortfall the evaluator would reject.
        exhausted("exhausted_enumeration", GOOD, 3)
        exhausted("distinct_declared_outputs", AUXILIARY, 3)
        check("minimization", OPTIMAL.replace("SENSE", "Min"), reference=OPTIMIZING)
        check("maximization", OPTIMAL.replace("SENSE", "Max"), reference=MAXIMIZING)
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
