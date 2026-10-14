"""Permutation flow shop: every job goes through the machines in the same order, machine 1
to machine M, and the jobs are processed in the same sequence on every machine. A machine
handles one job at a time and a job is on one machine at a time. Find the sequence of jobs
that makes the makespan (the time at which the last job leaves the last machine) smallest.

The model reports the minimal makespan.
"""
import pulp


def build(instance):
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    process_time = instance["process_time"]  # process_time[job][machine]
    horizon = sum(sum(row) for row in process_time)  # upper bound on any time: all work in a row

    problem = pulp.LpProblem("flowshop", pulp.LpMinimize)

    # sequence: at[j][k] = 1 if job j is the k-th job of the sequence. Every job is in
    # exactly one place and every place holds exactly one job.
    at = [[pulp.LpVariable(f"at_{j}_{k}", cat="Binary") for k in range(n_jobs)] for j in range(n_jobs)]
    for j in range(n_jobs):
        problem += pulp.lpSum(at[j]) == 1
    for k in range(n_jobs):
        problem += pulp.lpSum(at[j][k] for j in range(n_jobs)) == 1

    # time the k-th job of the sequence needs on machine m
    duration = [[pulp.lpSum(process_time[j][m] * at[j][k] for j in range(n_jobs))
                 for m in range(n_machines)] for k in range(n_jobs)]

    # start[k][m] and end[k][m]: when the k-th job of the sequence starts and finishes on machine m
    start = [[pulp.LpVariable(f"start_{k}_{m}", 0, horizon) for m in range(n_machines)]
             for k in range(n_jobs)]
    end = [[pulp.LpVariable(f"end_{k}_{m}", 0, horizon) for m in range(n_machines)]
           for k in range(n_jobs)]
    for k in range(n_jobs):
        for m in range(n_machines):
            problem += end[k][m] == start[k][m] + duration[k][m]
            # a job cannot start on machine m before it has finished on machine m - 1
            if m > 0:
                problem += start[k][m] >= end[k][m - 1]
            # the k-th job cannot start on machine m before the (k-1)-th has finished on it
            if k > 0:
                problem += start[k][m] >= end[k - 1][m]

    # makespan: the time at which all jobs have been processed, to be minimised
    makespan = pulp.LpVariable("makespan", 0, horizon, cat="Integer")
    for k in range(n_jobs):
        for m in range(n_machines):
            problem += makespan >= end[k][m]
    problem += makespan

    return problem, {"makespan": makespan}
