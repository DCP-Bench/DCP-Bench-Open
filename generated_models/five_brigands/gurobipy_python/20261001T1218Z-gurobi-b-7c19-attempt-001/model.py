"""Five brigands (Dudeney 133): how many of the 200 doubloons each of five brigands had."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: 200 doubloons and the multipliers
# 12, 3, 1, 1/2 and 1/3 come from the statement.
TOTAL = 200


def build(instance):
    model = gp.Model("five_brigands")

    # Doubloons of Alfonso, Benito, Carlos, Diego and Esteban; no brigand had
    # less than one, and none can have more than the total.
    A, B, C, D, E = (model.addVar(lb=1, ub=TOTAL, vtype=GRB.INTEGER, name=name) for name in "ABCDE")

    # Altogether they captured exactly 200 doubloons.
    model.addConstr(A + B + C + D + E == TOTAL, name="total")

    # With Alfonso having twelve times as much, Benito three times, Carlos the
    # same, Diego half and Esteban a third, they would still have 200; the
    # equation is multiplied by 6 to clear the fractions.
    model.addConstr(6 * (12 * A + 3 * B + C) + 3 * D + 2 * E == 6 * TOTAL, name="scaled_total")

    return model, {"A": A, "B": B, "C": C, "D": D, "E": E}
