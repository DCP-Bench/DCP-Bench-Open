# Mario collects gold: starting at Mario's house and ending at Luigi's, Mario visits houses that
# hold gold, burning fuel on every road he takes, and he has a limited amount of fuel. Choose
# the route that collects the most gold. The route is given by the successor of every house; a
# house that is not on the route is its own successor, and Luigi's successor is Mario's house.
from exact import Exact


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j]: fuel for going from house i to house j
    gold = instance["goldInHouse"]  # gold in each house

    solver = Exact()

    # succ[i][j] = 1 when house j is the successor of house i (j == i: i is not on the route)
    succ = [[f"succ_{i}_{j}" for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(n):
            solver.addVariable(succ[i][j], 0, 1)
    for i in range(n):
        # every house has exactly one successor
        solver.addConstraint([(1, succ[i][j]) for j in range(n)], True, 1, True, 1)
    for j in range(n):
        # the successors are all different: every house is the successor of exactly one house
        solver.addConstraint([(1, succ[i][j]) for i in range(n)], True, 1, True, 1)

    # s[i] is the house that follows house i
    s = [f"s_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(s[i], 0, n - 1)
        solver.addConstraint([(j, succ[i][j]) for j in range(1, n)] + [(-1, s[i])], True, 0, True, 0)

    # the route ends at Luigi's house, whose successor is Mario's house
    solver.addConstraint([(1, succ[luigi][mario])], True, 1, True, 1)

    # order[i] is the rank of house i along the route. It rules out loops that do not pass through
    # Mario's house. The reference also makes the ranks all different, which does not change which
    # successor arrays are possible (houses off the route can always be given distinct ranks
    # behind the route), so it is not repeated here.
    order = [f"order_{i}" for i in range(n)]
    for name in order:
        solver.addVariable(name, 1, n)

    # Mario's house is the start of the route, rank 1
    solver.addConstraint([(1, order[mario])], True, 1, True, 1)

    for i in range(n):
        for j in range(n):
            # rank progression: if j follows i on the route (j is not Mario's house, which closes
            # the loop) then j's rank is one more than i's. With n as the big M, written as two
            # inequalities: order[j] - order[i] = 1 when succ[i][j] = 1.
            if j != i and j != mario:
                solver.addConstraint([(1, order[j]), (-1, order[i]), (-n, succ[i][j])], True, 1 - n)
                solver.addConstraint([(1, order[j]), (-1, order[i]), (n, succ[i][j])], False, 0, True, 1 + n)
        # rank segregation: a house off the route (its own successor) ranks after Luigi's house
        solver.addConstraint([(1, order[i]), (-1, order[luigi]), (-n, succ[i][i])], True, 1 - n)

    # fuel: the roads taken (the successor arcs, with zero fuel for staying put) use at most the limit
    fuel = [(arc_fuel[i][j], succ[i][j]) for i in range(n) for j in range(n) if arc_fuel[i][j]]
    solver.addConstraint(fuel, False, 0, True, fuel_limit)

    # gold is earned in every house on the route, that is every house that is not its own successor
    # (visited[i] = 1 - succ[i][i])
    visited = [f"visited_{i}" for i in range(n)]
    for i in range(n):
        solver.addVariable(visited[i], 0, 1)
        solver.addConstraint([(1, visited[i]), (1, succ[i][i])], True, 1, True, 1)

    # maximise the gold collected
    return solver, {"s": s}, ("maximize", [(gold[i], visited[i]) for i in range(n) if gold[i]])
