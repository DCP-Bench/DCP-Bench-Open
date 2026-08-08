
import cpmpy as cp
import json

# Data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

# Flatten tasks and collect meta-information
total_tasks = sum(len(job) for job in jobs_data)
machines = []
durations = []
job_of = []        # job index for each flattened task
task_pos = []      # position in job for each flattened task

for j, job in enumerate(jobs_data):
    for tpos, (m, d) in enumerate(job):
        machines.append(m)
        durations.append(d)
        job_of.append(j)
        task_pos.append(tpos)

horizon = sum(durations)  # upper bound on makespan

# Model definition
model = cp.Model()

# Decision Variables
starts = cp.intvar(0, horizon, shape=total_tasks, name="start")
ends = cp.intvar(0, horizon, shape=total_tasks, name="end")
makespan = cp.intvar(0, horizon, name="makespan")

# Constraints
# Link start + duration = end for each task
for i in range(total_tasks):
    model += (ends[i] == starts[i] + durations[i])

# Precedence constraints: tasks within each job must follow order
# For each job, enforce start(curr) >= end(prev)
index = 0
for j, job in enumerate(jobs_data):
    for tpos in range(1, len(job)):
        prev_idx = index + tpos - 1
        curr_idx = index + tpos
        model += (starts[curr_idx] >= ends[prev_idx])
    index += len(job)

# No-overlap constraints on each machine
num_machines = max(machines) + 1
for m in range(num_machines):
    idxs = [i for i, mm in enumerate(machines) if mm == m]
    if len(idxs) > 1:
        start_m = [starts[i] for i in idxs]
        dur_m = [durations[i] for i in idxs]
        end_m = [ends[i] for i in idxs]
        model += cp.NoOverlap(start_m, dur_m, end_m)
    # if only 0 or 1 task on machine, no constraint needed

# Makespan: must be at least the end time of every task
for i in range(total_tasks):
    model += (makespan >= ends[i])

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'makespan': int(model.objective_value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
