"""Fancy dress: the cheapest green outfit (or entrance fee) that lets Mr Greenguest into the party."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data; the prices are those in the statement.
PRICE = {"t": 10, "h": 2, "s": 12, "n": 11}   # tie, hat, socks, entrance fee; he owns the shirt


def build(instance):
    model = gp.Model("fancy_dress")

    # t: green tie, h: green hat, r: green shirt, s: green socks, n: pays the fee.
    t, h, r, s, n = (model.addVar(vtype=GRB.BINARY, name=name) for name in "thrsn")

    # Each rule is written as clauses; a clause "a or b or not c" becomes
    # a + b + (1 - c) >= 1. Paying the fee (n) excuses a guest from every rule.

    # 1. Someone wearing a green tie has to wear a green shirt.
    model.addConstr((1 - t) + r + n >= 1, name="rule1")

    # 2. He may wear green socks or a green shirt only with a green tie or a
    #    green hat.
    model.addConstr((1 - s) + t + h + n >= 1, name="rule2_socks")
    model.addConstr((1 - r) + t + h + n >= 1, name="rule2_shirt")

    # 3. Wearing a green shirt, or a green hat, or no green socks, requires a
    #    green tie.
    model.addConstr((1 - r) + t + n >= 1, name="rule3_shirt")
    model.addConstr((1 - h) + t + n >= 1, name="rule3_hat")
    model.addConstr(s + t + n >= 1, name="rule3_no_socks")

    # Minimise what he pays: tie $10, hat $2, socks $12, fee $11.
    cost = PRICE["t"] * t + PRICE["h"] * h + PRICE["s"] * s + PRICE["n"] * n
    model.setObjective(cost, GRB.MINIMIZE)

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}
