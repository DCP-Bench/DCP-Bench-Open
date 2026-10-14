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

    # supplier_assignment[s] = the warehouse that supplies store s
    supplier_assignment = [model.intvar(0, n_suppliers - 1, name=f"supplier_{s}") for s in range(n_stores)]
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [model.boolvar(name=f"open_{w}") for w in range(n_suppliers)]

    for w in range(n_suppliers):
        # supplied[w] = number of stores warehouse w supplies, which cannot exceed its capacity
        supplied = model.intvar(0, min(capacity[w], n_stores), name=f"supplied_{w}")
        model.count(w, supplier_assignment, supplied).post()
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        model.arithm(supplied, ">", 0).reify_with(open_warehouses[w])

    # supply cost of each store, looked up in its row of the cost matrix by the chosen warehouse
    supply_costs = []
    for s in range(n_stores):
        cost = model.intvar(min(cost_matrix[s]), max(cost_matrix[s]), name=f"supply_cost_{s}")
        model.element(cost, cost_matrix[s], supplier_assignment[s]).post()
        supply_costs.append(cost)

    # total cost = supply costs + maintenance of the open warehouses (Choco minimises one variable)
    total_cost = model.intvar(0, sum(max(row) for row in cost_matrix) + n_suppliers * building_cost, name="total_cost")
    model.scalar(supply_costs + open_warehouses, [1] * n_stores + [building_cost] * n_suppliers, "=", total_cost).post()

    return (
        model,
        {"total_cost": total_cost, "open_warehouses": open_warehouses, "supplier_assignment": supplier_assignment},
        ("minimize", total_cost),
    )
