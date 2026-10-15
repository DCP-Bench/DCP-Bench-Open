# Warehouse location: choose which candidate warehouses to open and assign each
# store to exactly one open warehouse, within warehouse capacity, minimising the
# maintenance cost of opened warehouses plus the supply cost of all stores.
from pyscipopt import Model, quicksum


def build(instance):
    n_warehouses = instance["n_suppliers"]
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]  # cost[store][warehouse]

    m = Model("warehouse_location")
    m.hideOutput()

    # open[w] = 1 if warehouse w is open
    open_wh = [m.addVar(name=f"open_{w}", vtype="B") for w in range(n_warehouses)]
    # assign[s, w] = 1 if store s is supplied by warehouse w
    assign = {
        (s, w): m.addVar(name=f"assign_{s}_{w}", vtype="B")
        for s in range(n_stores)
        for w in range(n_warehouses)
    }

    # each store must be supplied by exactly one warehouse
    for s in range(n_stores):
        m.addCons(quicksum(assign[s, w] for w in range(n_warehouses)) == 1)

    # a store can only be supplied by an open warehouse
    for s in range(n_stores):
        for w in range(n_warehouses):
            m.addCons(assign[s, w] <= open_wh[w])

    # the stores supplied by a warehouse must not exceed its capacity
    for w in range(n_warehouses):
        m.addCons(
            quicksum(assign[s, w] for s in range(n_stores)) <= capacity[w] * open_wh[w]
        )

    # minimise maintenance cost of open warehouses plus supply cost of all stores
    total_cost = quicksum(building_cost * open_wh[w] for w in range(n_warehouses)) + quicksum(
        cost[s][w] * assign[s, w]
        for s in range(n_stores)
        for w in range(n_warehouses)
    )
    m.setObjective(total_cost, "minimize")

    # the warehouse assigned to each store, numbered from 0
    supplier_assignment = [
        quicksum(w * assign[s, w] for w in range(n_warehouses)) for s in range(n_stores)
    ]

    outputs = {
        "open_warehouses": open_wh,
        "supplier_assignment": supplier_assignment,
        "total_cost": total_cost,
    }
    return m, outputs
