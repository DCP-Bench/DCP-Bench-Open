# Facility location: choose which warehouses to open and how many units each open warehouse
# ships to each region, minimising fixed opening costs plus shipping costs.
from pyscipopt import Model, quicksum


def build(instance):
    warehouses = instance["warehouse_s"]
    fixed_costs = instance["fixed_costs"]
    shipping_costs = instance["shipping_costs"]
    demands = instance["demands"]
    max_shipping = instance["max_shipping"]

    W = range(len(warehouses))
    R = range(len(demands))
    NY, LA, CH, AT = [warehouses.index(c) for c in ("New York", "Los Angeles", "Chicago", "Atlanta")]

    m = Model()

    # open[i] = 1 if the warehouse in city i is opened
    open_w = {i: m.addVar(name=f"open_{i}", vtype="B") for i in W}
    # ships[i, j] = units shipped from warehouse i to region j
    ships = {
        (i, j): m.addVar(name=f"ships_{i}_{j}", vtype="I", lb=0, ub=max_shipping)
        for i in W for j in R
    }

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    m.addCons(open_w[NY] <= open_w[LA])

    # No more than three warehouses can be operational in any given week.
    m.addCons(quicksum(open_w[i] for i in W) <= 3)

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    m.addCons(open_w[AT] + open_w[LA] >= 1)

    # Each region's demand is met exactly by the shipments from all warehouses.
    for j in R:
        m.addCons(quicksum(ships[i, j] for i in W) == demands[j])

    # A warehouse that is not opened ships nothing; an opened one ships at most max_shipping
    # units to each region (max_shipping is the per-route capacity in the instance data).
    for i in W:
        for j in R:
            m.addCons(ships[i, j] <= max_shipping * open_w[i])

    # Objective: fixed opening costs plus shipping costs.
    m.setObjective(
        quicksum(fixed_costs[i] * open_w[i] for i in W)
        + quicksum(shipping_costs[i][j] * ships[i, j] for i in W for j in R),
        "minimize",
    )

    outputs = {
        "total_cost": m.getObjective(),
        "open_warehouse": [open_w[i] for i in W],
        "ships": [[ships[i, j] for j in R] for i in W],
    }
    return m, outputs
