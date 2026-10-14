"""Cutting stock: choose how often to cut each pattern so every order is met with as few raw rolls as possible."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    pieces = instance["num_rolls_width"]  # pieces[p][w]: pieces of width w one cut of pattern p yields
    orders = instance["orders"]
    patterns = range(instance["num_patterns"])
    widths = range(len(instance["widths"]))

    model = gp.Model("cutting_stock")

    # patterns_used[p] is how many raw rolls are cut with pattern p. The bound of
    # 100 is the domain the problem's reference model declares.
    patterns_used = model.addVars(patterns, lb=0, ub=100, vtype=GRB.INTEGER, name="patterns_used")

    # For each width, the pieces cut meet the number ordered.
    for w in widths:
        model.addConstr(gp.quicksum(pieces[p][w] * patterns_used[p] for p in patterns) >= orders[w],
                        name=f"order[{w}]")

    # Minimise the number of raw rolls cut.
    min_rolls_cut = patterns_used.sum()
    model.setObjective(min_rolls_cut, GRB.MINIMIZE)

    return model, {"patterns_used": [patterns_used[p] for p in patterns],
                   "min_rolls_cut": min_rolls_cut}
