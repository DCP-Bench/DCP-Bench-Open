# Mario collects gold: he drives from Mario's house through some of the other houses to Luigi's
# house on limited fuel, then returns to the start; maximise the gold in the houses he visits.
import cpmpy as cp


def build(instance):
    n_houses = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j] = fuel to drive from house i to house j
    gold = instance["goldInHouse"]   # gold available in each house
    houses = range(n_houses)

    # s[i] = the house that follows house i on the route; s[i] = i if house i is not visited
    s = cp.intvar(0, n_houses - 1, shape=n_houses, name="s")

    model = cp.Model()

    # Every house has its own successor, so the route is a permutation: whatever is not visited
    # points to itself, and the visited houses form cycles.
    model += cp.AllDifferent(s)

    # The route closes up: Luigi's house is followed by Mario's house.
    model += s[luigi] == mario

    # Auxiliary: order[i] = position of house i along the route from Mario's house (1, 2, ...).
    # Houses off the route also get a position (see below), so all positions are distinct.
    order = cp.intvar(1, n_houses, shape=n_houses, name="order")
    model += cp.AllDifferent(order)

    # The route starts at Mario's house.
    model += order[mario] == 1

    # Going from a visited house to its successor advances the position by one, except for the
    # step back to Mario's house that closes the route. This makes the visited houses one single
    # cycle through Mario's and Luigi's houses; a second, separate cycle would need positions
    # that increase all the way around, which is impossible.
    for i in houses:
        model += ((s[i] != i) & (s[i] != mario)).implies(order[s[i]] == order[i] + 1)

    # A house is either on the route (s[i] != i) or numbered after Luigi's house, so the
    # positions 1..k along the route are not shared with houses that are left out.
    for i in houses:
        model += (s[i] != i) | (order[luigi] < order[i])

    # The fuel used on the route (arc_fuel[i][i] = 0, so unvisited houses cost nothing)
    # stays within the fuel limit.
    model += cp.sum([cp.cpm_array(arc_fuel[i])[s[i]] for i in houses]) <= fuel_limit

    # Objective: maximise the gold in the houses visited (those with s[i] != i).
    model.maximize(cp.sum([(s[i] != i) * gold[i] for i in houses]))

    return model, {"s": s}
