import json
from ortools.sat.python import cp_model

# ------------------------------
# Input data (exactly as provided)
# ------------------------------
durations_data = [0, 3, 2, 5, 4, 2, 3, 4, 2, 4, 6, 0]
resource_needs_data = [
    [0, 0],  # job 0
    [5, 1],  # job 1
    [0, 4],  # job 2
    [1, 4],  # job 3
    [1, 3],  # job 4
    [3, 2],  # job 5
    [3, 1],  # job 6
    [2, 4],  # job 7
    [4, 0],  # job 8
    [5, 2],  # job 9
    [2, 5],  # job 10
    [0, 0],  # job 11
]
resource_capacities_data = [6, 8]

# (p, s) means: job p must finish before job s can start
successors_link_data = [
    [0, 1], [0, 2], [0, 3],
    [1, 4], [1, 5],
    [2, 9], [2, 10],
    [3, 8],
    [4, 6], [4, 7],
    [5, 9], [5, 10],
    [6, 8], [6, 9],
    [7, 8],
    [8, 11], [9, 11], [10, 11]
]

# ------------------------------
# Model construction
# ------------------------------
num_jobs = len(durations_data)
num_resources = len(resource_capacities_data)
HORIZON = sum(durations_data)  # simple upper bound of makespan

model = cp_model.CpModel()

# Decision variables: start time and end time for each job
start_vars = []
end_vars = []
interval_vars = []

for j in range(num_jobs):
    start = model.NewIntVar(0, HORIZON, f'start_{j}')
    end = model.NewIntVar(0, HORIZON, f'end_{j}')
    dur = durations_data[j]
    interval = model.NewIntervalVar(start, dur, end, f'interval_{j}')

    start_vars.append(start)
    end_vars.append(end)
    interval_vars.append(interval)

# Dummy source job starts at 0
model.Add(start_vars[0] == 0)

# Precedence constraints
for p, s in successors_link_data:
    model.Add(start_vars[s] >= end_vars[p])

# Renewable resource constraints (cumulative)
for r in range(num_resources):
    intervals_r = []
    demands_r = []
    for j in range(num_jobs):
        demand = resource_needs_data[j][r]
        duration = durations_data[j]
        if demand > 0 and duration > 0:
            intervals_r.append(interval_vars[j])
            demands_r.append(demand)
    if intervals_r:  # avoid adding empty cumulative
        model.AddCumulative(intervals_r, demands_r, resource_capacities_data[r])

# Objective: minimise project makespan (start time of dummy sink job 11)
model.Minimize(start_vars[11])

# ------------------------------
# Solve
# ------------------------------
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    raise RuntimeError('No feasible schedule found.')

# ------------------------------
# Output
# ------------------------------
start_times = [int(solver.Value(start_vars[j])) for j in range(num_jobs)]
print(json.dumps({"start_time": start_times}))