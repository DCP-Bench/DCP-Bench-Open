
import cpmpy as cp
import json

# Data
jobs_data = [  # (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

num_jobs = len(jobs_data)
num_machines = max(task[0] for job in jobs_data for task in job) + 1

# Flatten tasks and keep track of job and task indices
tasks = []
for j, job in enumerate(jobs_data):
    for t, (m, d) in enumerate(job):
        tasks.append((j, t, m, d))

num_tasks = len(tasks)

# Decision variables: start times for each task
horizon = sum(task[3] for task in tasks)  # upper bound on makespan
start_times = cp.intvar(0, horizon, shape=num_tasks, name="start_times")

# Makespan variable
makespan = cp.intvar(0, horizon, name="makespan")

model = cp.Model()

# Constraints

# 1) Precedence constraints: tasks in the same job must be done in order
for j in range(num_jobs):
    job_tasks = [i for i, (job_id, _, _, _) in enumerate(tasks) if job_id == j]
    for i in range(len(job_tasks) - 1):
        model += start_times[job_tasks[i]] + tasks[job_tasks[i]][3] <= start_times[job_tasks[i+1]]

# 2) No overlap on machines: tasks on the same machine cannot overlap
for m in range(num_machines):
    machine_tasks = [i for i, (_, _, machine_id, _) in enumerate(tasks) if machine_id == m]
    # For each pair of tasks on the same machine, one must finish before the other starts
    for i in range(len(machine_tasks)):
        for j in range(i+1, len(machine_tasks)):
            t1 = machine_tasks[i]
            t2 = machine_tasks[j]
            d1 = tasks[t1][3]
            d2 = tasks[t2][3]
            # Either t1 before t2 or t2 before t1
            model += (start_times[t1] + d1 <= start_times[t2]) | (start_times[t2] + d2 <= start_times[t1])

# 3) Makespan is at least the finish time of every task
for i, (_, _, _, d) in enumerate(tasks):
    model += start_times[i] + d <= makespan

# Objective: minimize makespan
model.minimize(makespan)

# Solve and print
if model.solve():
    solution = {'makespan': int(makespan.value())}
    print(json.dumps(solution, indent=4))
else:
    print("No solution found.")
