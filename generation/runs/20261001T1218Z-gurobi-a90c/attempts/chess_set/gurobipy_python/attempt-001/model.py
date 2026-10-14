"""Chess sets: how many small and large boxwood chess sets to make each week to maximise profit under lathe-hour and boxwood limits."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The problem has no instance data: hours, kilograms, limits and profits are the
    # problem's own, mirrored from the reference (as are the variable ranges).
    model = gp.Model("chess_set")

    small_set = model.addVar(lb=0, ub=100, vtype=GRB.INTEGER, name="small_set")
    large_set = model.addVar(lb=0, ub=100, vtype=GRB.INTEGER, name="large_set")
    max_profit = model.addVar(lb=0, ub=10000, vtype=GRB.INTEGER, name="max_profit")

    # Boxwood: 1 kg per small set and 3 kg per large set, 200 kg per week.
    model.addConstr(small_set + 3 * large_set <= 200, name="boxwood")

    # Lathe hours: 3 per small set and 2 per large set, 160 hours per week.
    model.addConstr(3 * small_set + 2 * large_set <= 160, name="lathe")

    # Profit: $5 per small set and $20 per large set; maximise it.
    model.addConstr(max_profit == 5 * small_set + 20 * large_set, name="profit")
    model.setObjective(max_profit, GRB.MAXIMIZE)

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}
