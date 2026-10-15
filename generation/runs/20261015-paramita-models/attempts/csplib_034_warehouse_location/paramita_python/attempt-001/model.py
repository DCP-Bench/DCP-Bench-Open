"""Warehouse location: decide which warehouses to open and supply every store from one of them.

Encoding: open_w[j] is a Bool per candidate warehouse; assign[i][j] is a one-hot Bool per store
(exactly one warehouse per store). Sizes, capacities, costs come from the instance.
"""
from paramita.modelling import Bool, If


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]  # stores to supply
    building_cost = instance["building_cost"]  # fixed maintenance cost of each opened warehouse
    capacity = instance["capacity"]  # number of stores each warehouse can supply
    cost = instance["cost_matrix"]  # cost[store][warehouse]: supply cost of the store from the warehouse

    # a warehouse is open, or not
    open_w = [Bool(f"open_{j}") for j in range(n_suppliers)]
    # store i is supplied by warehouse j
    assign = [[Bool(f"assign_{i}_{j}") for j in range(n_suppliers)] for i in range(n_stores)]

    cons = []

    # each store must be supplied by exactly one open warehouse
    for i in range(n_stores):
        cons.append(sum(assign[i][j] for j in range(n_suppliers)) == 1)

    # a store can only be supplied by a warehouse that is open
    for i in range(n_stores):
        for j in range(n_suppliers):
            cons.append(If(assign[i][j], open_w[j]))

    # a warehouse has a capacity limiting the number of stores it can supply
    for j in range(n_suppliers):
        cons.append(sum(assign[i][j] for i in range(n_stores)) <= capacity[j])

    # the total cost is the sum of the maintenance costs of the opened warehouses
    # and the supply costs of all stores
    maintenance = sum(building_cost * open_w[j] for j in range(n_suppliers))
    supply = sum(cost[i][j] * assign[i][j] for i in range(n_stores) for j in range(n_suppliers))
    total_cost = maintenance + supply

    # the warehouse (0-based) assigned to each store
    supplier_assignment = [sum(j * assign[i][j] for j in range(n_suppliers)) for i in range(n_stores)]

    return cons, {
        "open_warehouses": open_w,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }, ("minimize", total_cost)
