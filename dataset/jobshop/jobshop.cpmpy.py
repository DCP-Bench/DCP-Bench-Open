#!/usr/bin/python3
# Category: cpmpy_examples
# Source: https://github.com/CPMpy/cpmpy/blob/master/examples/jobshop.py
# Source description: https://developers.google.com/optimization/scheduling/job_shop

"""
One common scheduling problem is the job shop, in which multiple jobs are processed on several machines.

Each job consists of a sequence of tasks, which must be performed in a given order, and each task must be processed
on a specific machine. For example, the job could be the manufacture of a single consumer item, such as an automobile.
The problem is to schedule the tasks on the machines so as to minimize the length of the schedule—the time it takes
for all the jobs to be completed.

There are several constraints for the job shop problem:
- No task for a job can be started until the previous task for that job is completed.
- A machine can only work on one task at a time.
- A task, once started, must run to completion.

Print the optimal makespan (makespan), which is the total time taken to complete all jobs.
"""

# Data
jobs_data = [  # (job_id, task_id) -> (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0: Task 0 on Machine 0 for 3 time units, etc.
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]
# End of data

# Import libraries
from cpmpy import *
import json
from itertools import combinations
import builtins  # To access the original built-in functions (because of the import * above)

# Extract job data
n_jobs = len(jobs_data)
n_tasks = builtins.sum(len(job) for job in jobs_data)
machines = set(task[0] for job in jobs_data for task in job)
n_machines = len(machines)

# Create variables for start and end times
max_duration = builtins.sum(task[1] for job in jobs_data for task in job)
max_tasks_per_job = builtins.max(len(job) for job in jobs_data)
start_times = intvar(0, max_duration, shape=(n_jobs, max_tasks_per_job), name="start_times")
end_times = intvar(0, max_duration, shape=(n_jobs, max_tasks_per_job), name="end_times")
makespan = intvar(0, max_duration, name="makespan")

# Create the model
model = Model()

# Add constraints for each task
for job_id, job in enumerate(jobs_data):
    for task_id, (machine, duration) in enumerate(job):
        model += (end_times[job_id, task_id] == start_times[job_id, task_id] + duration)

        # No task can start before the previous one ends
        if task_id > 0:
            model += (start_times[job_id, task_id] >= end_times[job_id, task_id - 1])

# Add machine constraints
for machine in machines:
    machine_tasks = [(job_id, task_id) for job_id, job in enumerate(jobs_data) for task_id, (m, duration) in enumerate(job) if m == machine]
    for (job1, task1), (job2, task2) in combinations(machine_tasks, 2):
        model += (start_times[job1, task1] >= end_times[job2, task2]) | (start_times[job2, task2] >= end_times[job1, task1])

# Objective: Minimize makespan
model += (makespan == max(end_times.flatten()))
model.minimize(makespan)

# Solve the model
model.solve()

# Print the solution
solution = {
    "makespan": makespan.value()
}
print(json.dumps(solution))
# End of CPMPy script
