"""Multi-commodity transportation: ship every product from origins to destinations at the least total cost."""
from docplex.mp.model import Model


def build(instance):
    supply = instance["supply"]  # supply[i][p]: units of product p at origin i
    demand = instance["demand"]  # demand[j][p]: units of product p destination j needs
    limit = instance["limit"]    # limit[i][j]: most units, all products together, from i to j
    cost = instance["cost"]      # cost[i][j][p]: cost of shipping one unit of p from i to j
    origins = range(len(supply))
    destinations = range(len(demand))
    goods = range(len(supply[0]))

    # Bounds the reference model declares: no single shipment exceeds the largest
    # supply, and the total cost is at most all supply shipped at the dearest rate.
    max_supply = max(max(row) for row in supply)
    max_total_cost = sum(sum(row) for row in supply) * max(max(row) for matrix in cost for row in matrix)

    model = Model("multi")

    # x[i, j, p] is the amount of product p shipped from origin i to destination j.
    x = model.integer_var_cube(origins, destinations, goods, 0, max_supply, name="x")

    # No origin ships more of a product than it has.
    for i in origins:
        for p in goods:
            model.add_constraint(model.sum(x[i, j, p] for j in destinations) <= supply[i][p],
                                 ctname=f"supply_{i}_{p}")

    # Every destination receives at least the demand for each product.
    for j in destinations:
        for p in goods:
            model.add_constraint(model.sum(x[i, j, p] for i in origins) >= demand[j][p],
                                 ctname=f"demand_{j}_{p}")

    # The total shipped on each route stays within its limit.
    for i in origins:
        for j in destinations:
            model.add_constraint(model.sum(x[i, j, p] for p in goods) <= limit[i][j], ctname=f"limit_{i}_{j}")

    # total_cost is the cost of all shipments; a variable of its own so that the
    # declared output is this one integer rather than every shipment behind it.
    total_cost = model.integer_var(0, max_total_cost, name="total_cost")
    model.add_constraint(total_cost == model.sum(cost[i][j][p] * x[i, j, p]
                                                 for i in origins for j in destinations for p in goods),
                         ctname="cost")

    # Minimise the shipping cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost}
