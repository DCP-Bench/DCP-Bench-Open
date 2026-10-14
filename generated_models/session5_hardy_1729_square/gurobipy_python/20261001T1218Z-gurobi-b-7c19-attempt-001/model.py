"""Hardy 1729 (squares): four different numbers in 1..100 with a^2 + b^2 = c^2 + d^2."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: the range 1..100 is from the statement.
RANGE_MIN, RANGE_MAX = 1, 100
NAMES = "abcd"


def build(instance):
    model = gp.Model("session5_hardy_1729_square")
    # Squares reach 10,000; a tight integrality tolerance keeps a near-0
    # binary from shifting them.
    model.Params.IntFeasTol = 1e-9

    values = range(RANGE_MIN, RANGE_MAX + 1)

    # is_[x, v] = 1 when number x equals v. Each number and its square are
    # linear in these binaries, so no product of two variables is needed.
    is_ = model.addVars(NAMES, values, vtype=GRB.BINARY, name="is")
    number, square = {}, {}
    for x in NAMES:
        model.addConstr(is_.sum(x, "*") == 1, name=f"one_value[{x}]")
        number[x] = model.addVar(lb=RANGE_MIN, ub=RANGE_MAX, vtype=GRB.INTEGER, name=x)
        model.addConstr(number[x] == gp.quicksum(v * is_[x, v] for v in values), name=f"read[{x}]")
        square[x] = gp.quicksum(v * v * is_[x, v] for v in values)

    # The four numbers are all different.
    for v in values:
        model.addConstr(is_.sum("*", v) <= 1, name=f"different[{v}]")

    # a^2 + b^2 = c^2 + d^2.
    model.addConstr(square["a"] + square["b"] == square["c"] + square["d"], name="sum_of_squares")

    return model, {x: number[x] for x in NAMES}
