# Multi-commodity transportation: ship several products from origins to destinations, within each
# origin's supply of each product, meeting each destination's demand for each product and
# respecting a limit on the total amount shipped along each origin-destination lane. Minimise
# the total shipping cost.
from exact import Exact


def build(instance):
    supply = instance["supply"]  # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p required at destination j
    limit = instance["limit"]  # limit[i][j]: most units of all products shipped from i to j
    cost = instance["cost"]  # cost[i][j][p]: cost per unit of product p from origin i to j
    n_origins = len(supply)
    n_destinations = len(demand)
    n_products = len(supply[0])
    # as in the reference, no single shipment exceeds the largest supply, and the cost cannot
    # exceed shipping every unit supplied at the highest unit cost
    max_supply = max(max(row) for row in supply)
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    solver = Exact()

    # x[i][j][p] is the number of units of product p shipped from origin i to destination j
    x = [[[f"x_{i}_{j}_{p}" for p in range(n_products)] for j in range(n_destinations)]
         for i in range(n_origins)]
    for i in range(n_origins):
        for j in range(n_destinations):
            for p in range(n_products):
                solver.addVariable(x[i][j][p], 0, max_supply)

    # an origin cannot ship more of a product than it has
    for i in range(n_origins):
        for p in range(n_products):
            solver.addConstraint([(1, x[i][j][p]) for j in range(n_destinations)], False, 0, True, supply[i][p])

    # a destination must receive at least the demanded amount of each product
    for j in range(n_destinations):
        for p in range(n_products):
            solver.addConstraint([(1, x[i][j][p]) for i in range(n_origins)], True, demand[j][p])

    # the total amount shipped along a lane is at most its limit
    for i in range(n_origins):
        for j in range(n_destinations):
            solver.addConstraint([(1, x[i][j][p]) for p in range(n_products)], False, 0, True, limit[i][j])

    # total_cost is the cost of all shipments
    solver.addVariable("total_cost", 0, max_total_cost)
    shipping = [(cost[i][j][p], x[i][j][p]) for i in range(n_origins) for j in range(n_destinations)
                for p in range(n_products) if cost[i][j][p]]
    solver.addConstraint(shipping + [(-1, "total_cost")], True, 0, True, 0)

    # minimise the total shipping cost
    return solver, {"total_cost": "total_cost"}, ("minimize", [(1, "total_cost")])
