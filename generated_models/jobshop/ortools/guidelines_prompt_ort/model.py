
from ortools.sat.python import cp_model
import json
import collections

# Input data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# Compute an upper bound on the horizon (sum of all durations)
horizon = sum(duration for job in jobs_data for (_, duration) in job)

# Model definition
model = cp_model.CpModel()

# Decision variables: for each job and each of its tasks, define start, end, and interval
all_tasks = {}
machine_to_intervals = collections.defaultdict(list)

for job_id, job in enumerate(jobs_data):
    for task_id, (machine_id, duration) in enumerate(job):
        suffix = f'_{job_id}_{task_id}'
        start_var = model.NewIntVar(0, horizon, 'start' + suffix)
        end_var = model.NewIntVar(0, horizon, 'end' + suffix)
        interval_var = model.NewIntervalVar(start_var, duration, end_var, 'interval' + suffix)
        all_tasks[(job_id, task_id)] = (start_var, end_var, interval_var)
        machine_to_intervals[machine_id].append(interval_var)

# Constraints: no overlap on the same machine
for machine_id, intervals in machine_to_intervals.items():
    model.AddNoOverlap(intervals)

# Constraints: task ordering within each job
for job_id, job in enumerate(jobs_data):
    for task_id in range(1, len(job)):
        prev_end = all_tasks[(job_id, task_id - 1)][1]
        curr_start = all_tasks[(job_id, task_id)][0]
        model.Add(curr_start >= prev_end)

# Makespan variable
makespan = model.NewIntVar(0, horizon, 'makespan')
# All jobs must finish by makespan
for job_id, job in enumerate(jobs_data):
    last_end = all_tasks[(job_id, len(job) - 1)][1]
    model.Add(last_end <= makespan)

# Objective: minimize makespan
model.Minimize(makespan)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

# Print solution in JSON format
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'makespan': solver.Value(makespan)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
