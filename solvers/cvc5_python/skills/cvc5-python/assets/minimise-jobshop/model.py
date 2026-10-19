"""Minimise: job-shop makespan, read from a JSON file (default data.json).

Data: {"jobs": [[[machine, duration], ...], ...]}; each job visits its
operations in the listed order.

Shows: start-time variables, precedence constraints, no-overlap with a
pairwise disjunction per pair of operations on one machine, minimisation
by tightening the makespan bound until unsat.
"""
import json
import sys

from cvc5.pythonic import *

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    jobs = json.load(f)["jobs"]

horizon = sum(d for job in jobs for _, d in job)  # safe upper bound on any start
start = {}
s = SolverFor("QF_LIA")
for j, job in enumerate(jobs):
    for k, (machine, dur) in enumerate(job):
        start[j, k] = Int(f"s_{j}_{k}")
        s.add(start[j, k] >= 0, start[j, k] + dur <= horizon)
    for k in range(len(job) - 1):
        s.add(start[j, k + 1] >= start[j, k] + job[k][1])

by_machine = {}
for j, job in enumerate(jobs):
    for k, (machine, dur) in enumerate(job):
        by_machine.setdefault(machine, []).append((start[j, k], dur))
for ops in by_machine.values():
    for a in range(len(ops)):
        for b in range(a + 1, len(ops)):
            (sa, da), (sb, db) = ops[a], ops[b]
            s.add(Or(sa + da <= sb, sb + db <= sa))

makespan = Int("makespan")
for j, job in enumerate(jobs):
    k = len(job) - 1
    s.add(makespan >= start[j, k] + job[k][1])

best, best_starts = None, None
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    best = m.eval(makespan, model_completion=True).as_long()
    best_starts = {key: m.eval(v, model_completion=True).as_long() for key, v in start.items()}
    s.add(makespan < best)

if result == unknown:
    print(f"undecided: {s.reason_unknown()}; best so far {best}")
else:
    print(f"Optimal makespan: {best}")
    for j, job in enumerate(jobs):
        row = [f"m{machine}@{best_starts[j, k]}" for k, (machine, _) in enumerate(job)]
        print(f"job {j}: " + " ".join(row))
