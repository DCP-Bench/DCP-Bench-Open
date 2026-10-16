"""Multi-commodity transportation: ship each product from the origins to the
destinations at minimal total cost, within supplies, demands and lane limits.

Shipment integers are unary (order) encoded: x_bits[i][j][p][k] is true when
the number of units of product p shipped from origin i to destination j is at
least k + 1.
"""

from paramita.modelling import Bool, If


def unary(name, ub):
    """Order encoding of an integer in 0..ub, returned as (bits, constraints)."""
    bits = [Bool(f"{name}_ge_{k}") for k in range(1, ub + 1)]
    # value >= k + 1 implies value >= k
    cons = [If(bits[k], bits[k - 1]) for k in range(1, ub)]
    return bits, cons


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]

    n_o = len(supply)  # origins
    n_d = len(demand)  # destinations
    n_p = len(supply[0])  # products

    # x_bits[i][j][p]: units of product p from origin i to destination j.
    # Its upper bound is the smallest of the supply, the demand and the lane limit.
    x_bits = [[[None] * n_p for _ in range(n_d)] for _ in range(n_o)]
    x_val = [[[None] * n_p for _ in range(n_d)] for _ in range(n_o)]
    cons = []
    for i in range(n_o):
        for j in range(n_d):
            for p in range(n_p):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                bits, c = unary(f"x_{i}_{j}_{p}", ub)
                x_bits[i][j][p] = bits
                x_val[i][j][p] = sum(bits)
                cons += c

    # Each origin ships no more than its supply of each product.
    for i in range(n_o):
        for p in range(n_p):
            cons.append(sum(x_val[i][j][p] for j in range(n_d)) <= supply[i][p])

    # Each destination receives exactly its demand of each product.
    for j in range(n_d):
        for p in range(n_p):
            cons.append(sum(x_val[i][j][p] for i in range(n_o)) == demand[j][p])

    # The lane from origin i to destination j carries at most limit[i][j] units,
    # summed over all products.
    for i in range(n_o):
        for j in range(n_d):
            cons.append(sum(x_val[i][j][p] for p in range(n_p)) <= limit[i][j])

    # Total shipping cost of all products.
    total = sum(
        cost[i][j][p] * x_val[i][j][p]
        for i in range(n_o)
        for j in range(n_d)
        for p in range(n_p)
    )

    outputs = {"total_cost": total}
    return cons, outputs, ("minimize", total)
