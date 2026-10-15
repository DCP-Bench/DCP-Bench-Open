"""Multi-commodity transportation: ship each product from the origins to the
destinations at minimal total cost, within supplies, demands and lane limits.

Shipment integers are binary encoded: a shipment x[i][j][p] is the weighted sum
of its bits, with weights 1, 2, 4, ... and an explicit upper bound.
"""

from paramita.modelling import Bool


def binary(name, ub):
    """Binary encoding of an integer in 0..ub, returned as (weight, bit) pairs."""
    nbits = max(1, ub.bit_length())
    return [(2**k, Bool(f"{name}_bit_{k}")) for k in range(nbits)]


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]

    n_o = len(supply)  # origins
    n_d = len(demand)  # destinations
    n_p = len(supply[0])  # products

    # x[i][j][p]: units of product p from origin i to destination j, bounded by
    # the smallest of the supply, the demand and the lane limit.
    x = [[[None] * n_p for _ in range(n_d)] for _ in range(n_o)]
    cons = []
    for i in range(n_o):
        for j in range(n_d):
            for p in range(n_p):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                wb = binary(f"x_{i}_{j}_{p}", ub)
                x[i][j][p] = sum(w * b for w, b in wb)
                cons.append(x[i][j][p] <= ub)

    # Each origin ships no more than its supply of each product.
    for i in range(n_o):
        for p in range(n_p):
            cons.append(sum(x[i][j][p] for j in range(n_d)) <= supply[i][p])

    # Each destination receives exactly its demand of each product.
    for j in range(n_d):
        for p in range(n_p):
            cons.append(sum(x[i][j][p] for i in range(n_o)) == demand[j][p])

    # The lane from origin i to destination j carries at most limit[i][j] units,
    # summed over all products.
    for i in range(n_o):
        for j in range(n_d):
            cons.append(sum(x[i][j][p] for p in range(n_p)) <= limit[i][j])

    # Total shipping cost of all products.
    total = sum(
        cost[i][j][p] * x[i][j][p]
        for i in range(n_o)
        for j in range(n_d)
        for p in range(n_p)
    )

    outputs = {"total_cost": total}
    return cons, outputs, ("minimize", total)
