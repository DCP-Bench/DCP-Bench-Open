"""Minimise the makespan of tasks that share a renewable resource, read from
a JSON file (default data.json).

Data: {"capacity": C, "tasks": [{"dur": d, "demand": r}, ...]}

Shows: a cumulative constraint written by time point: at every time t the
sum of demands of the running tasks is at most the capacity, with
Sum(If(...)) as the 0/1 indicator.
"""
import json
import sys

from cvc5.pythonic import *

path = sys.argv[1] if len(sys.argv) > 1 else "data.json"
with open(path) as f:
    data = json.load(f)
capacity, tasks = data["capacity"], data["tasks"]
horizon = sum(t["dur"] for t in tasks)  # every task fits before this

start = [Int(f"start_{i}") for i in range(len(tasks))]
makespan = Int("makespan")

s = SolverFor("QF_LIA")
for i, t in enumerate(tasks):
    s.add(start[i] >= 0, start[i] + t["dur"] <= makespan)
s.add(makespan <= horizon)

for time in range(horizon):
    running = [
        If(And(start[i] <= time, time < start[i] + t["dur"]), t["demand"], 0)
        for i, t in enumerate(tasks)
    ]
    s.add(Sum(running) <= capacity)

best, best_starts = None, None
while True:
    result = s.check()
    if result != sat:
        break
    m = s.model()
    best = m.eval(makespan, model_completion=True).as_long()
    best_starts = [m.eval(v, model_completion=True).as_long() for v in start]
    s.add(makespan < best)

if result == unknown:
    print(f"undecided: {s.reason_unknown()}; best so far {best}")
else:
    print(f"Optimal makespan: {best}")
    print("starts:", best_starts)
