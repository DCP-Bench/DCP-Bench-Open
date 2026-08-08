import json
from ortools.sat.python import cp_model

# ----------------------
# 1. Input data (exact)
# ----------------------
jobs_data = [  # (job_id, task_id) -> (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# ----------------------
# 2. Derived sets & constants
# ----------------------
num_jobs = len(jobs_data)
all_jobs = range(num_jobs)
num_machines = 1 + max(machine for job in jobs_data for machine, _ in job)
all_machines = range(num_machines)

# Upper bound for the makespan (sum of all durations)
horizon = sum(duration for job in jobs_data for _, duration in job)

# ----------------------
# 3. Model
# ----------------------
model = cp_model.CpModel()

# Dictionaries to keep useful handles
start_vars = {}                       # (j, t) -> start IntVar
end_exprs = {}                        # (j, t) -> linear expression for end
intervals_per_machine = {m: [] for m in all_machines}

# 3.1 Create variables and intervals for each task
for j in all_jobs:
    for t, (machine, duration) in enumerate(jobs_data[j]):
        suffix = f'_{j}_{t}'
        start = model.NewIntVar(0, horizon - duration, f'start{suffix}')
        interval = model.NewIntervalVar(start, duration, start + duration, f'int{suffix}')

        # Store for later use
        start_vars[(j, t)] = start
        end_exprs[(j, t)] = start + duration  # linear expression
        intervals_per_machine[machine].append(interval)

# 3.2 Precedence constraints within each job
for j in all_jobs:
    for t in range(len(jobs_data[j]) - 1):
        model.Add(start_vars[(j, t + 1)] >= end_exprs[(j, t)])

# 3.3 Machine capacity – no overlap on each machine
for m in all_machines:
    model.AddNoOverlap(intervals_per_machine[m])

# 3.4 Makespan definition
makespan = model.NewIntVar(0, horizon, 'makespan')
for j in all_jobs:
    last_task_idx = len(jobs_data[j]) - 1
    model.Add(makespan >= end_exprs[(j, last_task_idx)])

# ----------------------
# 4. Objective
# ----------------------
model.Minimize(makespan)

# ----------------------
# 5. Solve
# ----------------------
solver = cp_model.CpSolver()
# Optional: use all cores
solver.parameters.num_search_workers = 8
status = solver.Solve(model)

# ----------------------
# 6. Output
# ----------------------
if status == cp_model.OPTIMAL:
    output = {"makespan": int(solver.Value(makespan))}
else:
    # If optimality is not proven, report null as makespan per requirements.
    output = {"makespan": None}

print(json.dumps(output))
