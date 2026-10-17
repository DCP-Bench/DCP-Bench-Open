# Warehouse location (csplib 034): decide which candidate warehouses to open to supply
# a set of stores. Each store is supplied by exactly one open warehouse, and each
# warehouse supplies at most its capacity of stores. The objective is the total cost:
# the fixed maintenance cost of the opened warehouses plus the supply cost of each store.
import mip


def build(instance):
    n_stores = instance["n_stores"]
    n_sup = instance["n_suppliers"]
    fixed = instance["building_cost"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]

    m = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Which warehouses are open.
    open_w = [m.add_var(f"open_{w}", var_type=mip.BINARY) for w in range(n_sup)]
    # Which warehouse supplies which store.
    x = [
        [m.add_var(f"x_{s}_{w}", var_type=mip.BINARY) for w in range(n_sup)]
        for s in range(n_stores)
    ]

    # Each store must be supplied by exactly one open warehouse.
    for s in range(n_stores):
        m += mip.xsum(x[s][w] for w in range(n_sup)) == 1
        for w in range(n_sup):
            m += x[s][w] <= open_w[w]

    # A warehouse can supply at most its capacity of stores, and none when it is closed.
    for w in range(n_sup):
        m += mip.xsum(x[s][w] for s in range(n_stores)) <= capacity[w] * open_w[w]

    # The warehouse assigned to each store, as an integer output tied to the assignment.
    assign = []
    for s in range(n_stores):
        a = m.add_var(f"supplier_{s}", lb=0, ub=n_sup - 1, var_type=mip.INTEGER)
        m += a == mip.xsum(w * x[s][w] for w in range(n_sup))
        assign.append(a)

    # The total cost is the sum of the maintenance costs for opened warehouses and the
    # supply costs for all stores.
    lo = min(0, fixed) * n_sup + sum(min(row) for row in cost)
    hi = max(0, fixed) * n_sup + sum(max(row) for row in cost)
    total = m.add_var("total_cost", lb=lo, ub=hi, var_type=mip.INTEGER)
    m += total == fixed * mip.xsum(open_w) + mip.xsum(
        cost[s][w] * x[s][w] for s in range(n_stores) for w in range(n_sup)
    )
    m.objective = total

    outputs = {
        "open_warehouses": open_w,
        "supplier_assignment": assign,
        "total_cost": total,
    }
    return m, outputs
