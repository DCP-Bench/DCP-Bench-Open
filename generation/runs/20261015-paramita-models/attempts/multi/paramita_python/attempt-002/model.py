"""Multi-commodity transportation: ship every product from the origins to the destinations
at minimum total shipping cost, within supplies, demands and lane limits.

Each shipment x[i][j][p] (units of product p from origin i to destination j) is an integer
in binary: bit k has weight 2**k. A PB bound x <= ub keeps it within its tightest limit.
"""
from paramita.modelling import Bool


def build(instance):
    supply = instance["supply"]  # supply[i][p]
    demand = instance["demand"]  # demand[j][p]
    limit = instance["limit"]    # limit[i][j], shipments of all products on lane i -> j
    cost = instance["cost"]      # cost[i][j][p], cost per unit of product p on lane i -> j
    n_orig, n_dest, n_prod = len(supply), len(demand), len(supply[0])

    # binary bits for each shipment: a list of (weight, Bool) terms
    ship = {}
    cons = []
    for i in range(n_orig):
        for j in range(n_dest):
            for p in range(n_prod):
                # a shipment never exceeds the tightest of its supply, demand and lane limit
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                if ub == 0:
                    ship[(i, j, p)] = []
                    continue
                nb = ub.bit_length()
                terms = [(1 << k, Bool(f"ship_{i}_{j}_{p}_bit_{k}")) for k in range(nb)]
                if ub < (1 << nb) - 1:
                    cons.append(sum(w * b for w, b in terms) <= ub)
                ship[(i, j, p)] = terms

    # origin supply: the product p shipped out of origin i does not exceed its supply
    for i in range(n_orig):
        for p in range(n_prod):
            out = [t for j in range(n_dest) for t in ship[(i, j, p)]]
            if out:
                cons.append(sum(w * b for w, b in out) <= supply[i][p])

    # destination demand: the product p delivered to destination j equals its demand
    for j in range(n_dest):
        for p in range(n_prod):
            inc = [t for i in range(n_orig) for t in ship[(i, j, p)]]
            if inc:
                cons.append(sum(w * b for w, b in inc) == demand[j][p])
            else:
                assert demand[j][p] == 0, "demand cannot be met: no shipment can reach it"

    # lane limit: all products together shipped from origin i to destination j stay within the limit
    for i in range(n_orig):
        for j in range(n_dest):
            lane = [t for p in range(n_prod) for t in ship[(i, j, p)]]
            if lane:
                cons.append(sum(w * b for w, b in lane) <= limit[i][j])

    # total shipping cost: each unit of product p on lane i -> j costs cost[i][j][p]
    total = sum(
        cost[i][j][p] * w * b
        for (i, j, p), terms in ship.items()
        for w, b in terms
    )
    return cons, {"total_cost": total}, ("minimize", total)
