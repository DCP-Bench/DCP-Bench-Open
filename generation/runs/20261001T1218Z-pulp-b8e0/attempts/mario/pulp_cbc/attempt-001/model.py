"""Mario: Mario collects as much gold as possible by visiting houses. He starts at Mario's
house and ends at Luigi's house; travelling between houses uses fuel and he has a limited
amount of fuel. Maximise the gold in the houses on his route.

The model reports, for every house, the house that follows it on the route (the house
itself if it is not on the route); Luigi's house is followed by Mario's house.
"""
import pulp


def build(instance):
    n = instance["nHouses"]  # number of houses
    mario = instance["marioHouse"]  # 0-based
    luigi = instance["luigiHouse"]  # 0-based
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j] = fuel to travel from house i to house j
    gold = instance["goldInHouse"]  # gold in each house

    problem = pulp.LpProblem("mario", pulp.LpMaximize)

    # go[i][j] = 1 if house j is the successor s[i] of house i. Every house has exactly one
    # successor and is the successor of exactly one house (the successors are all different),
    # so go is a permutation matrix: the route is one cycle Mario -> ... -> Luigi -> Mario,
    # and every house off the route is its own successor.
    go = pulp.LpVariable.dicts("go", (range(n), range(n)), cat="Binary")
    for i in range(n):
        problem += pulp.lpSum(go[i][j] for j in range(n)) == 1
        problem += pulp.lpSum(go[j][i] for j in range(n)) == 1
    s = [pulp.LpVariable(f"s_{i}", 0, n - 1, cat="Integer") for i in range(n)]
    for i in range(n):
        problem += s[i] == pulp.lpSum(j * go[i][j] for j in range(n))

    # The route ends at Luigi's house, which is followed by Mario's house.
    problem += go[luigi][mario] == 1

    # Houses on the route have a rank along it, starting with 1 at Mario's house. A house that
    # follows another one (other than going back to Mario's house) has a rank at least one
    # higher, which rules out a cycle that does not pass through Mario's house. The reference
    # makes this rank exact and numbers the houses off the route after Luigi's house; such
    # numbers always exist, so asking only "at least one higher" allows the same routes.
    # Ranks are continuous: the rank of a house on the route is then determined by the route.
    order = [pulp.LpVariable(f"order_{i}", 1, n) for i in range(n)]
    problem += order[mario] == 1
    for i in range(n):
        for j in range(n):
            if j != i and j != mario:
                # if j follows i, j ranks at least one above i (slack n - 1 when not)
                problem += order[j] >= order[i] + 1 - (n - 1) * (1 - go[i][j])

    # The fuel used (the arcs of the route, including the last one back to Mario's house) is
    # within the limit.
    problem += pulp.lpSum(arc_fuel[i][j] * go[i][j] for i in range(n) for j in range(n)) \
        <= fuel_limit

    # maximise the gold of the houses on the route (those that are not their own successor)
    problem += pulp.lpSum(gold[i] * (1 - go[i][i]) for i in range(n))

    return problem, {"s": s}
