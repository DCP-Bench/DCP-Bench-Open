"""Project Euler 9: the Pythagorean triplet a^2 + b^2 = c^2 with a + b + c = 1000."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data. The sum 1000 is from the statement; each
# number lies in 1..500 as in the reference.
TOTAL = 1000
UPPER = 500


def build(instance):
    model = gp.Model("pythagorean_triplet")
    # The squares reach 250,000; a tight integrality tolerance keeps a near-0
    # binary from shifting them.
    model.Params.IntFeasTol = 1e-9

    values = range(1, UPPER + 1)

    # For each of a, b and c, is_[v] = 1 when it equals v. The number and its
    # square are then both linear in these binaries, so a^2 + b^2 = c^2 needs
    # no product of two variables.
    def number(name):
        is_ = model.addVars(values, vtype=GRB.BINARY, name=f"{name}_is")
        model.addConstr(is_.sum() == 1, name=f"{name}_one_value")
        var = model.addVar(lb=1, ub=UPPER, vtype=GRB.INTEGER, name=name)
        model.addConstr(var == gp.quicksum(v * is_[v] for v in values), name=f"{name}_read")
        return var, gp.quicksum(v * v * is_[v] for v in values)

    a, a_sq = number("a")
    b, b_sq = number("b")
    c, c_sq = number("c")

    # a + b + c = 1000.
    model.addConstr(a + b + c == TOTAL, name="sum")

    # a^2 + b^2 = c^2.
    model.addConstr(a_sq + b_sq == c_sq, name="pythagoras")

    return model, {"a": a, "b": b, "c": c}
