# Import libraries
from cpmpy import *
import json

# Parameters
jobs_data = [
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# Extract all tasks and machines
all_tasks = []
machine_ids = set()
for job in jobs_data:
    for task in job:
        machine_ids.add(task[0])
        all_tasks.append(task)
n_machines = len(machine_ids)
n_jobs = len(jobs_data)

# Decision Variables
max_time = sum(task[1] for job in jobs_data for task in job)  # Upper bound for makespan
start_times = intvar(0, max_time, shape=len(all_tasks), name="start_times")
makespan = intvar(0, max_time, name="makespan")

# Model
model = Model()

# Constraint: makespan is the maximum end time of all tasks
end_times = [start_times[i] + all_tasks[i][1] for i in range(len(all_tasks))]
model += makespan == max(end_times)

# Constraint: tasks within a job must be in sequence
task_idx = 0
for job in jobs_data:
    for i in range(len(job)-1):
        model += start_times[task_idx + i + 1] >= start_times[task_idx + i] + job[i][1]
    task_idx += len(job)

# Constraint: no overlapping tasks on the same machine
for machine in machine_ids:
    machine_tasks = [i for i, task in enumerate(all_tasks) if task[0] == machine]
    for i in range(len(machine_tasks)):
        for j in range(i+1, len(machine_tasks)):
            ti = machine_tasks[i]
            tj = machine_tasks[j]
            # Either task i finishes before task j starts or vice versa
            model += (start_times[ti] + all_tasks[ti][1] <= start_times[tj]) | \
                     (start_times[tj] + all_tasks[tj][1] <= start_times[ti])

# Objective: minimize makespan
model.minimize(makespan)

# Solve
model.solve()

# Print solution
solution = {
    "makespan": makespan.value()
}
print(json.dumps(solution))
# End of CPMPy script