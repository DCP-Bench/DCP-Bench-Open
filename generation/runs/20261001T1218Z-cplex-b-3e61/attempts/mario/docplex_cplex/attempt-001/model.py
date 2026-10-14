"""Mario: plan a route from Mario's house to Luigi's house through other houses, collecting as much
gold as possible, without the fuel spent on the way exceeding the fuel limit.

The model reports the successor of every house: s[i] is the house visited after house i, s[i] = i
for a house not on the route, and Luigi's house is followed by Mario's house.
"""
from docplex.mp.model import Model


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]   # arc_fuel[i][j]: fuel to go from house i to house j
    gold = instance["goldInHouse"]    # gold collected by visiting a house
    houses = range(n)

    model = Model("mario")

    # go[i, j] = 1 when house j is the successor of house i; go[i, i] = 1 means house i is not
    # on the route. Successor binaries keep the output a linear expression over binaries.
    go = model.binary_var_matrix(houses, houses, name="go")

    # Every house has exactly one successor, and every house is the successor of exactly one
    # house (the successors are all different).
    for i in houses:
        model.add_constraint(model.sum(go[i, j] for j in houses) == 1)
        model.add_constraint(model.sum(go[j, i] for j in houses) == 1)

    # The route ends at Luigi's house, which loops back to Mario's house.
    model.add_constraint(go[luigi, mario] == 1)

    # order[i] is the rank of house i on the route; Mario's house is first. Along every arc of
    # the route other than the one back into Mario's house the rank goes up by one, so the
    # houses on the route form a single path from Mario to Luigi and no detached loop can exist.
    order = model.integer_var_list(n, 1, n, name="order")
    model.add_constraint(order[mario] == 1)
    for i in houses:
        for j in houses:
            if i != j and j != mario:
                model.add_indicator(go[i, j], order[j] == order[i] + 1)

    # The fuel consumed along the chosen arcs may not exceed the fuel limit.
    model.add_constraint(model.sum(arc_fuel[i][j] * go[i, j] for i in houses for j in houses) <= fuel_limit)

    # Maximize the gold of the houses on the route (those that are not their own successor).
    model.maximize(model.sum(gold[i] * (1 - go[i, i]) for i in houses))

    s = [model.sum(j * go[i, j] for j in houses) for i in houses]
    return model, {"s": s}
