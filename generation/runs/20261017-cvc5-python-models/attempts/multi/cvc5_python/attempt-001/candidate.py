# Multi-commodity transportation problem (cvc5, pythonic API).
#
# Origins i ship products p to destinations j. Each origin has a supply per product,
# each destination a demand per product, each (origin, destination) lane a total limit
# over all products, and each (origin, destination, product) unit a cost. Minimise the
# total shipping cost. Output: total_cost.

import cvc5.pythonic as cz


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    limit = instance["limit"]
    cost = instance["cost"]

    n_origins = len(supply)
    n_products = len(supply[0])
    n_destinations = len(demand)

    # x[i][j][p]: units of product p shipped from origin i to destination j.
    x = [[[cz.Int(f"x_{i}_{j}_{p}") for p in range(n_products)]
          for j in range(n_destinations)]
         for i in range(n_origins)]

    constraints = []

    # Shipments are non-negative and bounded by what the origin, the destination and the lane can carry.
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                constraints.append(x[i][j][p] >= 0)
                constraints.append(x[i][j][p] <= ub)

    # Each origin ships at most its supply of each product.
    for i in range(n_origins):
        for p in range(n_products):
            constraints.append(
                cz.Sum([x[i][j][p] for j in range(n_destinations)]) <= supply[i][p])

    # Each destination receives exactly its demand of each product.
    for j in range(n_destinations):
        for p in range(n_products):
            constraints.append(
                cz.Sum([x[i][j][p] for i in range(n_origins)]) == demand[j][p])

    # The total over all products on each lane stays within the lane limit.
    for i in range(n_origins):
        for j in range(n_destinations):
            constraints.append(
                cz.Sum([x[i][j][p] for p in range(n_products)]) <= limit[i][j])

    # Total shipping cost is the objective.
    total = cz.Sum([cost[i][j][p] * x[i][j][p]
                    for i in range(n_origins)
                    for j in range(n_destinations)
                    for p in range(n_products)])

    return constraints, {"total_cost": total}, ("minimize", total)
