"""Arch friends: find the order (1..4) in which Harriet bought four pairs of shoes and the store where she bought each."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    # The puzzle has no instance data: the shoes, stores and clues are the puzzle's
    # own, mirrored from the reference.
    n = 4
    stops = range(1, n + 1)
    shoe_names = ["ecruespadrilles", "fuchsiaflats", "purplepumps", "suedesandals"]
    store_names = ["footfarm", "heelsinahandcart", "theshoepalace", "tootsies"]

    model = gp.Model("arch_friends")

    # shoe_at[s, k] is 1 when shoe s was bought at stop k; store_at[t, k] likewise for
    # store t. Different shoes (stores) come at different stops.
    shoe_at = model.addVars(n, stops, vtype=GRB.BINARY, name="shoe_at")
    store_at = model.addVars(n, stops, vtype=GRB.BINARY, name="store_at")
    for x in (shoe_at, store_at):
        for i in range(n):
            model.addConstr(x.sum(i, "*") == 1)
        for k in stops:
            model.addConstr(x.sum("*", k) == 1)

    shoe = {s: gp.quicksum(k * shoe_at[i, k] for k in stops) for i, s in enumerate(shoe_names)}
    store = {t: gp.quicksum(k * store_at[i, k] for k in stops) for i, t in enumerate(store_names)}
    ecru, fuchsia, purple, suede = range(n)
    footfarm, heels, palace, tootsies = range(n)

    # 1. Harriet bought fuchsia flats at Heels in a Handcart.
    model.addConstr(shoe["fuchsiaflats"] == store["heelsinahandcart"])

    # 2. The store she visited just after buying her purple pumps was not Tootsies:
    #    purple pumps at stop k and Tootsies at stop k + 1 never both hold.
    for k in stops:
        if k + 1 in stops:
            model.addConstr(shoe_at[purple, k] + store_at[tootsies, k + 1] <= 1)

    # 3. The Foot Farm was Harriet's second stop.
    model.addConstr(store_at[footfarm, 2] == 1)

    # 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
    model.addConstr(store["theshoepalace"] + 2 == shoe["suedesandals"])

    return model, {**shoe, **store}
