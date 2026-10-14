# Warehouse location: decide which warehouses to open and which open warehouse supplies
# each store, within warehouse capacities, minimising maintenance plus supply cost.
import cpmpy as cp


def build(instance):
    n_warehouses = instance["n_suppliers"]     # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of each open warehouse
    capacity = instance["capacity"]            # capacity[w]: most stores warehouse w can supply
    cost_matrix = instance["cost_matrix"]      # cost_matrix[s][w]: cost of supplying store s from warehouse w

    # supplier_assignment[s] is the warehouse that supplies store s.
    supplier_assignment = cp.intvar(0, n_warehouses - 1, shape=n_stores, name="supplier_assignment")
    # open_warehouses[w] is true when warehouse w is open.
    open_warehouses = cp.boolvar(shape=n_warehouses, name="open_warehouses")

    model = cp.Model()

    # A warehouse cannot supply more stores than its capacity.
    for w in range(n_warehouses):
        model += cp.Count(supplier_assignment, w) <= capacity[w]

    # A warehouse is open exactly when it supplies at least one store; this also makes
    # sure no store is supplied from a closed warehouse.
    for w in range(n_warehouses):
        model += open_warehouses[w] == (cp.Count(supplier_assignment, w) > 0)

    # Total cost: the supply cost of every store from its warehouse plus the maintenance
    # cost of every open warehouse. The matrix is wrapped so it can be indexed by a variable.
    costs = cp.cpm_array(cost_matrix)
    supply_cost = cp.sum([costs[s, supplier_assignment[s]] for s in range(n_stores)])
    maintenance_cost = cp.sum(open_warehouses) * building_cost
    total_cost = supply_cost + maintenance_cost

    model.minimize(total_cost)

    return model, {"open_warehouses": open_warehouses,
                   "supplier_assignment": supplier_assignment,
                   "total_cost": total_cost}
