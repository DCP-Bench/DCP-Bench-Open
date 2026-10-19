"""Job shop: each job is a sequence of (machine, duration) tasks; a machine runs one
task at a time. Minimise the makespan."""
from pycsp3 import *

jobs = [
    [(0, 3), (1, 2), (2, 2)],
    [(0, 2), (2, 1), (1, 4)],
    [(1, 4), (2, 3)],
]
horizon = sum(d for job in jobs for _, d in job)
tasks = [(j, k) for j, job in enumerate(jobs) for k in range(len(job))]
# the machines are the ones the tasks name, so any number of machines works
machines = sorted({m for job in jobs for m, _ in job})

# start[t] is the start time of task tasks[t]; one flat VarArray, so ids are automatic
start = VarArray(size=len(tasks), dom=range(horizon + 1))
index = {t: i for i, t in enumerate(tasks)}
makespan = Var(dom=range(horizon + 1))

satisfy(
    # the tasks of a job run in order
    [start[index[j, k]] + jobs[j][k][1] <= start[index[j, k + 1]]
     for j in range(len(jobs)) for k in range(len(jobs[j]) - 1)],
    # a machine runs one task at a time
    [NoOverlap(origins=[start[index[t]] for t in tasks if jobs[t[0]][t[1]][0] == m],
               lengths=[jobs[t[0]][t[1]][1] for t in tasks if jobs[t[0]][t[1]][0] == m])
     for m in machines],
    # the makespan is the end of the last task of each job
    makespan == Maximum(start[index[j, len(jobs[j]) - 1]] + jobs[j][-1][1] for j in range(len(jobs))),
)
minimize(makespan)

status = solve()
if status is OPTIMUM:
    print("Makespan:", bound())
    for (j, k), s in zip(tasks, values(start)):
        print(f"job {j} task {k}: machine {jobs[j][k][0]}, start {s}")
else:
    print("Status:", status)
