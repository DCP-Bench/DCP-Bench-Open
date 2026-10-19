# Mario: collect as much gold as possible on a route that starts at Mario's house
# and ends at Luigi's house. Travel between houses consumes fuel, and the route
# must not exceed the fuel limit. Output s[i] is the house succeeding house i
# (s[i] = i if house i is not part of the route); Luigi's successor is Mario's house.
import mip


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]
    limit = instance["fuelLimit"]

    m = mip.Model(sense=mip.MAXIMIZE, solver_name="CBC")
    m.verbose = 0

    # x[i][j] = 1 when the route travels directly from house i to house j
    x = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                x[i][j] = m.add_var(f"x_{i}_{j}", var_type=mip.BINARY)
    # v[i] = 1 when house i is on the route
    v = [m.add_var(f"v_{i}", var_type=mip.BINARY) for i in range(n)]
    # u[i] = position of house i along the route, Mario's house at 0
    u = [m.add_var(f"u_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER) for i in range(n)]
    # s[i] = successor of house i on the route, or i itself when off the route
    s = [m.add_var(f"s_{i}", lb=0, ub=n - 1, var_type=mip.INTEGER) for i in range(n)]

    # The route starts at Mario's house and ends at Luigi's house
    m += v[mario] == 1
    m += v[luigi] == 1
    m += u[mario] == 0

    # For Luigi's house, the succeeding house should be Mario's house
    m += x[luigi][mario] == 1

    # Each house on the route has one succeeding and one preceding house; houses
    # not on the route have none
    for i in range(n):
        m += mip.xsum(x[i][j] for j in range(n) if j != i) == v[i]
        m += mip.xsum(x[j][i] for j in range(n) if j != i) == v[i]

    # The route is one path from Mario's house to Luigi's house, with no separate
    # loops among the other houses (positions increase along each arc, except the
    # arc back to Mario's house)
    for i in range(n):
        for j in range(n):
            if i != j and j != mario:
                m += u[j] >= u[i] + 1 - n * (1 - x[i][j])

    # Mario has a fuel limit: the total fuel of the route must not exceed it
    m += mip.xsum(fuel[i][j] * x[i][j] for i in range(n) for j in range(n) if i != j) <= limit

    # s[i] is the house succeeding house i, or i itself when house i is not on the route
    for i in range(n):
        m += s[i] == mip.xsum(j * x[i][j] for j in range(n) if j != i) + i - i * v[i]

    # Maximise the gold collected from the houses on the route
    m.objective = mip.xsum(gold[i] * v[i] for i in range(n))

    return m, {"s": s}
