"""Project scheduling with a renewable resource: minimise the makespan.

Usage: python3 model.py tasks.json
"""
import json
import sys

import cpmpy as cp
from cpmpy.solvers.solver_interface import ExitStatus

with open(sys.argv[1] if len(sys.argv) > 1 else "tasks.json") as f:
    data = json.load(f)
tasks, capacity = data["tasks"], data["capacity"]
duration = [t["duration"] for t in tasks]
demand = [t["demand"] for t in tasks]
horizon = sum(duration)  # a safe upper bound on the finish time

start = cp.intvar(0, horizon, shape=len(tasks), name="start")
end = cp.intvar(0, horizon, shape=len(tasks), name="end")
makespan = cp.intvar(0, horizon, name="makespan")

model = cp.Model(
    [end[i] == start[i] + duration[i] for i in range(len(tasks))],
    [start[a] + duration[a] <= start[b] for a, b in data["precedence"]],  # a finishes before b starts
    cp.Cumulative(start, duration, end=end, demand=demand, capacity=capacity),
    [makespan >= end[i] for i in range(len(tasks))],
)
model.minimize(makespan)

if model.solve():
    s = [int(v.value()) for v in start]
    # Independent check: the resource is never over capacity at any time unit.
    for t in range(horizon):
        used = sum(demand[i] for i in range(len(tasks)) if s[i] <= t < s[i] + duration[i])
        assert used <= capacity, f"capacity exceeded at time {t}"
    for i, task in enumerate(tasks):
        print(f"{task['name']:8s} start {s[i]:2d} end {s[i] + duration[i]:2d}")
    print("Makespan:", int(makespan.value()))
    print("Proven optimal:", model.status().exitstatus == ExitStatus.OPTIMAL)
else:
    print("No schedule")
