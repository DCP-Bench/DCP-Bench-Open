"""Job shop: minimise the makespan. Each job visits its machines in order; each machine runs
one task at a time.

Each job is a list of (machine, duration) pairs in processing order.
"""
import cpmpy as cp
from cpmpy.solvers.solver_interface import ExitStatus

jobs = [
    [(0, 3), (1, 2), (2, 2)],   # job 0
    [(0, 2), (2, 1), (1, 4)],   # job 1
    [(1, 4), (2, 3), (0, 1)],   # job 2
]
horizon = sum(d for job in jobs for _, d in job)  # safe upper bound on every finish time

start = [[cp.intvar(0, horizon, name=f"s{j}{k}") for k in range(len(job))]
         for j, job in enumerate(jobs)]
end = [[cp.intvar(0, horizon, name=f"e{j}{k}") for k in range(len(job))]
       for j, job in enumerate(jobs)]
makespan = cp.intvar(0, horizon, name="makespan")

model = cp.Model()
tasks_on = {}  # machine -> list of (start, duration, end) of the tasks it runs
for j, job in enumerate(jobs):
    for k, (machine, duration) in enumerate(job):
        model += end[j][k] == start[j][k] + duration
        model += makespan >= end[j][k]
        if k + 1 < len(job):
            model += end[j][k] <= start[j][k + 1]  # the job's tasks run in order
        tasks_on.setdefault(machine, []).append((start[j][k], duration, end[j][k]))

for tasks in tasks_on.values():
    s, d, e = (list(column) for column in zip(*tasks))
    model += cp.NoOverlap(s, d, e)  # one task at a time on this machine

model.minimize(makespan)

if model.solve():
    for j, job in enumerate(jobs):
        row = ", ".join(f"M{m} {int(start[j][k].value())}-{int(end[j][k].value())}"
                        for k, (m, _) in enumerate(job))
        print(f"job {j}: {row}")
    print("Makespan:", int(makespan.value()))
    print("Proven optimal:", model.status().exitstatus == ExitStatus.OPTIMAL)
else:
    print("No schedule")
