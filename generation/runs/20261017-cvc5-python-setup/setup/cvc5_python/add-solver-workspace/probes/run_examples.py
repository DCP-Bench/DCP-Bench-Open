import subprocess
import sys
import time

REPO = "/home/tias/research/kostis/DCP-Bench-Open/.claude/worktrees/cvc5-python"
ASSETS = "solvers/cvc5_python/skills/cvc5-python/assets/"

for name in sys.argv[1:]:
    t0 = time.time()
    cmd = ["timeout", "200", "docker", "run", "--rm", "--network", "none",
           "-v", REPO + ":/w", "-w", "/w/" + ASSETS + name, "--entrypoint", "python",
           "dcp-eval/cvc5_python:v1", "model.py"]
    p = subprocess.run(cmd, capture_output=True, text=True)
    dt = time.time() - t0
    print(f"== {name} exit={p.returncode} wall={dt:.2f}s")
    print(p.stdout.rstrip())
    if p.stderr.strip():
        print("STDERR:", p.stderr.strip()[-600:])
