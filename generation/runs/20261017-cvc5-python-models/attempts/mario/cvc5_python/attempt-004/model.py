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

    # Shortest fuel distances between houses, computed from the fuel data (Floyd-Warshall).
    # Any route from Mario's house through i and j to Luigi's house and back costs at least
    # the sum of these distances plus the arc fuel, so it bounds which arcs and houses are usable.
    d = [[0 if i == j else fuel[i][j] for j in range(n)] for i in range(n)]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if d[i][k] + d[k][j] < d[i][j]:
                    d[i][j] = d[i][k] + d[k][j]

    s = cz.SolverFor("QF_LIA")

    # x[i][j] = 1 when the route goes directly from house i to house j.
    # x[i][i] = 1 when house i is not part of the route (a skipped house is its own successor).
    x = [[cz.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]
    # ge[i][k] = 1 when house i is at position k or later on the route (order encoding of
    # the position, counted from Mario's house, which is at position 0).
    ge = [[cz.Bool(f"ge_{i}_{k}") for k in range(n)] for i in range(n)]

    # Mario's house starts the route and Luigi's house is on it; Luigi's successor is Mario's house.
    s.add(cz.Not(x[m][m]), cz.Not(x[l][l]), x[l][m])
    # Mario's house is at position 0.
    for k in range(1, n):
        s.add(cz.Not(ge[m][k]))
    # Positions are monotone: being at position k+1 or later implies being at position k or later.
    for i in range(n):
        for k in range(1, n - 1):
            s.add(cz.Implies(ge[i][k + 1], ge[i][k]))

    # Each house has one successor (itself when skipped) and one predecessor.
    for i in range(n):
        s.add(cz.Or([x[i][j] for j in range(n)]))
        for a in range(n):
            for b in range(a + 1, n):
                s.add(cz.Or(cz.Not(x[i][a]), cz.Not(x[i][b])))
    for j in range(n):
        s.add(cz.Or([x[i][j] for i in range(n)]))
        for a in range(n):
            for b in range(a + 1, n):
                s.add(cz.Or(cz.Not(x[a][j]), cz.Not(x[b][j])))

    # Mario's house has Luigi's house as its only predecessor, since the route closes at Mario's house.
    for i in range(n):
        if i != l and i != m:
            s.add(cz.Not(x[i][m]))

    # A house whose cheapest round trip from Mario's house via Luigi's house exceeds the fuel
    # limit cannot be on the route. An arc whose cheapest completion of the route exceeds the
    # fuel limit cannot be used.
    for i in range(n):
        if i != m and i != l and d[m][i] + d[i][l] + d[l][m] > limit:
            s.add(x[i][i])
    for i in range(n):
        for j in range(n):
            if i == j or i == l or j == m:
                continue
            if d[m][i] + fuel[i][j] + d[j][l] + d[l][m] > limit:
                s.add(cz.Not(x[i][j]))

    # Only one route: a house other than Mario's has a larger position than its predecessor.
    # This removes cycles that do not pass through Mario's house.
    for i in range(n):
        for j in range(n):
            if i == j or j == m:
                continue
            # The successor of a route house is at a position one after its own.
            s.add(cz.Implies(x[i][j], ge[j][1]))
            if i != m:
                for k in range(1, n - 1):
                    s.add(cz.Or(cz.Not(x[i][j]), cz.Not(ge[i][k]), ge[j][k + 1]))
                s.add(cz.Or(cz.Not(x[i][j]), cz.Not(ge[i][n - 1])))

    # The fuel used from Mario's house up to each house stays within the fuel limit.
    # fuel_to[i] is the fuel spent on the route before house i, so along each route arc the
    # running fuel grows by the arc's fuel.
    fuel_to = [cz.Int(f"fuel_to_{i}") for i in range(n)]
    for i in range(n):
        s.add(fuel_to[i] >= 0, fuel_to[i] <= limit)
    s.add(fuel_to[m] == 0)
    for i in range(n):
        for j in range(n):
            if i == j or j == m or i == l:
                continue
            s.add(cz.Implies(x[i][j], fuel_to[j] >= fuel_to[i] + fuel[i][j]))

    # The fuel used along the route stays within the fuel limit.
    s.add(cz.Sum([cz.If(x[i][j], fuel[i][j], 0) for i in range(n) for j in range(n) if i != j]) <= limit)

    # Output: the successor of each house (its own index when skipped).
    succ = [cz.Sum([cz.If(x[i][j], j, 0) for j in range(n)]) for i in range(n)]

    # Objective: gold collected from the houses on the route.
    gold_total = cz.Sum([cz.If(cz.Not(x[i][i]), gold[i], 0) for i in range(n)])

    return s, {"s": succ}, ("maximize", gold_total)
