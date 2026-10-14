"""Farmer and cows: share cows 1..n among the sons, a given number each, so every son gets the same amount of milk."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    num_cows, num_sons = instance["num_cows"], instance["num_sons"]
    cows_per_son = instance["cows_per_son"]
    cows = range(num_cows)
    sons = range(num_sons)
    # Cow i (0-based) gives i + 1 units of milk; each son's share is the total
    # divided by the number of sons, rounded down as in the reference.
    milk = [i + 1 for i in cows]
    milk_per_son = sum(milk) // num_sons

    model = gp.Model("farmer_and_cows")

    # owns[i, s] is 1 when cow i goes to son s.
    owns = model.addVars(cows, sons, vtype=GRB.BINARY, name="owns")

    # Every cow goes to exactly one son.
    for i in cows:
        model.addConstr(owns.sum(i, "*") == 1, name=f"cow[{i}]")

    for s in sons:
        # Each son gets the number of cows the distribution gives him.
        model.addConstr(owns.sum("*", s) == cows_per_son[s], name=f"count[{s}]")
        # Each son's cows give the same total quantity of milk.
        model.addConstr(gp.quicksum(milk[i] * owns[i, s] for i in cows) == milk_per_son, name=f"milk[{s}]")

    # The son each cow goes to, read back from the assignment.
    return model, {"cow_assignments": [gp.quicksum(s * owns[i, s] for s in sons) for i in cows]}
