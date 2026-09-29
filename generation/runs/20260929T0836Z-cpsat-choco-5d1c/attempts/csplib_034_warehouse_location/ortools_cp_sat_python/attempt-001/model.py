# Warehouse location: decide which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity and the maintenance cost of the open warehouses plus the supply
# costs of all stores is minimal.
from ortools.sat.python import cp_model


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse
    capacity = instance["capacity"]  # most stores each warehouse can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    model = cp_model.CpModel()

    # serves[s][w] is true when warehouse w supplies store s
    serves = [[model.new_bool_var(f"serves_{s}_{w}") for w in range(n_suppliers)] for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [model.new_bool_var(f"open_{w}") for w in range(n_suppliers)]
    # supplier_assignment[s] = the warehouse that supplies store s
    supplier_assignment = [model.new_int_var(0, n_suppliers - 1, f"supplier_{s}") for s in range(n_stores)]

    for s in range(n_stores):
        # every store is supplied by exactly one warehouse
        model.add_exactly_one(serves[s])
        # tie the chosen warehouse number to the Booleans
        model.add(supplier_assignment[s] == sum(w * serves[s][w] for w in range(n_suppliers)))

    for w in range(n_suppliers):
        # a warehouse cannot supply more stores than its capacity
        model.add(sum(serves[s][w] for s in range(n_stores)) <= capacity[w])
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        for s in range(n_stores):
            model.add_implication(serves[s][w], open_warehouses[w])
        model.add(sum(serves[s][w] for s in range(n_stores)) >= 1).only_enforce_if(open_warehouses[w])

    # total cost = maintenance of the open warehouses + supply cost of every store
    max_supply = sum(max(row) for row in cost_matrix)
    total_cost = model.new_int_var(0, n_suppliers * building_cost + max_supply, "total_cost")
    model.add(
        total_cost
        == building_cost * sum(open_warehouses)
        + sum(cost_matrix[s][w] * serves[s][w] for s in range(n_stores) for w in range(n_suppliers))
    )
    model.minimize(total_cost)

    return model, {
        "total_cost": total_cost,
        "open_warehouses": open_warehouses,
        "supplier_assignment": supplier_assignment,
    }
