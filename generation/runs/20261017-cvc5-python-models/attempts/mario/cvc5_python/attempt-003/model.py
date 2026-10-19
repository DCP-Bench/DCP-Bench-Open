# Mario: Mario collects as much gold as possible by visiting houses. He starts at Mario's
# house and ends at Luigi's house. Each house has gold, travel between houses consumes fuel,
# and the route must not exceed the fuel limit. Output s[i] is the house succeeding house i
# (s[i] = i if the house is not part of the route); the successor of Luigi's house is Mario's house.
import cvc5.pythonic as cz


def build(instance):
    n = instance["nHouses"]
    m = instance["marioHouse"]
    l = instance["luigiHouse"]
    limit = instance["fuelLimit"]
    fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]

    s = cz.SolverFor("QF_LIA")

    # go[i][j] = 1 when the route goes directly from house i to house j.
    # go[i][i] = 1 when house i is not part of the route.
    go = [[cz.Int(f"go_{i}_{j}") for j in range(n)] for i in range(n)]
    # order[i] = position of house i on the route, counted from Mario's house.
    order = [cz.Int(f"order_{i}") for i in range(n)]

    # Bounds on the 0/1 arc variables and on the positions.
    for i in range(n):
        for j in range(n):
            s.add(go[i][j] >= 0, go[i][j] <= 1)
        s.add(order[i] >= 0, order[i] <= n - 1)

    # Mario's house starts the route and Luigi's house is on it; Luigi's successor is Mario's house.
    s.add(go[m][m] == 0, go[l][l] == 0, go[l][m] == 1, order[m] == 0)

    # An arc whose fuel alone exceeds the fuel limit cannot be used.
    for i in range(n):
        for j in range(n):
            if i != j and fuel[i][j] > limit:
                s.add(go[i][j] == 0)

    # Each house has one successor (itself when skipped) and one predecessor.
    for i in range(n):
        s.add(cz.Sum([go[i][j] for j in range(n)]) == 1)
    for j in range(n):
        s.add(cz.Sum([go[i][j] for i in range(n)]) == 1)

    # Only one route: the positions increase along every arc into a house other than Mario's.
    # This removes cycles that do not pass through Mario's house.
    for i in range(n):
        for j in range(n):
            if i != j and j != m:
                s.add(order[j] >= order[i] + 1 - (n - 1) + (n - 1) * go[i][j])

    # The fuel used along the route stays within the fuel limit.
    s.add(cz.Sum([fuel[i][j] * go[i][j] for i in range(n) for j in range(n) if i != j]) <= limit)

    # Output: the successor of each house.
    succ = [cz.Sum([j * go[i][j] for j in range(n)]) for i in range(n)]

    # Objective: gold collected from the houses on the route.
    gold_total = cz.Sum([gold[i] * (1 - go[i][i]) for i in range(n)])

    return s, {"s": succ}, ("maximize", gold_total)
