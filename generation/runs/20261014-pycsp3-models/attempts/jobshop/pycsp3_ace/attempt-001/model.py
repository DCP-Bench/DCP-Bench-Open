# Job shop: schedule the tasks of each job in their given order, each task on its machine, with no two tasks on one machine at the same time, so as to minimise the makespan.
from pycsp3 import *

jobs_data = data.jobs_data
num_jobs = len(jobs_data)
horizon = sum(duration for job in jobs_data for (_, duration) in job)

# offset[j] is the position of the first task of job j in the flat list of tasks
offset = [sum(len(jobs_data[i]) for i in range(j)) for j in range(num_jobs)]
num_tasks = sum(len(job) for job in jobs_data)

# start[t] is the start time of task t, tasks numbered job by job in their order
start = VarArray(size=num_tasks, dom=range(horizon + 1))
# makespan is the time when all jobs are completed
makespan = Var(dom=range(horizon + 1))

satisfy(
    # no task of a job can start until the previous task of that job is completed
    [start[offset[j] + k + 1] >= start[offset[j] + k] + jobs_data[j][k][1] for j in range(num_jobs) for k in range(len(jobs_data[j]) - 1)],
    # the makespan is at least the completion time of the last task of each job
    [makespan >= start[offset[j] + len(jobs_data[j]) - 1] + jobs_data[j][-1][1] for j in range(num_jobs)],
)

machines = sorted({machine for job in jobs_data for (machine, _) in job})
for m in machines:
    tasks = [(offset[j] + k, jobs_data[j][k][1]) for j in range(num_jobs) for k in range(len(jobs_data[j])) if jobs_data[j][k][0] == m]
    satisfy(
        # a machine can only work on one task at a time, and a task once started runs to completion
        NoOverlap(origins=[start[t] for t, _ in tasks], lengths=[length for _, length in tasks]),
    )

# minimise the time it takes for all the jobs to be completed
minimize(makespan)
