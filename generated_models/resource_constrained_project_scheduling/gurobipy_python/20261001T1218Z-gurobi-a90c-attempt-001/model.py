"""Resource-constrained project scheduling: start every job after its predecessors, within the resource capacities, minimising the latest start time."""
import gurobipy as gp
from gurobipy import GRB


def serial_schedule(durations, needs, capacities, preds, order):
    """Start times of a feasible schedule: each job, in the given order, at the earliest
    time its predecessors have finished and every resource has room for its whole run."""
    used = {}
    start = {}
    for i in order:
        t = max((start[p] + durations[p] for p in preds[i]), default=0)
        while any(used.get((r, s), 0) + needs[i][r] > capacities[r]
                  for s in range(t, t + durations[i]) for r in range(len(capacities))):
            t += 1
        start[i] = t
        for s in range(t, t + durations[i]):
            for r in range(len(capacities)):
                used[r, s] = used.get((r, s), 0) + needs[i][r]
    return start


def build(instance):
    durations = instance["durations_data"]
    needs = instance["resource_needs_data"]
    capacities = instance["resource_capacities_data"]
    links = instance["successors_link_data"]
    jobs = range(len(durations))
    resources = range(len(capacities))

    preds = {i: [a for a, b in links if b == i] for i in jobs}
    succs = {i: [b for a, b in links if a == i] for i in jobs}

    # head[i]: earliest start of job i from the precedences alone (longest chain before it).
    head = {}
    def earliest(i):
        if i not in head:
            head[i] = max((earliest(p) + durations[p] for p in preds[i]), default=0)
        return head[i]
    # tail[i]: how much later than job i some job must start (longest chain after it).
    tail = {}
    def latest_gap(i):
        if i not in tail:
            tail[i] = max((durations[i] + latest_gap(j) for j in succs[i]), default=0)
        return tail[i]
    for i in jobs:
        earliest(i)
        latest_gap(i)

    # An upper bound on the optimal objective: the latest start of a feasible schedule
    # built greedily from the instance (jobs with the longest remaining chain first).
    # No optimal schedule starts a job later than bound - tail[i], so the time grid of
    # each job can stop there without losing an optimal schedule.
    topo = sorted(jobs, key=lambda i: (head[i], -tail[i], i))
    by_tail = sorted(jobs, key=lambda i: (-tail[i], head[i], i))
    ready_order = []
    placed = set()
    while len(ready_order) < len(durations):
        for i in by_tail:
            if i not in placed and all(p in placed for p in preds[i]):
                ready_order.append(i)
                placed.add(i)
                break
    bound = min(max(serial_schedule(durations, needs, capacities, preds, order).values())
                for order in (topo, ready_order))

    model = gp.Model("rcpsp")

    # at[i, t] is 1 when job i starts at time t, for t between its earliest and latest start.
    window = {i: range(head[i], bound - tail[i] + 1) for i in jobs}
    at = {(i, t): model.addVar(vtype=GRB.BINARY, name=f"at[{i},{t}]") for i in jobs for t in window[i]}
    start = {i: gp.quicksum(t * at[i, t] for t in window[i]) for i in jobs}

    # Every job starts exactly once.
    for i in jobs:
        model.addConstr(gp.quicksum(at[i, t] for t in window[i]) == 1, name=f"once[{i}]")

    # Precedence: a job starts only after each predecessor has finished.
    for a, b in links:
        model.addConstr(start[b] >= start[a] + durations[a], name=f"prec[{a},{b}]")

    # Cumulative resources: at every time, the jobs running then (started in the last
    # duration time units) need no more of each resource than its capacity.
    horizon = range(bound + max(durations) + 1)
    for r in resources:
        for s in horizon:
            running = [needs[i][r] * at[i, t] for i in jobs if needs[i][r] > 0
                       for t in window[i] if t <= s < t + durations[i]]
            if running:
                model.addConstr(gp.quicksum(running) <= capacities[r], name=f"cap[{r},{s}]")

    # The objective is the latest start time over all jobs, as in the reference.
    makespan = model.addVar(lb=0, ub=bound, vtype=GRB.INTEGER, name="makespan")
    for i in jobs:
        model.addConstr(makespan >= start[i], name=f"last[{i}]")
    model.setObjective(makespan, GRB.MINIMIZE)

    return model, {"start_time": [start[i] for i in jobs]}
