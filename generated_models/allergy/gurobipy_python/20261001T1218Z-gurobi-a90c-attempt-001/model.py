"""Allergy: match four friends (Debra, Janet, Hugh, Rick) to their surname and to their one allergy."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the friends, foods, surnames and clues are the
    # puzzle's own, mirrored from the reference.
    n = 4
    friends = range(n)
    debra, janet, hugh, rick = friends
    foods = ["eggs", "mold", "nuts", "ragweed"]
    surnames = ["baxter", "lemon", "malone", "fleet"]

    model = gp.Model("allergy")

    # has_food[f, p] is 1 when friend p is allergic to food f; has_name[s, p] likewise
    # for surname s. Each food and each surname belongs to exactly one friend, and
    # each friend has exactly one of each (all different).
    has_food = model.addVars(n, n, vtype=GRB.BINARY, name="has_food")
    has_name = model.addVars(n, n, vtype=GRB.BINARY, name="has_name")
    for x in (has_food, has_name):
        for k in range(n):
            model.addConstr(x.sum(k, "*") == 1)
            model.addConstr(x.sum("*", k) == 1)

    food = {f: gp.quicksum(p * has_food[i, p] for p in friends) for i, f in enumerate(foods)}
    name = {s: gp.quicksum(p * has_name[i, p] for p in friends) for i, s in enumerate(surnames)}
    eggs, mold, ragweed = 0, 1, 3
    baxter, lemon, fleet = 0, 1, 3

    # Rick is not allergic to mold.
    model.addConstr(has_food[mold, rick] == 0)
    # Baxter is allergic to eggs.
    for p in friends:
        model.addConstr(has_name[baxter, p] == has_food[eggs, p])
    # Hugh is neither surnamed Lemon nor Fleet.
    model.addConstr(has_name[lemon, hugh] == 0)
    model.addConstr(has_name[fleet, hugh] == 0)
    # Debra is allergic to ragweed.
    model.addConstr(has_food[ragweed, debra] == 1)
    # Janet (who isn't Lemon) is neither allergic to eggs nor to mold.
    model.addConstr(has_name[lemon, janet] == 0)
    model.addConstr(has_food[eggs, janet] == 0)
    model.addConstr(has_food[mold, janet] == 0)

    # Each food and surname is reported as the friend it belongs to (Debra 0 .. Rick 3).
    return model, {**food, **name}
