"""Arch friends: Harriet bought four pairs of shoes (ecru espadrilles, fuchsia flats, purple
pumps, suede sandals) at four different stores (Foot Farm, Heels in a Handcart, The Shoe
Palace, Tootsies). Find the order of the stops and what she bought where.

The model reports, for each shoe and each store, its stop number 1..4.
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its names are below

    n = 4
    stops = range(1, n + 1)
    shoe_names = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    store_names = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    problem = pulp.LpProblem("arch_friends", pulp.LpMinimize)  # satisfaction

    # at[name][s] = 1 if the shoe (or store) named is bought (visited) at stop s. Every
    # shoe and every store gets a different stop: a one-to-one matching within each group.
    at = {name: {s: pulp.LpVariable(f"at_{name}_{s}", cat="Binary") for s in stops}
          for name in shoe_names + store_names}
    for group in (shoe_names, store_names):
        for name in group:
            problem += pulp.lpSum(at[name].values()) == 1
        for s in stops:
            problem += pulp.lpSum(at[name][s] for name in group) == 1
    stop = {name: pulp.lpSum(s * at[name][s] for s in stops) for name in at}

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    problem += stop["fuchsiaflats"] == stop["heelsinahandcart"]

    # 2. The store she visited just after buying her purple pumps was not Tootsies.
    for s in stops:
        if s + 1 in stops:
            problem += at["purplepumps"][s] + at["tootsies"][s + 1] <= 1

    # 3. The Foot Farm was Harriet's second stop.
    problem += at["footfarm"][2] == 1

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    problem += stop["theshoepalace"] + 2 == stop["suedesandals"]

    return problem, stop
