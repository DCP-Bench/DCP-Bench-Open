from pycsp3 import *

# Permutation flowshop: every job goes through the machines 1 to M in the same order.
# A machine works on one job at a time, and a job starts on a machine only when it has
# finished on the previous machine. All jobs use the same sequence on every machine.

process_time = data.process_time
n_jobs = len(process_time)
n_machines = len(process_time[0])
horizon = sum(sum(row) for row in process_time)

# seq[k] is the job at position k of the sequence
seq = VarArray(size=n_jobs, dom=range(n_jobs))
# pt[k][m] is the processing time of the job at position k on machine m
pt = VarArray(size=[n_jobs, n_machines], dom=sorted({t for row in process_time for t in row}))
# start[k][m] is the time at which the job at position k starts on machine m
start = VarArray(size=[n_jobs, n_machines], dom=range(0, horizon + 1))
# makespan is the time when all jobs have been processed
makespan = Var(dom=range(0, horizon + 1))

satisfy(
    # each job appears once in the sequence
    AllDifferent(seq),

    # the processing time at each position is the time of the job there
    [Table(scope=[seq[k], pt[k][m]], supports=[(j, process_time[j][m]) for j in range(n_jobs)])
     for k in range(n_jobs) for m in range(n_machines)],

    # the first job starts at time 0 on the first machine
    start[0][0] == 0,

    # a machine works on one job at a time: a job starts after the previous job leaves the machine
    [start[k][m] >= start[k - 1][m] + pt[k - 1][m] for k in range(1, n_jobs) for m in range(n_machines)],

    # a job goes to the next machine only after it is processed on the current one
    [start[k][m] >= start[k][m - 1] + pt[k][m - 1] for k in range(n_jobs) for m in range(1, n_machines)],

    # the makespan is the finishing time of the last job on the last machine
    makespan == start[n_jobs - 1][n_machines - 1] + pt[n_jobs - 1][n_machines - 1],
)

# minimise the makespan
minimize(makespan)
