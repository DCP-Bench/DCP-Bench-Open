"""Giant cat army riddle: from 0, build a list by adding 5, adding 7 or taking a square root, so that 2, 10 and 14 appear in that order."""
import math

import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: values at most 60, a list of 24 numbers,
# starting at 0 and ending at 14, as stated.
MAXVAL = 60
N = 24
START, END = 0, 14
FIRST, SECOND = 2, 10       # must appear, FIRST before SECOND
STEPS = (5, 7)


def build(instance):
    model = gp.Model("giant_cat_army")

    # x[i] is the i-th number of the list; all are integers in 0..60.
    x = [model.addVar(lb=0, ub=MAXVAL, vtype=GRB.INTEGER, name=f"x[{i}]") for i in range(N)]

    # The list starts with 0 and ends with 14.
    model.addConstr(x[0] == START, name="start")
    model.addConstr(x[N - 1] == END, name="end")

    # The second number is 5 or 7.
    second_is_5 = model.addVar(vtype=GRB.BINARY, name="second_is_5")
    model.addConstr(x[1] == 7 - 2 * second_is_5, name="second_number")

    # Each next number is the previous plus 5, plus 7, or its square root.
    # For the root, root[i, r] = 1 when x[i] = r^2 and x[i+1] = r; r^2 <= 60.
    roots = range(math.isqrt(MAXVAL) + 1)
    for i in range(N - 1):
        add = {s: model.addVar(vtype=GRB.BINARY, name=f"add{s}[{i}]") for s in STEPS}
        sqrt = model.addVar(vtype=GRB.BINARY, name=f"sqrt[{i}]")
        model.addConstr(gp.quicksum(add.values()) + sqrt == 1, name=f"one_operation[{i}]")
        for s, b in add.items():
            model.addConstr((b == 1) >> (x[i + 1] == x[i] + s), name=f"add{s}_step[{i}]")
        root = model.addVars(roots, vtype=GRB.BINARY, name=f"root[{i}]")
        model.addConstr(root.sum() == sqrt, name=f"root_chosen[{i}]")
        model.addConstr((sqrt == 1) >> (x[i] == gp.quicksum(r * r * root[r] for r in roots)), name=f"square[{i}]")
        model.addConstr((sqrt == 1) >> (x[i + 1] == gp.quicksum(r * root[r] for r in roots)), name=f"root_step[{i}]")

    # All the numbers are distinct: for each pair, one lies below the other.
    for i in range(N):
        for j in range(i + 1, N):
            below = model.addVar(vtype=GRB.BINARY, name=f"below[{i},{j}]")
            model.addConstr((below == 1) >> (x[i] <= x[j] - 1))
            model.addConstr((below == 0) >> (x[i] >= x[j] + 1))

    # 2 and 10 appear in the list (at positions 1..N-1, as in the reference's
    # index domain), 2 before 10.
    def appears(value, name):
        where = model.addVars(range(1, N), vtype=GRB.BINARY, name=name)
        model.addConstr(where.sum() == 1, name=f"{name}_once")
        for i in range(1, N):
            model.addConstr((where[i] == 1) >> (x[i] == value), name=f"{name}[{i}]")
        return gp.quicksum(i * where[i] for i in range(1, N))

    model.addConstr(appears(FIRST, "pos2") <= appears(SECOND, "pos10") - 1, name="order")

    return model, {"x": x}
