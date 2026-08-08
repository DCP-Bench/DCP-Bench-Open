from cpmpy import *
import json

# Input data
jobs_data = [
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

# Number of jobs and machines
num_jobs = len(jobs_data)
num_machines = 3  # Since machine IDs are 0, 1, 2

# Maximum possible makespan (sum of all durations)
max_duration = sum([duration for job in jobs_data for _, duration in job])

# Decision variables
# start_time[j][t]: start time of task t in job j
start_time = intvar(0, max_duration, shape=(num_jobs, max(len(job) for job in jobs_data)), name="start_time")

# Makespan: the maximum end time of all tasks
makespan = intvar(0, max_duration, name="makespan")

# Model
model = Model()

# Constraint: For each job, tasks must be processed in order
for j in range(num_jobs):
    for t in range(1, len(jobs_data[j])):
        model += [start_time[j, t] >= start_time[j, t - 1] + jobs_data[j][t - 1][1]]

# Constraint: For each machine, no two tasks can overlap
for m in range(num_machines):
    for j1 in range(num_jobs):
        for t1 in range(len(jobs_data[j1])):
            if jobs_data[j1][t1][0] == m:
                for j2 in range(j1 + 1, num_jobs):
                    for t2 in range(len(jobs_data[j2])):
                        if jobs_data[j2][t2][0] == m:
                            # Ensure tasks on the same machine do not overlap
                            model += (start_time[j1, t1] + jobs_data[j1][t1][1] <= start_time[j2, t2]) | \
                                     (start_time[j2, t2] + jobs_data[j2][t2][1] <= start_time[j1, t1])

# Constraint: Makespan is the maximum end time of all tasks
model += [makespan >= start_time[j, t] + jobs_data[j][t][1] for j in range(num_jobs) for t in range(len(jobs_data[j]))]

# Objective: Minimize the makespan
model.minimize(makespan)

# Solve the model
model.solve()

# Print the solution
solution = {"makespan": makespan.value()}
print(json.dumps(solution))