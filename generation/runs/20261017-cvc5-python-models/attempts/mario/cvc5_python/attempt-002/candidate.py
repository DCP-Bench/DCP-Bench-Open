# Mario: collect as much gold as possible on a route from Mario's house to Luigi's house,
# within the fuel limit. Output s[i] is the house succeeding house i (s[i] = i if house i is
# not on the route); Luigi's successor is Mario's house.
import cvc5.pythonic as cz


def build(instance):
    n = instance["nHouses"]
    mh = instance["marioHouse"]
    lh = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc = instance["arc_fuel"]
    gold = instance["goldInHouse"]

    s = [cz.Int(f"s{i}") for i in range(n)]
    pos = [cz.Int(f"pos{i}") for i in range(n)]
    on = [cz.Bool(f"on{i}") for i in range(n)]
    x = [[cz.Bool(f"x{i}_{j}") for j in range(n)] for i in range(n)]

    constraints = []

    # Each house is on the route exactly when it does not succeed itself.
    for i in range(n):
        constraints.append(s[i] >= 0)
        constraints.append(s[i] <= n - 1)
        constraints.append(pos[i] >= 0)
        constraints.append(pos[i] <= n - 1)
        constraints.append(on[i] == Not_eq_self(s[i], i))
        for j in range(n):
            if j != i:
                constraints.append(x[i][j] == (s[i] == j))
        constraints.append(x[i][i] == False)

    # Each house on the route has exactly one successor, and each house on the route has
    # exactly one predecessor. The number of arcs leaving a house equals whether it is on the route.
    for i in range(n):
        constraints.append(cz.Sum([cz.If(x[i][j], 1, 0) for j in range(n)]) == cz.If(on[i], 1, 0))
        constraints.append(cz.Sum([cz.If(x[j][i], 1, 0) for j in range(n)]) == cz.If(on[i], 1, 0))

    # Mario's house starts the route and is on it. Luigi's house ends the route and its
    # successor is Mario's house.
    constraints.append(on[mh] == True)
    constraints.append(on[lh] == True)
    constraints.append(s[lh] == mh)
    constraints.append(pos[mh] == 0)

    # Positions along the route: each step from a house other than Luigi's advances one position,
    # so the route is a single path from Mario's house to Luigi's house with no separate loops.
    for i in range(n):
        if i == lh:
            continue
        for j in range(n):
            if j != i:
                constraints.append(cz.Implies(x[i][j], pos[j] == pos[i] + 1))

    # Fuel used by the route: the travel arc from each house to its successor, summed over the
    # route, must stay within the fuel limit.
    fuel = cz.Sum([cz.If(x[i][j], arc[i][j], 0) for i in range(n) for j in range(n) if j != i])
    constraints.append(fuel <= fuel_limit)

    # Gold collected: the gold in each house on the route.
    total_gold = cz.Sum([cz.If(on[i], gold[i], 0) for i in range(n)])

    outputs = {"s": [s[i] for i in range(n)]}
    return constraints, outputs, ("maximize", total_gold)


def Not_eq_self(si, i):
    return cz.Not(si == i)
