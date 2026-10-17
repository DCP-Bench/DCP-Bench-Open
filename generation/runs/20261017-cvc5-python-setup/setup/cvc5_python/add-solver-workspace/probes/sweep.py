import subprocess
import sys

REPO = "/home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/cvc5-python"
PROBE = "generation/runs/20261017-cvc5-python-setup/setup/cvc5_python/add-solver-workspace/probes/p3_perf.py"
JOBSHOP = "skills/add-solver/assets/toy-problems/jobshop/instances/small.json"
JOBSHOP_FT = "skills/add-solver/assets/toy-problems/jobshop/instances/ft06.json"

cases = []
configs = sys.argv[1].split(",")
which = sys.argv[2]
for c in configs:
    if which == "php":
        for n in ["6", "7", "8"]:
            cases.append(("php", c, n))
    elif which == "magic":
        for n in ["3", "4"]:
            cases.append(("magic", c, n))
    elif which == "queens":
        for n in ["8", "20", "40"]:
            cases.append(("queens", c, n))
    elif which == "jobshop":
        cases.append(("jobshop", c, JOBSHOP + ",12"))
        cases.append(("jobshop", c, JOBSHOP_FT + ",55"))
        cases.append(("jobshop", c, JOBSHOP_FT + ",54"))

for model, c, arg in cases:
    cmd = ["timeout", "150", "docker", "run", "--rm", "--network", "none",
           "-v", REPO + ":/w", "-w", "/w", "--entrypoint", "python",
           "dcp-eval/cvc5_python:v1", PROBE, model, c, arg]
    p = subprocess.run(cmd, capture_output=True, text=True)
    out = (p.stdout.strip().splitlines() or [""])[-1]
    err = p.stderr.strip().splitlines()[-1:] if p.returncode != 0 else []
    print(out if out else f"{model} {c} {arg}: exit={p.returncode} {err}", flush=True)
