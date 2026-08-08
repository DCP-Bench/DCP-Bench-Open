
import cpmpy as cp
import json

jobs_data = [
    [(0, 3), (1, 2), (2, 2)],  
    [(0, 2), (2, 1), (1, 4)],  
    [(1, 4), (2, 3)]           
]

# Build all_tasks list: (job_id, task_in_job, machine_id, duration)
all_tasks = []
for job_idx, job in enumerate(jobs_data):
    for task_in_job, (machine, duration) in enumerate(job):
        all_tasks.append((job_idx, task_in_job, machine, duration))

n_tasks = len(all_tasks)
total_duration = sum(task[3] for task in all_tasks)
starts = [cp.intvar(0, total_duration) for _ in range(n_tasks)]

model = cp.Model()

# Job sequence constraints
job_indices = [[] for _ in range(len(jobs_data))]
for idx, task in enumerate(all_tasks):
    job_id = task[0]
    job_indices[job_id].append(idx)

for job_id in range(len(jobs_data)):
    indices = job_indices[job_id]
    for i in range(1, len(indices)):
        prev_idx = indices[i-1]
        curr_idx = indices[i]
        prev_duration = all_tasks[prev_idx][3]
        model += (starts[curr_idx] >= starts[prev_idx] + prev_duration)

# Machine constraints using NoOverlap
machines = set(task[2] for task in all_tasks)
for m in machines:
    # Collect tasks for this machine
    indices = [idx for idx, task in enumerate(all_tasks) if task[2] == m]
    durations = [all_tasks[idx][3] for idx in indices]
    starts_m = [starts[idx] for idx in indices]
    ends_m = [starts[idx] + duration for idx, duration in zip(indices, durations)]
    model += cp.NoOverlap(starts_m, durations, ends_m)

# Objective: minimize makespan
ends = [starts[i] + task[3] for i, task in enumerate(all_tasks)]
model.minimize(cp.max(ends))

# Solve and output
if model.solve():
    solution = {'makespan': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
