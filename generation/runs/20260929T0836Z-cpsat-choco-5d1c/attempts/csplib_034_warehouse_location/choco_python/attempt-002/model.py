# Warehouse location: decide which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity and the maintenance cost of the open warehouses plus the supply
# costs of all stores is minimal.
from pychoco.model import Model


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse
    capacity = instance["capacity"]  # most stores each warehouse can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    model = Model()

    # serves[s][w] is true when warehouse w supplies store s. Choosing with one
    # Boolean per store and warehouse, instead of one warehouse number per store,
    # lets the supply cost be a plain weighted sum that Choco bounds well.
    serves = [[model.boolvar(name=f"serves_{s}_{w}") for w in range(n_suppliers)] for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [model.boolvar(name=f"open_{w}") for w in range(n_suppliers)]
    # supplier_assignment[s] = the warehouse that supplies store s
    supplier_assignment = [model.intvar(0, n_suppliers - 1, name=f"supplier_{s}") for s in range(n_stores)]

    for s in range(n_stores):
        # every store is supplied by exactly one warehouse
        model.sum(serves[s], "=", 1).post()
        # supplier_assignment[s] is the number of that warehouse
        model.scalar(serves[s], list(range(n_suppliers)), "=", supplier_assignment[s]).post()

    for w in range(n_suppliers):
        column = [serves[s][w] for s in range(n_stores)]
        # a warehouse cannot supply more stores than its capacity
        model.sum(column, "<=", capacity[w]).post()
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        model.sum(column, ">", 0).reify_with(open_warehouses[w])

    # total cost = supply costs + maintenance of the open warehouses (Choco minimises one variable)
    total_cost = model.intvar(0, sum(max(row) for row in cost_matrix) + n_suppliers * building_cost, name="total_cost")
    flat = [serves[s][w] for s in range(n_stores) for w in range(n_suppliers)]
    flat_costs = [cost_matrix[s][w] for s in range(n_stores) for w in range(n_suppliers)]
    model.scalar(flat + open_warehouses, flat_costs + [building_cost] * n_suppliers, "=", total_cost).post()

    return (
        model,
        {"total_cost": total_cost, "open_warehouses": open_warehouses, "supplier_assignment": supplier_assignment},
        ("minimize", total_cost),
    )
