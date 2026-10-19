# Warehouse location (csplib 034): choose which warehouses to open to supply
# every store, respecting each warehouse's capacity, minimising the total cost
# of maintenance for open warehouses plus the supply cost of every store.
# Encoded as a 0/1 linear model: x[t][w] = 1 when store t is supplied by warehouse w,
# o[w] = 1 when warehouse w is open. No if-then-else terms, so the solver sees linear rows.
import cvc5.pythonic as cz


def build(instance):
    n_sup = instance["n_suppliers"]
    n_sto = instance["n_stores"]
    building_cost = instance["building_cost"]
    capacity = instance["capacity"]
    cost = instance["cost_matrix"]

    o = [cz.Int(f"open_{w}") for w in range(n_sup)]
    x = [[cz.Int(f"x_{t}_{w}") for w in range(n_sup)] for t in range(n_sto)]
    assign = [cz.Int(f"assign_{t}") for t in range(n_sto)]
    total = cz.Int("total_cost")

    constraints = []

    # Each warehouse is either open (1) or closed (0).
    for w in range(n_sup):
        constraints.append(o[w] >= 0)
        constraints.append(o[w] <= 1)

    # Each store must be supplied by exactly one open warehouse.
    for t in range(n_sto):
        for w in range(n_sup):
            constraints.append(x[t][w] >= 0)
            constraints.append(x[t][w] <= 1)
            # A store can only be supplied by a warehouse that is open.
            constraints.append(x[t][w] <= o[w])
        constraints.append(cz.Sum(x[t]) == 1)
        # The warehouse index assigned to the store, in the range 0 to n_suppliers-1.
        constraints.append(
            assign[t] == cz.Sum([w * x[t][w] for w in range(n_sup)])
        )

    # The number of stores a warehouse supplies cannot exceed its capacity.
    for w in range(n_sup):
        constraints.append(
            cz.Sum([x[t][w] for t in range(n_sto)]) <= capacity[w]
        )

    # The total cost is the sum of the maintenance costs for all opened
    # warehouses and the supply costs for all stores.
    constraints.append(
        total
        == building_cost * cz.Sum(o)
        + cz.Sum([cost[t][w] * x[t][w] for t in range(n_sto) for w in range(n_sup)])
    )

    outputs = {
        "open_warehouses": [o[w] == 1 for w in range(n_sup)],
        "supplier_assignment": assign,
        "total_cost": total,
    }
    return constraints, outputs, ("minimize", total)
