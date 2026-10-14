"""Aircraft landing: choose a landing time for each aircraft inside its window, keeping the separation times, to minimise the penalty for missing target times."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    earliest = instance["earliest_landing"]
    latest = instance["latest_landing"]
    target = instance["target_landing"]
    penalty_after = instance["penalty_after"]    # per unit of time landing after the target
    penalty_before = instance["penalty_before"]  # per unit of time landing before the target
    separation = instance["separation_time"]     # [i][j]: minimum gap between aircraft i and j
    planes = range(len(earliest))
    horizon = max(latest)  # the reference's upper bound for times, earliness and lateness

    model = gp.Model("aircraft_landing")

    landing = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="landing")
    earliness = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="earliness")
    lateness = model.addVars(planes, lb=0, ub=horizon, vtype=GRB.INTEGER, name="lateness")

    for i in planes:
        # Each aircraft lands inside its time window.
        model.addConstr(landing[i] >= earliest[i], name=f"earliest[{i}]")
        model.addConstr(landing[i] <= latest[i], name=f"latest[{i}]")
        # The distance to the target time is split into earliness and lateness.
        model.addConstr(landing[i] - target[i] == lateness[i] - earliness[i], name=f"target[{i}]")

    # The aircraft land in the order of their index (as the reference assumes), each at least
    # the separation time after the one before it.
    for i in planes:
        for j in range(i + 1, len(earliest)):
            model.addConstr(landing[j] - landing[i] >= separation[i][j], name=f"separation[{i},{j}]")

    # Minimise the penalty for landing before or after the target times.
    total_penalty = gp.quicksum(penalty_before[i] * earliness[i] + penalty_after[i] * lateness[i] for i in planes)
    model.setObjective(total_penalty, GRB.MINIMIZE)

    return model, {"landing_times": [landing[i] for i in planes], "total_penalty": total_penalty}
