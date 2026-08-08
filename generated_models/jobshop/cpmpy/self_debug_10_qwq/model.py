
import cpmpy as cp
import json
from collections import defaultdict

jobs_data = [
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# Compute total duration for variable bounds
total_duration = sum(d for job in jobs_data for (_, d) in job)

# Initialize variables and tasks
tasks = []  # Structure: list of jobs, each job is a list of (machine, duration, start, end)
all_tasks = []  # Flat list of all tasks for machine grouping

for job_id, job in enumerate(jobs_data):
    job_tasks = []
    for task_id, (machine, duration) in enumerate(job):
        start = cp.intvar(0, total_duration, name=f"s_{job_id}_{task_id}")
        end = start + duration
        job_tasks.append((machine, duration, start, end))
        all_tasks.append((machine, duration, start, end))
    tasks.append(job_tasks)

model = cp.Model()

# Add sequence constraints for each job
for job in tasks:
    for i in range(len(job) - 1):
        current = job[i]
        next_task = job[i+1]
        model += current[3] <= next_task[2]  # current end <= next start

# Group tasks by machine and add no-overlap constraints
machine_tasks = defaultdict(list)
for task in all_tasks:
    m, duration, start, end = task
    machine_tasks[m].append((start, duration, end))

for m in machine_tasks:
    tasks_on_m = machine_tasks[m]
    starts = [t[0] for t in tasks_on_m]
    durations = [t[1] for t in tasks_on_m]
    ends = [t[2] for t in tasks_on_m]
    model += cp.NoOverlap(starts, durations, ends)

# Objective: minimize makespan (max end time)
ends_all = [t[3] for t in all_tasks]
makespan_var = cp.Maximum(ends_all)
model.minimize(makespan_var)

# Solve and print
if model.solve():
    solution = {'makespan': int(makespan_var.value())}
    print(json.dumps(solution))
else:
    print("No solution found.")
