"""Permutation flow shop: sequence the jobs, which all visit machines 1..M in order, so that the makespan is minimal."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n_jobs = len(instance["jobs"])
    n_machines = len(instance["machines"])
    p = instance["process_time"]  # p[j][m]: processing time of job j on machine m
    jobs = range(n_jobs)
    slots = range(n_jobs)
    machines = range(n_machines)
    # Every time lies in 0..sum of all processing times, the horizon of the
    # problem's reference model.
    horizon = sum(sum(row) for row in p)

    model = gp.Model("flowshop_scheduling")

    # job_at[k, j] is 1 when job j is the k-th job of the sequence; every job
    # appears exactly once.
    job_at = model.addVars(slots, jobs, vtype=GRB.BINARY, name="job_at")
    for k in slots:
        model.addConstr(job_at.sum(k, "*") == 1, name=f"slot[{k}]")
    for j in jobs:
        model.addConstr(job_at.sum("*", j) == 1, name=f"job[{j}]")

    # Start and completion time of the k-th job of the sequence on each machine.
    start = model.addVars(slots, machines, lb=0, ub=horizon, vtype=GRB.INTEGER, name="start")
    end = model.addVars(slots, machines, lb=0, ub=horizon, vtype=GRB.INTEGER, name="end")
    for k in slots:
        for m in machines:
            # The k-th job occupies machine m for its processing time there.
            model.addConstr(
                end[k, m] == start[k, m] + gp.quicksum(p[j][m] * job_at[k, j] for j in jobs),
                name=f"duration[{k},{m}]",
            )
            # A job starts on machine m only after it has finished on machine m-1.
            if m > 0:
                model.addConstr(start[k, m] >= end[k, m - 1], name=f"route[{k},{m}]")
            # The k-th job starts on machine m only after the (k-1)-th has left it.
            if k > 0:
                model.addConstr(start[k, m] >= end[k - 1, m], name=f"machine_free[{k},{m}]")

    # The makespan is the latest completion time; minimise it.
    makespan = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name="makespan")
    model.addConstr(makespan == gp.max_([end[k, m] for k in slots for m in machines]), name="makespan_def")
    model.setObjective(makespan, GRB.MINIMIZE)

    return model, {"makespan": makespan}
