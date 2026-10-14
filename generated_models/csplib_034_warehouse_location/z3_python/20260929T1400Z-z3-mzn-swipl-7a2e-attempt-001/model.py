# Warehouse location: decide which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity and the maintenance cost of the open warehouses plus the supply
# costs of all stores is minimal.
import z3


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse
    capacity = instance["capacity"]  # most stores each warehouse can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    solver = z3.Solver()

    # supplier_assignment[s] = the warehouse that supplies store s
    supplier_assignment = [z3.Int(f"supplier_{s}") for s in range(n_stores)]
    for s in range(n_stores):
        solver.add(supplier_assignment[s] >= 0, supplier_assignment[s] < n_suppliers)
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = [z3.Bool(f"open_{w}") for w in range(n_suppliers)]

    for w in range(n_suppliers):
        supplied = [supplier_assignment[s] == w for s in range(n_stores)]
        # a warehouse cannot supply more stores than its capacity
        solver.add(z3.AtMost(*supplied, capacity[w]))
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        solver.add(open_warehouses[w] == z3.Or(supplied))

    # supply cost of each store: the entry of its row picked by the warehouse it uses
    # (Z3 has no element constraint, so it is an If chain over the warehouses)
    supply = z3.Sum([z3.If(supplier_assignment[s] == w, cost_matrix[s][w], 0)
                     for s in range(n_stores) for w in range(n_suppliers)])
    # total cost = supply costs + maintenance of the open warehouses
    total_cost = z3.Int("total_cost")
    solver.add(total_cost == supply + building_cost * z3.Sum([z3.If(o, 1, 0) for o in open_warehouses]))

    return (
        solver,
        {"total_cost": total_cost, "open_warehouses": open_warehouses, "supplier_assignment": supplier_assignment},
        ("minimize", total_cost),
    )
