"""Eighteen-hole golf: give each of 18 holes a length of 3, 4 or 5 so that the course totals 72."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: 18 holes, lengths 3..5, total 72, as stated.
NUM_HOLES = 18
TOTAL_LENGTH = 72
SHORTEST, LONGEST = 3, 5


def build(instance):
    model = gp.Model("eighteen_hole_golf")

    # The length of each hole is 3, 4 or 5.
    holes = [model.addVar(lb=SHORTEST, ub=LONGEST, vtype=GRB.INTEGER, name=f"hole[{i}]")
             for i in range(NUM_HOLES)]

    # The total length of the course is 72.
    model.addConstr(gp.quicksum(holes) == TOTAL_LENGTH, name="total_length")

    return model, {"holes": holes}
