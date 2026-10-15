from pyscipopt import Model, quicksum

# Warehouse location: choose which candidate warehouses to open, and assign every store
# to one open warehouse, so that the maintenance and supply costs are minimal.


def build(instance):
    n_stores = instance["n_stores"]
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    building_cost = instance["building_cost"]  # maintenance cost of an open warehouse
    capacity = instance["capacity"]  # number of stores a warehouse can supply
    cost = instance["cost_matrix"]  # cost[s][w]: supply cost of store s from warehouse w

    m = Model()
    # open[w] = 1 if warehouse w is opened
    open_w = [m.addVar(name=f"open_{w}", vtype="B") for w in range(n_suppliers)]
    # assign[s][w] = 1 if store s is supplied by warehouse w
    assign = [[m.addVar(name=f"assign_{s}_{w}", vtype="B") for w in range(n_suppliers)]
              for s in range(n_stores)]
    total = m.addVar(name="total_cost", vtype="I", lb=0)

    # each store is supplied by exactly one warehouse
    for s in range(n_stores):
        m.addCons(quicksum(assign[s][w] for w in range(n_suppliers)) == 1)
    # a store can only be supplied by a warehouse that is open
    for s in range(n_stores):
        for w in range(n_suppliers):
            m.addCons(assign[s][w] <= open_w[w])
    # a warehouse supplies at most its capacity in stores, and none when closed
    for w in range(n_suppliers):
        m.addCons(quicksum(assign[s][w] for s in range(n_stores)) <= capacity[w] * open_w[w])
    # the total cost is the maintenance cost of the open warehouses plus the supply costs
    m.addCons(total == quicksum(building_cost * open_w[w] for w in range(n_suppliers))
              + quicksum(cost[s][w] * assign[s][w]
                         for s in range(n_stores) for w in range(n_suppliers)))
    m.setObjective(total, "minimize")

    # the assigned warehouse of each store, numbered from 0
    supplier_assignment = [quicksum(w * assign[s][w] for w in range(n_suppliers))
                           for s in range(n_stores)]
    return m, {"open_warehouses": open_w, "supplier_assignment": supplier_assignment,
               "total_cost": total}
