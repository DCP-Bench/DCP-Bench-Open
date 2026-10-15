# Mario: pick a route from Mario's house to Luigi's house that collects the most gold within a fuel limit.
from pyscipopt import Model, quicksum


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]

    m = Model()

    # arc[i, j] = 1 if Mario drives directly from house i to house j.
    # Luigi's house has one outgoing arc, back to Mario's house. That closing arc
    # is not a real trip: the data sets its fuel to 0.
    # Arcs into Mario's house come only from Luigi's house, and Luigi's house has no other exits.
    arcs = {}
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if j == mario and i != luigi:
                continue
            if i == luigi and j != mario:
                continue
            arcs[i, j] = m.addVar(name=f"arc_{i}_{j}", vtype="B")

    # visited[i] = 1 if house i is on the route (driven into and out of).
    visited = {}
    for i in range(n):
        if i == mario or i == luigi:
            visited[i] = 1
        else:
            visited[i] = m.addVar(name=f"visited_{i}", vtype="B")

    # Mario's house is the start and Luigi's house the end: the closing arc is forced on.
    m.addCons(arcs[luigi, mario] == 1)

    # one departure per visited house, one arrival per visited house, none for houses off the route
    # (each house on the route is entered and left exactly once)
    for i in range(n):
        out_arcs = [arcs[i, j] for j in range(n) if (i, j) in arcs]
        in_arcs = [arcs[j, i] for j in range(n) if (j, i) in arcs]
        if i == mario:
            m.addCons(quicksum(out_arcs) == 1)
        elif i == luigi:
            m.addCons(quicksum(in_arcs) == 1)
        else:
            m.addCons(quicksum(out_arcs) == visited[i])
            m.addCons(quicksum(in_arcs) == visited[i])

    # no separate loops: the route is numbered from Mario's house, and each used arc goes to a
    # house with a higher number (Miller-Tucker-Zemlin subtour elimination)
    order = {}
    for i in range(n):
        if i == mario:
            order[i] = m.addVar(name="order_0", vtype="I", lb=0, ub=0)
        else:
            order[i] = m.addVar(name=f"order_{i}", vtype="I", lb=1, ub=n - 1)
    # an arc i -> j used means house j comes after house i in the route
    for (i, j), a in arcs.items():
        if j == mario:
            continue
        m.addConsIndicator(order[j] - order[i] >= 1, binvar=a)

    # the fuel used along the route stays within the limit (the closing arc is free)
    m.addCons(
        quicksum(fuel[i][j] * a for (i, j), a in arcs.items() if (i, j) != (luigi, mario))
        <= fuel_limit
    )

    # objective: total gold in the houses visited on the route
    m.setObjective(
        quicksum(gold[i] * visited[i] for i in range(n) if i not in (mario, luigi))
        + gold[mario] + gold[luigi],
        "maximize",
    )

    # output: s[i] is the house after house i on the route; houses off the route point to themselves
    # visited house: successor is the target of its outgoing arc; off the route: s[i] = i
    succ = []
    for i in range(n):
        out_arcs = [(j, arcs[i, j]) for j in range(n) if (i, j) in arcs]
        succ.append(
            quicksum(j * a for j, a in out_arcs)
            + i * (1 - quicksum(a for _, a in out_arcs))
        )
    return m, {"s": succ}
