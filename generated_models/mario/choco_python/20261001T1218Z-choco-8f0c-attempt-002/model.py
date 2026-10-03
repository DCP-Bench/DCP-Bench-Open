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

    # The houses on the route, closed by the arc from Luigi's house back to Mario's house,
    # form one circuit, and every house off the route is its own successor. That is exactly
    # a sub-circuit, which Choco has as one constraint; it stands in for the reference's rank
    # variables (every house has a distinct successor, ranks increase along the route, and
    # houses off the route cannot form a route of their own) and allows the same successors.
    route_length = model.intvar(2, n, name="route_length")  # number of houses on the route
    model.sub_circuit(s, 0, route_length).post()

    # the route ends at Luigi's house, which is followed by Mario's house
    model.arithm(s[luigi], "=", mario).post()

    # fuel used: the sum of the fuel of the arc leaving each house (0 for a house off the route,
    # since arc_fuel[i][i] = 0), at most the fuel limit
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
