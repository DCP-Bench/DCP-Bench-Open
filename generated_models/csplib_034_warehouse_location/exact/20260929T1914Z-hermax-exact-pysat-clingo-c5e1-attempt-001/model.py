# Warehouse location: decide which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity and the maintenance cost of the open warehouses plus the supply
# costs of all stores is minimal.
from exact import Exact


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse
    capacity = instance["capacity"]  # most stores each warehouse can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    solver = Exact()
    # supplier_assignment[s] = the warehouse that supplies store s; serves[s][w] is 1
    # exactly when it is warehouse w
    supplier_assignment = [f"supplier_{s}" for s in range(n_stores)]
    serves = [[f"serves_{s}_{w}" for w in range(n_suppliers)] for s in range(n_stores)]
    # open_warehouses[w] is 1 when warehouse w is open
    open_warehouses = [f"open_{w}" for w in range(n_suppliers)]
    for w in range(n_suppliers):
        solver.addVariable(open_warehouses[w], 0, 1)
    for s in range(n_stores):
        solver.addVariable(supplier_assignment[s], 0, n_suppliers - 1)
        for name in serves[s]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in serves[s]], True, 1, True, 1)
        solver.addConstraint([(w, serves[s][w]) for w in range(1, n_suppliers)] + [(-1, supplier_assignment[s])],
                             True, 0, True, 0)

    for w in range(n_suppliers):
        column = [(1, serves[s][w]) for s in range(n_stores)]
        # a warehouse cannot supply more stores than its capacity
        solver.addConstraint(column, False, 0, True, capacity[w])
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        solver.addConstraint(column + [(-n_stores, open_warehouses[w])], False, 0, True, 0)
        solver.addConstraint(column + [(-1, open_warehouses[w])], True, 0)

    # total cost = supply costs + maintenance of the open warehouses
    terms = [(cost_matrix[s][w], serves[s][w]) for s in range(n_stores) for w in range(n_suppliers)]
    terms += [(building_cost, name) for name in open_warehouses]
    solver.addVariable("total_cost", 0, sum(max(row) for row in cost_matrix) + n_suppliers * building_cost)
    solver.addConstraint(terms + [(-1, "total_cost")], True, 0, True, 0)

    return (solver, {"total_cost": "total_cost", "open_warehouses": open_warehouses,
                     "supplier_assignment": supplier_assignment}, ("minimize", terms))
