from ortools.sat.python import cp_model
import json

# Input data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# Model definition
model = cp_model.CpModel()

num_jobs = len(jobs_data)
num_machines = 1 + max(task[0] for job in jobs_data for task in job)

# Compute horizon as sum of all durations (upper bound on makespan)
horizon = sum(task[1] for job in jobs_data for task in job)

# Decision variables: start times for each task
# Also create interval variables for no-overlap constraints on machines
all_tasks = {}
machine_to_intervals = [[] for _ in range(num_machines)]

for job_id, job in enumerate(jobs_data):
    for task_id, (machine, duration) in enumerate(job):
        suffix = f'j{job_id}t{task_id}'
        start_var = model.NewIntVar(0, horizon, 'start_' + suffix)
        end_var = model.NewIntVar(0, horizon, 'end_' + suffix)
        interval_var = model.NewIntervalVar(start_var, duration, end_var, 'interval_' + suffix)
        all_tasks[(job_id, task_id)] = (start_var, end_var, interval_var, machine, duration)
        machine_to_intervals[machine].append(interval_var)

# Add precedence constraints inside each job
for job_id, job in enumerate(jobs_data):
    for task_id in range(len(job) - 1):
        _, end_var, _, _, _ = all_tasks[(job_id, task_id)]
        start_next, _, _, _, _ = all_tasks[(job_id, task_id + 1)]
        model.Add(start_next >= end_var)

# Add no-overlap constraints for each machine
for machine in range(num_machines):
    model.AddNoOverlap(machine_to_intervals[machine])

# Makespan variable: max of all task end times
makespan = model.NewIntVar(0, horizon, 'makespan')
ends = [all_tasks[(job_id, len(jobs_data[job_id]) - 1)][1] for job_id in range(num_jobs)]
model.AddMaxEquality(makespan, ends)

# Objective: minimize makespan
model.Minimize(makespan)

# Solve the model
solver = cp_model.CpSolver()
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    solution = {
        'makespan': solver.Value(makespan)
    }
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")