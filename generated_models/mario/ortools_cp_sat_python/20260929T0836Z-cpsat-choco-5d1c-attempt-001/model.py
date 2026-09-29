# Mario's gold: Mario walks from his house to Luigi's, visiting some of the
# other houses on the way and collecting the gold in each visited house. The
# fuel used by the trip may not exceed the limit; collect as much gold as possible.
from ortools.sat.python import cp_model


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]  # fuel from house i to house j
    gold = instance["goldInHouse"]

    model = cp_model.CpModel()

    # The route is a circuit: Mario's house -> ... -> Luigi's house -> back to
    # Mario's house, with the houses that are not visited left as self-loops.
    # go[i][j] is true when the route leaves house i for house j; go[i][i] is
    # true when house i is not on the route.
    go = [[model.new_bool_var(f"go_{i}_{j}") for j in range(n)] for i in range(n)]
    model.add_circuit([(i, j, go[i][j]) for i in range(n) for j in range(n)])

    # Luigi's house is followed by Mario's, which closes the circuit
    model.add(go[luigi][mario] == 1)

    # s[i] = the house that follows house i (i itself if house i is not on the route)
    s = [model.new_int_var(0, n - 1, f"s_{i}") for i in range(n)]
    for i in range(n):
        model.add(s[i] == sum(j * go[i][j] for j in range(n)))

    # the fuel used along the route stays within the limit
    model.add(sum(arc_fuel[i][j] * go[i][j] for i in range(n) for j in range(n)) <= fuel_limit)

    # gold is collected in every house on the route, that is, every house that is not a self-loop
    model.maximize(sum(gold[i] * (1 - go[i][i]) for i in range(n)))

    return model, {"s": s}
