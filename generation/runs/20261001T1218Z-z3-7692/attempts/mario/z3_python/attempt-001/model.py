# Mario's gold: Mario drives from his house to Luigi's house through some of the other houses,
# collecting the gold in each house he visits, with a limited amount of fuel. The route is
# written as the successor of each house; maximize the gold collected.
import z3


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]       # 0-indexed
    luigi = instance["luigiHouse"]       # 0-indexed
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]      # arc_fuel[i][j] = fuel to drive from house i to j
    gold_in_house = instance["goldInHouse"]

    # s[i] is the house after house i on the route, and s[i] = i if house i is not on the
    # route. Luigi's house is followed by Mario's house, which closes the route into a cycle.
    s = [z3.Int(f"s_{i}") for i in range(n)]
    # go[i][j] is true if s[i] = j. Used so that the fuel and the gold are plain sums.
    go = [[s[i] == j for j in range(n)] for i in range(n)]
    # order[i] is the rank of house i on the route from Mario's house (rank 1) to Luigi's.
    order = [z3.Int(f"order_{i}") for i in range(n)]

    solver = z3.Solver()

    for i in range(n):
        solver.add(s[i] >= 0, s[i] <= n - 1)
        solver.add(order[i] >= 1, order[i] <= n)

    # Every house is the successor of exactly one house, itself included (the successors are
    # all different). This is a pseudo-Boolean equality per house, which Z3 handles better
    # than Distinct.
    for j in range(n):
        solver.add(z3.PbEq([(go[i][j], 1) for i in range(n)], 1))

    # The route starts at Mario's house, which has rank 1, and ends at Luigi's house, which
    # is followed by Mario's house.
    solver.add(order[mario] == 1)
    solver.add(s[luigi] == mario)

    # Rank progression: for a house on the route, its successor has the next rank, except
    # for the last arc from Luigi's house back to Mario's. The ranks increase along the
    # route, so no separate cycle (subtour) can exist among the other houses. The reference
    # also makes all ranks different and puts the ranks of the houses off the route
    # after Luigi's rank; both can always be arranged for any route, so they are left out.
    for i in range(n):
        for j in range(n):
            if j != i and j != mario:
                solver.add(z3.Implies(go[i][j], order[j] == order[i] + 1))

    # Fuel: the arcs of the route (the arc from each house to its successor, with a house
    # off the route costing arc_fuel[i][i]) use at most the fuel limit.
    fuel = z3.Sum([z3.If(go[i][j], arc_fuel[i][j], 0) for i in range(n) for j in range(n)])
    solver.add(fuel <= fuel_limit)

    # Gold collected: the gold of every house that is on the route (s[i] != i).
    gold = z3.Sum([z3.If(go[i][i], 0, gold_in_house[i]) for i in range(n)])

    # Maximize the gold.
    return solver, {"s": s}, ("maximize", gold)
