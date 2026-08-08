import cpmpy as cp
import numpy as np
import json

# Job Shop Scheduling Problem
# Minimize makespan (total time to complete all jobs)

# Problem data
jobs_data = [  # (job_id, task_id) -> (machine_id, duration)
    [(0, 3), (1, 2), (2, 2)],  # Job 0
    [(0, 2), (2, 1), (1, 4)],  # Job 1
    [(1, 4), (2, 3)]           # Job 2
]

num_jobs = len(jobs_data)
num_machines = 3

# Calculate upper bound for start times
total_duration = sum(duration for job in jobs_data for machine_id, duration in job)
horizon = total_duration

# Create the model
model = cp.Model()

# Decision variables: start times for each task
start = {}
for job_id in range(num_jobs):
    start[job_id] = cp.intvar(0, horizon, shape=len(jobs_data[job_id]), name=f"start_job_{job_id}")

# Makespan variable (objective to minimize)
makespan = cp.intvar(0, horizon, name="makespan")

# Constraint 1: Precedence within jobs
# Each task in a job must start after the previous task completes
for job_id in range(num_jobs):
    job = jobs_data[job_id]
    for task_id in range(len(job) - 1):
        machine_id, duration = job[task_id]
        model += start[job_id][task_id + 1] >= start[job_id][task_id] + duration

# Constraint 2: Machine capacity (no overlap on same machine)
for machine_id in range(num_machines):
    # Find all tasks that use this machine
    tasks_on_machine = []
    for job_id in range(num_jobs):
        job = jobs_data[job_id]
        for task_id, (m_id, duration) in enumerate(job):
            if m_id == machine_id:
                tasks_on_machine.append((job_id, task_id, duration))
    
    # Add non-overlap constraints for all pairs of tasks on this machine
    for i in range(len(tasks_on_machine)):
        for j in range(i + 1, len(tasks_on_machine)):
            job1, task1, dur1 = tasks_on_machine[i]
            job2, task2, dur2 = tasks_on_machine[j]
            
            # Either task1 finishes before task2 starts, or task2 finishes before task1 starts
            model += (start[job1][task1] + dur1 <= start[job2][task2]) | \
                     (start[job2][task2] + dur2 <= start[job1][task1])

# Constraint 3: Makespan definition
# Makespan must be at least the completion time of all tasks
for job_id in range(num_jobs):
    job = jobs_data[job_id]
    last_task_id = len(job) - 1
    machine_id, duration = job[last_task_id]
    model += makespan >= start[job_id][last_task_id] + duration

# Objective: minimize makespan
model.minimize(makespan)

# Solve the model
if model.solve():
    solution = {"makespan": makespan.value()}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))