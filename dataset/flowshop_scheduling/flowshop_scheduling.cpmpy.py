#!/usr/bin/python3
# Category: complex_or
# Source: https://github.com/xzymustbexzy/Chain-of-Experts/blob/main/dataset/ComplexOR/flowshop_scheduling

"""
A set of jobs `Jobs` need to be processed on a set of machines `Machines` in series. All jobs have the same processing
order through all the machines from machine 1 to machine M. Each machine can work in parallel. The workflow is the
following: the first job of the sequence goes to the first machine to be processed; meanwhile, other jobs wait; when
the first machine has processed the first job, the first job goes to the second machine and the second job of the
sequence starts to be processed by the first machine; and so on. The time required to process job `j` on machine `m`
is `ProcesTime_{j, m}`. The problem aims to minimize the total makespan. The goal is to find a sequence of jobs that
minimize the makespan: the time when all jobs have been processed.

Print the optimal makespan (makespan) as an integer.
"""

# Data
jobs = [1, 2, 3]  # List of jobs
schedules = [1, 2, 3]  # List of schedules (same as jobs)
machines = [1, 2]  # List of machines
process_time = [  # process_time[job_index][machine_index] is the processing time of job j on machine m
    [9, 12],
    [2, 2],
    [3, 1]
]
# Note: job_index = job - 1, machine_index = machine - 1
# End of data

# Import libraries
from cpmpy import *
import json


# Decision variables

# # Start times of jobs on machines
# S = model.addVars(J, M, vtype=GRB.CONTINUOUS, name='S')
#
# # Completion times of jobs on machines
# C = model.addVars(J, M, vtype=GRB.CONTINUOUS, name='C')
#
# # Sequencing variables between jobs
# y = model.addVars(J, J, vtype=GRB.BINARY, name='y')
#
# # Objective: minimize makespan
# makespan = model.addVar(vtype=GRB.CONTINUOUS, name='makespan')
# model.setObjective(makespan, GRB.MINIMIZE)

n_jobs = len(jobs)
n_machines = len(machines)
max_duration = sum(sum(row) for row in process_time)

# Start times of jobs on machines
start_times = intvar(0, max_duration, shape=(n_jobs, n_machines), name="start_times")
# Completion times of jobs on machines
end_times = intvar(0, max_duration, shape=(n_jobs, n_machines), name="end_times")
# Makespan
makespan = intvar(0, max_duration, name="makespan")

# Model
model = Model()

# Add constraints for each job and machine
for j in range(n_jobs):
    for m in range(n_machines):
        model += (end_times[j, m] == start_times[j, m] + process_time[j][m])
        # Job cannot start on machine m before it has completed on machine m-1
        if m > 0:
            model += (start_times[j, m] >= end_times[j, m - 1])
        # Job j cannot start on machine m before job j-1 has completed on machine m
        if j > 0:
            model += (start_times[j, m] >= end_times[j - 1, m])
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