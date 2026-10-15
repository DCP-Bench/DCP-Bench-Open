# Multi-commodity transportation: ship every product from the origins to the destinations at minimum total cost.
from pyscipopt import Model, quicksum


def build(instance):
    supply = instance["supply"]    # supply[i][p]: units of product p available at origin i
    demand = instance["demand"]    # demand[j][p]: units of product p required at destination j
    limit = instance["limit"]      # limit[i][j]: total units (all products) on the lane from i to j
    cost = instance["cost"]        # cost[i][j][p]: cost of shipping one unit of p from i to j
    n_orig = len(supply)
    n_dest = len(demand)
    n_prod = len(supply[0])

    m = Model()

    # ship[i, j, p] = units of product p shipped from origin i to destination j
    ship = {}
    for i in range(n_orig):
        for j in range(n_dest):
            for p in range(n_prod):
                ub = min(supply[i][p], demand[j][p], limit[i][j])
                ship[i, j, p] = m.addVar(name=f"ship_{i}_{j}_{p}", vtype="I", lb=0, ub=ub)

    # the units of each product shipped out of an origin cannot exceed its supply of that product
    for i in range(n_orig):
        for p in range(n_prod):
            m.addCons(quicksum(ship[i, j, p] for j in range(n_dest)) <= supply[i][p])

    # the units of each product received at a destination must equal its demand for that product
    for j in range(n_dest):
        for p in range(n_prod):
            m.addCons(quicksum(ship[i, j, p] for i in range(n_orig)) == demand[j][p])

    # the total of all products on a lane cannot exceed the lane limit
    for i in range(n_orig):
        for j in range(n_dest):
            m.addCons(quicksum(ship[i, j, p] for p in range(n_prod)) <= limit[i][j])

    # the objective is the total shipping cost of all units
    total_cost = quicksum(cost[i][j][p] * ship[i, j, p]
                          for i in range(n_orig) for j in range(n_dest) for p in range(n_prod))
    m.setObjective(total_cost, "minimize")

    return m, {"total_cost": total_cost}
