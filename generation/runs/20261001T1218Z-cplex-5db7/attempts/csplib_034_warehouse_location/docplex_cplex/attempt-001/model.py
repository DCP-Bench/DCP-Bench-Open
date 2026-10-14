"""Warehouse location: assign every store to one warehouse within the warehouses' capacities,
paying the supply cost of each assignment plus a building cost for every warehouse that
supplies at least one store, at the least total cost.

The model reports the total cost, which warehouses are open, and the warehouse of each store.
"""
from docplex.mp.model import Model


def build(instance):
    n_suppliers = instance["n_suppliers"]      # number of warehouses
    n_stores = instance["n_stores"]            # number of stores
    building_cost = instance["building_cost"]  # cost of each open warehouse
    capacity = instance["capacity"]            # capacity[w]: stores warehouse w can supply
    cost = instance["cost_matrix"]             # cost[s][w]: cost of warehouse w supplying store s

    warehouses = range(n_suppliers)
    stores = range(n_stores)

    model = Model("warehouse_location")

    # supplies[s, w] is 1 when warehouse w supplies store s; each store has exactly one.
    supplies = {(s, w): model.binary_var(name=f"supplies_{s}_{w}") for s in stores for w in warehouses}
    for s in stores:
        model.add_constraint(model.sum(supplies[s, w] for w in warehouses) == 1)

    # supplier_assignment[s] = w: which warehouse supplies store s.
    supplier_assignment = [model.sum(w * supplies[s, w] for w in warehouses) for s in stores]

    # open_warehouses[w] is 1 if warehouse w is open.
    open_warehouses = [model.binary_var(name=f"open_{w}") for w in warehouses]

    for w in warehouses:
        served = model.sum(supplies[s, w] for s in stores)
        # The number of stores assigned to a warehouse cannot exceed its capacity.
        model.add_constraint(served <= capacity[w])
        # A warehouse is open if and only if it supplies at least one store: open when any
        # store is assigned to it, closed when none is.
        for s in stores:
            model.add_constraint(open_warehouses[w] >= supplies[s, w])
        model.add_constraint(open_warehouses[w] <= served)

    # Total cost: supply costs plus the building cost of every open warehouse.
    total_cost = (model.sum(cost[s][w] * supplies[s, w] for s in stores for w in warehouses)
                  + building_cost * model.sum(open_warehouses))

    # Objective: the least total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouses": open_warehouses,
                   "supplier_assignment": supplier_assignment}
