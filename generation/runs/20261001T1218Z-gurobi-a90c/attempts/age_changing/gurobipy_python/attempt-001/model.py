"""Age changing: applying +2, /8, -3 and *7 in some order to my age gives my husband's age, and in another order to his age gives mine."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the four operations, the age range 16..120 and
    # the range 1..1000 of intermediate values are the puzzle's own, mirrored from the reference.
    n_ops = 4                  # 0: +2, 1: /8, 2: -3, 3: *7
    age_low, age_high = 16, 120
    steps = range(n_ops)
    ops = range(n_ops)

    model = gp.Model("age_changing")

    m = model.addVar(lb=age_low, ub=age_high, vtype=GRB.INTEGER, name="m")   # my age
    h = model.addVar(lb=age_low, ub=age_high, vtype=GRB.INTEGER, name="h")   # husband's age

    # Values after each operation: hlist starts at my age and ends at his,
    # mlist starts at his age and ends at mine.
    hlist = model.addVars(n_ops + 1, lb=1, ub=1000, vtype=GRB.INTEGER, name="hlist")
    mlist = model.addVars(n_ops + 1, lb=1, ub=1000, vtype=GRB.INTEGER, name="mlist")
    model.addConstr(hlist[0] == m)
    model.addConstr(hlist[n_ops] == h)
    model.addConstr(mlist[0] == h)
    model.addConstr(mlist[n_ops] == m)

    # order1[i, o] (order2[i, o]) is 1 when operation o is applied at step i of the
    # first (second) sequence; each order uses every operation exactly once.
    order1 = model.addVars(steps, ops, vtype=GRB.BINARY, name="order1")
    order2 = model.addVars(steps, ops, vtype=GRB.BINARY, name="order2")
    for order in (order1, order2):
        for i in steps:
            model.addConstr(order.sum(i, "*") == 1)
        for o in ops:
            model.addConstr(order.sum("*", o) == 1)

    # The same operations in a different order: the two orders agree on at most
    # n_ops - 1 steps. same[i, o] is at least 1 when both orders apply o at step i.
    same = model.addVars(steps, ops, vtype=GRB.BINARY, name="same")
    for i in steps:
        for o in ops:
            model.addConstr(same[i, o] >= order1[i, o] + order2[i, o] - 1)
    model.addConstr(same.sum() <= n_ops - 1, name="different_order")

    # Each step applies its operation to the previous value. Division by 8 is
    # written 8 * new == old, as in the reference, so it must divide exactly.
    for order, values in ((order1, hlist), (order2, mlist)):
        for i in steps:
            old, new = values[i], values[i + 1]
            model.addConstr((order[i, 0] == 1) >> (new == old + 2))
            model.addConstr((order[i, 1] == 1) >> (8 * new == old))
            model.addConstr((order[i, 2] == 1) >> (new == old - 3))
            model.addConstr((order[i, 3] == 1) >> (new == 7 * old))

    return model, {"m": m, "h": h}
