# Warehouse location: decide which candidate warehouses to open and which open
# warehouse supplies each store, so that no warehouse serves more stores than
# its capacity and the maintenance cost of the open warehouses plus the supply
# costs of all stores is minimal.
from hermax.model import Model


def build(instance):
    n_suppliers = instance["n_suppliers"]  # candidate warehouses
    n_stores = instance["n_stores"]
    building_cost = instance["building_cost"]  # maintenance cost of one open warehouse
    capacity = instance["capacity"]  # most stores each warehouse can supply
    cost_matrix = instance["cost_matrix"]  # cost_matrix[store][warehouse] = supply cost

    m = Model()
    # supplier_assignment[s] = the warehouse that supplies store s
    supplier_assignment = m.int_vector("supplier_assignment", n_stores, 0, n_suppliers - 1)
    # open_warehouses[w] is true when warehouse w is open
    open_warehouses = m.bool_vector("open_warehouses", n_suppliers)

    for w in range(n_suppliers):
        supplies = [supplier_assignment[s] == w for s in range(n_stores)]
        # a warehouse cannot supply more stores than its capacity
        m &= (sum(1 * lit for lit in supplies) <= capacity[w])
        # a warehouse is open exactly when it supplies at least one store; this
        # also forbids supplying a store from a closed warehouse
        for lit in supplies:
            m &= lit.implies(open_warehouses[w])
        clause = ~open_warehouses[w]
        for lit in supplies:
            clause = clause | lit
        m &= clause

    # supply cost of each store: the entry of its row picked by the warehouse it uses
    supply_cost = []
    for s in range(n_stores):
        cost = m.int(f"supply_cost_{s}", min(cost_matrix[s]), max(cost_matrix[s]))
        for w in range(n_suppliers):
            m &= (~(supplier_assignment[s] == w) | (cost == cost_matrix[s][w]))
        supply_cost.append(cost)

    # Minimise the total cost: each unit of a store's supply cost above its cheapest entry
    # pays one exactly when supply_cost >= k holds, and every open warehouse pays its
    # maintenance cost. (The cheapest entries are a constant and do not change the optimum.)
    for s in range(n_stores):
        for k in range(min(cost_matrix[s]) + 1, max(cost_matrix[s]) + 1):
            m.obj[1] += ~(supply_cost[s] >= k)
    if building_cost > 0:
        for w in range(n_suppliers):
            m.obj[building_cost] += ~open_warehouses[w]

    # total_cost is a declared output: supply costs plus the maintenance of the open warehouses
    # (a warehouse costs nothing to maintain when building_cost is 0)
    open_count = []
    for w in range(n_suppliers):
        if building_cost > 0:
            flag = m.int(f"open_flag_{w}", 0, 1)
            m &= (~open_warehouses[w] | (flag == 1))
            m &= (open_warehouses[w] | (flag == 0))
            open_count.append(m.scale(flag, building_cost))
    total_cost = m.sum_var(supply_cost + open_count)

    return m, {"total_cost": total_cost, "open_warehouses": open_warehouses,
               "supplier_assignment": supplier_assignment}
