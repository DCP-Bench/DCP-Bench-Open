# Mario: starting at Mario's house and ending at Luigi's house, collect as much gold as
# possible on a route through some of the houses, without using more fuel than the limit.
# The route is given by successors: s[i] is the house after house i, s[i] = i if house i is
# not on the route, and Luigi's house is followed by Mario's house.
from pychoco.model import Model


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]  # 0-indexed
    luigi = instance["luigiHouse"]  # 0-indexed
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # arc_fuel[i][j] = fuel needed to go from house i to house j
    gold_in_house = instance["goldInHouse"]

    model = Model()

    # s[i] = the house that succeeds house i on the route (s[i] = i if i is not on the route)
    s = [model.intvar(0, n - 1, name=f"s_{i}") for i in range(n)]
    # order[i] = rank of house i: 1 for Mario's house, then 2, 3, ... along the route
    order = [model.intvar(1, n, name=f"order_{i}") for i in range(n)]

    # every house has its own successor (the successors are a permutation of the houses),
    # and every house has its own rank
    model.all_different(s).post()
    model.all_different(order).post()

    # the route starts at Mario's house (rank 1) and ends at Luigi's house, which is
    # followed by Mario's house
    model.arithm(order[mario], "=", 1).post()
    model.arithm(s[luigi], "=", mario).post()

    for i in range(n):
        # Rank progression: if house i is on the route and its successor is not Mario's house
        # (that arc closes the route), the successor's rank is one higher.
        # successor_rank[i] = order[s[i]]
        successor_rank = model.intvar(1, n, name=f"successor_rank_{i}")
        model.element(successor_rank, order, s[i]).post()
        on_route_and_not_closing = model.and_([model.arithm(s[i], "!=", i), model.arithm(s[i], "!=", mario)])
        model.if_then(on_route_and_not_closing, model.arithm(successor_rank, "-", order[i], "=", 1))

        # Rank segregation: a house is on the route, or its rank is higher than Luigi's
        # (so houses off the route cannot form a route of their own).
        model.or_([model.arithm(s[i], "!=", i), model.arithm(order[luigi], "<", order[i])]).post()

    # Symmetry breaking on the auxiliary ranks only. The houses off the route take the ranks
    # above Luigi's in any order, and every order gives the same successors s. Fixing
    # them to increase with the house number removes those equivalent assignments;
    # the route and the declared output s are unchanged.
    for i in range(n):
        for j in range(i + 1, n):
            off_route_pair = model.and_([model.arithm(s[i], "=", i), model.arithm(s[j], "=", j)])
            model.if_then(off_route_pair, model.arithm(order[i], "<", order[j]))

    # fuel used: the sum of the fuel of the arc leaving each house (0 for a house off the route,
    # since arc_fuel[i][i] = 0)
    fuel = []
    for i in range(n):
        fuel_i = model.intvar(0, max(arc_fuel[i]), name=f"fuel_{i}")
        model.element(fuel_i, arc_fuel[i], s[i]).post()
        fuel.append(fuel_i)
    model.sum(fuel, "<=", fuel_limit).post()

    # gold collected: the gold of every house on the route (s[i] != i)
    # (the maximum is a variable because Choco optimises a single variable)
    on_route = [model.arithm(s[i], "!=", i).reify() for i in range(n)]
    gold = model.intvar(0, sum(gold_in_house), name="gold")
    model.scalar(on_route, gold_in_house, "=", gold).post()

    return model, {"s": s}, ("maximize", gold)
