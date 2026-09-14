"""Readiness checks for the clingo_asp integration and its current image.

Drives the repository evaluator against real containers, prints a JSON object
mapping check name to Boolean on stdout, and exits nonzero if any check failed.
`python -m generation.readiness check --solver clingo_asp` runs this and keeps
its output as the readiness evidence.

One check differs from the Python integrations by necessity. ASP is declarative
and this image's clingo has no Python scripting (`#script(python)` raises
"python support not available"), so a submission cannot inspect its own
container the way a Python candidate does. The isolation check therefore drives
the image directly under the evaluator's own container flags instead of through
a submission. It tests the same guarantees on the same image; it just cannot
route them through the ASP entrypoint.
"""
import json
from pathlib import Path
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from evaluation import evaluate
from evaluation.execution import image_identity, integration, run_process
from evaluation.results import EvaluationError

SOLVER = "clingo_asp"

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

GOOD = """val(0..N) :- n(N).
1 { xv(X) : val(X) } 1.
1 { yv(Y) : val(Y) } 1.
:- xv(X), yv(Y), n(N), X + Y != N.
x(X) :- xv(X).
y(Y) :- yv(Y).
#show x/1.
#show y/1.
"""
OPTIMAL = """val(0..N) :- n(N).
1 { xv(X) : val(X) } 1.
1 { yv(Y) : val(Y) } 1.
:- xv(X), yv(Y), n(N), X + Y < N.
x(X) :- xv(X).
y(Y) :- yv(Y).
#DIRECTION { X + Y : xv(X), yv(Y) }.
#show x/1.
#show y/1.
"""
# Shows nothing, so the runner cannot tell what the declared outputs are.
MALFORMED = "val(0..N) :- n(N).\n1 { xv(X) : val(X) } 1.\n"
UNSATISFIABLE = "x(0).\ny(0).\n:- #true.\n#show x/1.\n#show y/1.\n"
# Pigeonhole is unsatisfiable and exponentially hard, so it exhausts any budget.
SLOW = """hole(1..15).
pigeon(1..16).
1 { inside(P,H) : hole(H) } 1 :- pigeon(P).
:- inside(P1,H), inside(P2,H), P1 < P2.
x(0).
y(2).
#show x/1.
#show y/1.
"""

ISOLATION_PROBE = """import os, socket
probe = socket.socket(); probe.settimeout(0.5)
assert os.getuid() != 0, "container runs as root"
assert sorted(os.listdir("/input")) == ["model.lp", "request.json"], "unexpected /input"
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
    (staging / "model.lp").write_text("#show x/1.\n", encoding="utf-8")
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
            path = temp / f"{name}.lp"
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
