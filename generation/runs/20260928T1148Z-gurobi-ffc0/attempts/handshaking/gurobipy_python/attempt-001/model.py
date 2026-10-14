"""Handshaking: at Hilary and Jocelyn's party everyone but Hilary shook a different number of hands; how many did Hilary shake?"""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    n = 2 + 2 * instance["num_couples"]  # the guests' couples plus Hilary (0) and Jocelyn (1)
    people = range(n)
    # Spouses sit next to each other: 0 and 1, 2 and 3, and so on.
    spouse = [p + 1 if p % 2 == 0 else p - 1 for p in people]

    model = gp.Model("handshaking")

    # shake[i, j], for i < j, is 1 when i and j shook hands; nobody shakes hands
    # with themselves or their spouse, so those pairs have no variable at all.
    pairs = [(i, j) for i in people for j in range(i + 1, n) if j != spouse[i]]
    shake = model.addVars(pairs, vtype=GRB.BINARY, name="shake")

    def hands(p):
        return gp.quicksum(shake[i, j] for (i, j) in pairs if p in (i, j))

    # Everyone except Hilary shook a different number of hands. Those are n - 1
    # people with counts in 0..n-2, so every count occurs exactly once.
    others = range(1, n)
    counts = range(n - 1)
    has = model.addVars(others, counts, vtype=GRB.BINARY, name="has")
    for p in others:
        model.addConstr(has.sum(p, "*") == 1, name=f"one_count[{p}]")
        model.addConstr(hands(p) == gp.quicksum(c * has[p, c] for c in counts), name=f"count[{p}]")
    for c in counts:
        model.addConstr(has.sum("*", c) == 1, name=f"distinct[{c}]")

    # hil is the number of hands Hilary shook. It is a variable of its own so that
    # the declared output is this one number, not every handshake behind it.
    hil = model.addVar(lb=0, ub=n - 2, vtype=GRB.INTEGER, name="hil")
    model.addConstr(hil == hands(0), name="hilary")

    return model, {"hil": hil}
