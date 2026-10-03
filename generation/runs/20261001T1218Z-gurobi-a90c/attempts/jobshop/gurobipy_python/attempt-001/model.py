"""Job shop: schedule each job's tasks in order on their machines, one task per machine at a time, minimising the makespan."""
from itertools import combinations

import gurobipy as gp
from gurobipy import GRB


def build(instance):
    jobs_data = instance["jobs_data"]  # jobs_data[job][task] = [machine, duration]
    tasks = [(j, t) for j, job in enumerate(jobs_data) for t in range(len(job))]
    # Every time lies in 0..sum of all durations, the horizon of the problem's
    # reference model.
    horizon = sum(duration for job in jobs_data for _, duration in job)

    model = gp.Model("jobshop")

    start = {}
    end = {}
    for (j, t) in tasks:
        start[j, t] = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name=f"start[{j},{t}]")
        end[j, t] = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name=f"end[{j},{t}]")

    for (j, t) in tasks:
        # A task, once started, runs for its full duration.
        model.addConstr(end[j, t] == start[j, t] + jobs_data[j][t][1], name=f"duration[{j},{t}]")
        # No task of a job starts before the previous task of that job ends.
        if t > 0:
            model.addConstr(start[j, t] >= end[j, t - 1], name=f"precedence[{j},{t}]")

    # A machine works on one task at a time: of two tasks on the same machine,
    # one ends before the other starts. first[a, b] is 1 when a goes first;
    # indicator constraints state each branch without a big-M.
    machines = sorted({m for job in jobs_data for m, _ in job})
    for m in machines:
        on_m = [(j, t) for (j, t) in tasks if jobs_data[j][t][0] == m]
        for a, b in combinations(on_m, 2):
            first = model.addVar(vtype=GRB.BINARY, name=f"first[{a},{b}]")
            model.addConstr((first == 1) >> (start[b] >= end[a]), name=f"a_before_b[{a},{b}]")
            model.addConstr((first == 0) >> (start[a] >= end[b]), name=f"b_before_a[{a},{b}]")

    # The makespan is the latest end time; minimise it.
    makespan = model.addVar(lb=0, ub=horizon, vtype=GRB.INTEGER, name="makespan")
    model.addConstr(makespan == gp.max_([end[k] for k in tasks]), name="makespan_def")
    model.setObjective(makespan, GRB.MINIMIZE)

    return model, {"makespan": makespan}
