"""Multi-commodity transportation: ship every product from origins to destinations at the least total cost."""
import gurobipy as gp
from gurobipy import GRB


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

    model = gp.Model("multi")

    # x[i, j, p] is the amount of product p shipped from origin i to destination j.
    x = model.addVars(origins, destinations, goods, lb=0, ub=max_supply, vtype=GRB.INTEGER, name="x")

    # No origin ships more of a product than it has.
    for i in origins:
        for p in goods:
            model.addConstr(x.sum(i, "*", p) <= supply[i][p], name=f"supply[{i},{p}]")

    # Every destination receives at least the demand for each product.
    for j in destinations:
        for p in goods:
            model.addConstr(x.sum("*", j, p) >= demand[j][p], name=f"demand[{j},{p}]")

    # The total shipped on each route stays within its limit.
    for i in origins:
        for j in destinations:
            model.addConstr(x.sum(i, j, "*") <= limit[i][j], name=f"limit[{i},{j}]")

    # total_cost is the cost of all shipments; a variable of its own so that the
    # declared output is this one integer rather than every shipment behind it.
    total_cost = model.addVar(lb=0, ub=max_total_cost, vtype=GRB.INTEGER, name="total_cost")
    model.addConstr(total_cost == gp.quicksum(cost[i][j][p] * x[i, j, p]
                                              for i in origins for j in destinations for p in goods),
                    name="cost")

    # Minimise the shipping cost.
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"total_cost": total_cost}
