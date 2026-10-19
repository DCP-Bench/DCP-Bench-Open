# Mario: collect as much gold as possible on a route from Mario's house to Luigi's house,
# visiting houses, with the route's fuel use within the fuel limit. Output s[i] is the house
# succeeding house i (s[i] = i if house i is not on the route); Luigi's successor is Mario's house.
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

    constraints = []

    # Successor domains: every house succeeds some house of the instance.
    # Each house succeeds one house: s is a permutation (non-route houses are fixed points).
    for i in range(n):
        constraints.append(s[i] >= 0)
        constraints.append(s[i] <= n - 1)
        constraints.append(pos[i] >= 0)
        constraints.append(pos[i] <= n - 1)
    constraints.append(cz.Distinct(s))

    # The route starts at Mario's house and ends at Luigi's house, which succeeds Mario's house.
    # Mario's house is always on the route, so it is not a fixed point.
    constraints.append(s[lh] == mh)
    constraints.append(s[mh] != mh)
    constraints.append(pos[mh] == 0)

    # A house is on the route exactly when it is not a fixed point.
    # Each route house visited in order: the successor of a route house (other than Luigi's)
    # is one step further along the route. This keeps the route one path with no subtours.
    # Route houses other than Luigi's advance the position by one to their successor.
    for i in range(n):
        if i == lh:
            continue
        for j in range(n):
            if j == i:
                continue
            constraints.append(cz.Implies(s[i] == j, pos[j] == pos[i] + 1))

    # The route cannot pass through a house twice, and the position order is fixed by the route.
    # Fuel used by the route: the travel from each route house to its successor must stay
    # within the fuel limit.
    fuel_terms = []
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            fuel_terms.append(cz.If(s[i] == j, arc[i][j], 0))
    constraints.append(cz.Sum(fuel_terms) <= fuel_limit)

    # Gold collected: sum of the gold in every house on the route.
    gold_terms = [cz.If(s[i] != i, gold[i], 0) for i in range(n)]
    total_gold = cz.Sum(gold_terms)

    outputs = {"s": [s[i] for i in range(n)]}
    return constraints, outputs, ("maximize", total_gold)
