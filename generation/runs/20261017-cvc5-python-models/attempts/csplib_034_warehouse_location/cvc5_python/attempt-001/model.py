# Warehouse location (csplib 034): choose which warehouses to open to supply
# every store, respecting each warehouse's capacity, minimising the total cost
# of maintenance for open warehouses plus the supply cost of every store.
import cvc5.pythonic as cz


def build(instance):
    n_sup = instance["n_suppliers"]
    n_sto = instance["n_stores"]
    building_cost = instance["building_cost"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]

    open_w = cz.Bools(" ".join(f"open_{w}" for w in range(n_sup)))
    assign = cz.Ints(" ".join(f"assign_{t}" for t in range(n_sto)))
    total = cz.Int("total_cost")

    constraints = []

    # Each store must be supplied by exactly one open warehouse, the
    # warehouse index being in the range 0 to n_suppliers-1.
    for t in range(n_sto):
        constraints.append(assign[t] >= 0)
        constraints.append(assign[t] <= n_sup - 1)
        for w in range(n_sup):
            constraints.append(cz.Implies(assign[t] == w, open_w[w]))

    # The number of stores a warehouse supplies cannot exceed its capacity.
    for w in range(n_sup):
        constraints.append(
            cz.Sum([cz.If(assign[t] == w, 1, 0) for t in range(n_sto)]) <= capacity[w]
        )

    # The total cost is the sum of the maintenance costs for all opened
    # warehouses and the supply costs for all stores.
    maintenance = cz.Sum([cz.If(open_w[w], building_cost, 0) for w in range(n_sup)])
    supply = cz.Sum(
        [
            cz.Sum([cz.If(assign[t] == w, cost[t][w], 0) for w in range(n_sup)])
            for t in range(n_sto)
        ]
    )
    constraints.append(total == maintenance + supply)

    outputs = {
        "open_warehouses": open_w,
        "supplier_assignment": assign,
        "total_cost": total,
    }
    return constraints, outputs, ("minimize", total)
