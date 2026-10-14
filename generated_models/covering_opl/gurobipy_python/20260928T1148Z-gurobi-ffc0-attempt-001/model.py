"""Covering: hire the cheapest set of workers such that every task has a qualified worker."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    cost = instance["Cost"]
    qualified = instance["Qualified"]  # qualified[t]: the workers, 1-based, who can do task t
    workers = range(instance["nb_workers"])
    tasks = range(instance["num_tasks"])

    model = gp.Model("covering_opl")

    # hire[w] is 1 when worker w is hired.
    hire = model.addVars(workers, vtype=GRB.BINARY, name="workers")

    # Every task has at least one hired worker qualified for it (the list is 1-based).
    for t in tasks:
        model.addConstr(gp.quicksum(hire[w - 1] for w in qualified[t]) >= 1, name=f"task[{t}]")

    # Minimise the total hiring cost.
    total_cost = gp.quicksum(cost[w] * hire[w] for w in workers)
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost, "workers": [hire[w] for w in workers]}
