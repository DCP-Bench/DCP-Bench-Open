"""Multi-commodity transportation: ship every product from the origins to the destinations
at minimum total shipping cost, within supplies, demands and lane limits.

Each shipment x[i][j][p] (units of product p from origin i to destination j) is an integer
encoded in unary: bits[k] means x >= k+1. The unary order makes the sums and bounds linear
over the bits.
"""
from paramita.modelling import Bool, If


def build(instance):
    supply = instance["supply"]  # supply[i][p]
    demand = instance["demand"]  # demand[j][p]
    limit = instance["limit"]    # limit[i][j], shipments of all products on lane i -> j
    cost = instance["cost"]      # cost[i][j][p], cost per unit of product p on lane i -> j
    n_orig, n_dest, n_prod = len(supply), len(demand), len(supply[0])

    # unary bits for each shipment; the upper bound is the tightest of the three limits
    ship = {}
    cons = []
    for i in range(n_orig):
        for j in range(n_dest):
            for p in range(n_prod):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                bits = [Bool(f"ship_{i}_{j}_{p}_ge_{k}") for k in range(1, ub + 1)]
                # order of the unary bits: x >= k+1 implies x >= k
                cons += [If(bits[k], bits[k - 1]) for k in range(1, len(bits))]
                ship[(i, j, p)] = bits

    # origin supply: the product p shipped out of origin i does not exceed its supply
    for i in range(n_orig):
        for p in range(n_prod):
            out = [b for j in range(n_dest) for b in ship[(i, j, p)]]
            if out:
                cons.append(sum(out) <= supply[i][p])

    # destination demand: the product p delivered to destination j equals its demand
    for j in range(n_dest):
        for p in range(n_prod):
            inc = [b for i in range(n_orig) for b in ship[(i, j, p)]]
            if inc:
                cons.append(sum(inc) == demand[j][p])
            else:
                assert demand[j][p] == 0, "demand cannot be met: no shipment can reach it"

    # lane limit: all products together shipped from origin i to destination j stay within the limit
    for i in range(n_orig):
        for j in range(n_dest):
            lane = [b for p in range(n_prod) for b in ship[(i, j, p)]]
            if lane:
                cons.append(sum(lane) <= limit[i][j])

    # total shipping cost: each unit of product p on lane i -> j costs cost[i][j][p]
    total = sum(
        cost[i][j][p] * b
        for (i, j, p), bits in ship.items()
        for b in bits
    )
    return cons, {"total_cost": total}, ("minimize", total)
