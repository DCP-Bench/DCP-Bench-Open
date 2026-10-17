import json
import sys

import mip

jobs = json.load(open(sys.argv[1]))["jobs"]

# a horizon that every schedule fits in: all tasks run one after another
H = sum(d for job in jobs for _, d in job)

m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")
m.verbose = 0
m.max_mip_gap = 0.0
m.max_mip_gap_abs = 0.0

# s[j][k] = start time of task k of job j
s = [[m.add_var(f"s_{j}_{k}", var_type=mip.INTEGER, lb=0, ub=H) for k in range(len(job))]
     for j, job in enumerate(jobs)]
makespan = m.add_var("makespan", var_type=mip.INTEGER, lb=0, ub=H)

# tasks of a job run in order, and the makespan is at least each task's end
for j, job in enumerate(jobs):
    for k, (_, d) in enumerate(job):
        if k + 1 < len(job):
            m += s[j][k + 1] >= s[j][k] + d
        m += makespan >= s[j][k] + d

# tasks on one machine do not overlap: a binary picks which one goes first
by_machine = {}
for j, job in enumerate(jobs):
    for k, (mach, d) in enumerate(job):
        by_machine.setdefault(mach, []).append((j, k, d))

for tasks in by_machine.values():
    for a in range(len(tasks)):
        for b in range(a + 1, len(tasks)):
            j1, k1, d1 = tasks[a]
            j2, k2, d2 = tasks[b]
            if j1 == j2:
                continue  # the job's order already separates them
            o = m.add_var(f"o_{j1}_{k1}_{j2}_{k2}", var_type=mip.BINARY)
            # o = 0: task a before task b
            m += s[j2][k2] >= s[j1][k1] + d1 - H * o
            # o = 1: task b before task a
            m += s[j1][k1] >= s[j2][k2] + d2 - H * (1 - o)

m.objective = makespan

status = m.optimize(max_seconds=600)
if status != mip.OptimizationStatus.OPTIMAL:
    raise SystemExit(f"Status: {status.name}")

start = [[round(s[j][k].x) for k in range(len(job))] for j, job in enumerate(jobs)]
print(json.dumps({"start": start}))
