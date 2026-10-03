"""Warehouse location: decide which warehouses to open and which open warehouse supplies
each store. A warehouse has a capacity (the number of stores it can supply), every store
is supplied by exactly one warehouse, and the total cost is the building cost of every
open warehouse plus the supply cost of every store from its warehouse; it is to be minimal.

The model reports the total cost, which warehouses are open, and the warehouse that
supplies each store.
"""
import pulp


def build(instance):
    n_warehouses = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # cost of opening any one warehouse
    capacity = instance["capacity"]  # capacity[w] = stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    problem = pulp.LpProblem("warehouse_location", pulp.LpMinimize)

    # supplies[s][w] = 1 if warehouse w supplies store s
    supplies = [[pulp.LpVariable(f"supplies_{s}_{w}", cat="Binary") for w in range(n_warehouses)]
                for s in range(n_stores)]
    # open_warehouses[w] = 1 if warehouse w is open
    open_warehouses = [pulp.LpVariable(f"open_{w}", cat="Binary") for w in range(n_warehouses)]

    # supplier_assignment[s] = the warehouse supplying store s
    supplier_assignment = [pulp.LpVariable(f"supplier_{s}", 0, n_warehouses - 1, cat="Integer")
                           for s in range(n_stores)]
    for s in range(n_stores):
        # each store is supplied by exactly one warehouse
        problem += pulp.lpSum(supplies[s]) == 1
        problem += supplier_assignment[s] == pulp.lpSum(
            w * supplies[s][w] for w in range(n_warehouses))

    for w in range(n_warehouses):
        used = pulp.lpSum(supplies[s][w] for s in range(n_stores))
        # a warehouse supplies at most `capacity[w]` stores
        problem += used <= capacity[w]
        # a warehouse is open if and only if it supplies at least one store: a store is
        # supplied only by an open warehouse, and an open warehouse supplies a store
        for s in range(n_stores):
            problem += supplies[s][w] <= open_warehouses[w]
        problem += open_warehouses[w] <= used

    # total cost = building cost of the open warehouses + supply cost of every store.
    # The largest possible value bounds the variable: every warehouse open, every store
    # at its dearest warehouse.
    upper = building_cost * n_warehouses + sum(max(row) for row in cost_matrix)
    total_cost = pulp.LpVariable("total_cost", 0, upper, cat="Integer")
    problem += total_cost == (
        building_cost * pulp.lpSum(open_warehouses)
        + pulp.lpSum(cost_matrix[s][w] * supplies[s][w]
                     for s in range(n_stores) for w in range(n_warehouses)))

    # objective: minimise the total cost
    problem += total_cost

    return problem, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                     "supplier_assignment": supplier_assignment}
