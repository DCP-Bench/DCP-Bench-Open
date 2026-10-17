import sys
import time
import json
from cvc5.pythonic import *

TLIMIT = 60000  # ms per check


def make_solver(config):
    if config == "default":
        s = Solver()
    elif config == "qf_lia":
        s = SolverFor("QF_LIA")
    elif config == "qf_lia_nobrab":
        s = SolverFor("QF_LIA")
        s.set("arith-brab", False)
    elif config == "qf_lia_noprop":
        s = SolverFor("QF_LIA")
        s.set("arith-prop", "none")
    elif config == "qf_lia_nosatrand":
        s = SolverFor("QF_LIA")
        s.set("sat-random-seed", 7)
    else:
        raise SystemExit("unknown config " + config)
    s.set("tlimit-per", TLIMIT)
    return s


def php(n, config):
    # pigeonhole: n+1 pigeons into n holes, unsat
    p = [Int(f"p{i}") for i in range(n + 1)]
    s = make_solver(config)
    s.add(*[And(v >= 0, v < n) for v in p])
    s.add(Distinct(p))
    return s, "unsat" if True else ""


def magic(n, config):
    cells = [[Int(f"c{i}_{j}") for j in range(n)] for i in range(n)]
    flat = [c for row in cells for c in row]
    target = n * (n * n + 1) // 2
    s = make_solver(config)
    s.add(*[And(c >= 1, c <= n * n) for c in flat])
    s.add(Distinct(flat))
    for row in cells:
        s.add(Sum(row) == target)
    for j in range(n):
        s.add(Sum([cells[i][j] for i in range(n)]) == target)
    s.add(Sum([cells[i][i] for i in range(n)]) == target)
    s.add(Sum([cells[i][n - 1 - i] for i in range(n)]) == target)
    return s, "sat"


def queens(n, config):
    q = [Int(f"q{i}") for i in range(n)]
    s = make_solver(config)
    s.add(*[And(v >= 0, v < n) for v in q])
    s.add(Distinct(q))
    s.add(Distinct([q[i] + i for i in range(n)]))
    s.add(Distinct([q[i] - i for i in range(n)]))
    return s, "sat"


def jobshop(path, horizon, config):
    with open(path) as f:
        data = json.load(f)
    jobs = data["jobs"]
    ops = {}
    s = make_solver(config)
    starts = {}
    for j, job in enumerate(jobs):
        for k, (m, d) in enumerate(job):
            st = Int(f"s_{j}_{k}")
            starts[(j, k)] = (st, d, m)
            s.add(st >= 0, st + d <= horizon)
    for j, job in enumerate(jobs):
        for k in range(len(job) - 1):
            a, da, _ = starts[(j, k)]
            b, _, _ = starts[(j, k + 1)]
            s.add(b >= a + da)
    machines = {}
    for key, (st, d, m) in starts.items():
        machines.setdefault(m, []).append((st, d))
    for m, tasks in machines.items():
        for x in range(len(tasks)):
            for y in range(x + 1, len(tasks)):
                sx, dx = tasks[x]
                sy, dy = tasks[y]
                s.add(Or(sx + dx <= sy, sy + dy <= sx))
    return s, "sat"


if __name__ == "__main__":
    model = sys.argv[1]
    config = sys.argv[2]
    arg = sys.argv[3] if len(sys.argv) > 3 else None
    t0 = time.time()
    if model == "php":
        s, _ = php(int(arg), config)
    elif model == "magic":
        s, _ = magic(int(arg), config)
    elif model == "queens":
        s, _ = queens(int(arg), config)
    elif model == "jobshop":
        path, horizon = arg.split(",")
        s, _ = jobshop(path, int(horizon), config)
    else:
        raise SystemExit("unknown model")
    build = time.time() - t0
    r = s.check()
    total = time.time() - t0
    extra = ""
    if r == sat:
        extra = "model ok"
    print(f"{model} {arg} {config}: {r} reason={s.reason_unknown() if r == unknown else '-'} build={build:.2f}s total={total:.2f}s {extra}")
