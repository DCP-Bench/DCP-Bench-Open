# Facility location: choose which of four warehouses to open and how many units each open warehouse ships to each region, minimising total cost.
from paramita.modelling import Bool, If, Or


def build(instance):
    cities = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cost = instance["shipping_costs"]
    demands = instance["demands"]
    cap = instance["max_shipping"]
    n_w, n_r = len(cities), len(demands)
    ny, la, atl = cities.index("New York"), cities.index("Los Angeles"), cities.index("Atlanta")

    # open[i] = 1 if warehouse i is opened
    open_ = [Bool(f"open_{i}") for i in range(n_w)]

    cons = []

    # Shipped amounts are unary: ge[i][j][k] is true when ships[i][j] is at least k + 1.
    # Shipments are summed in demand and capacity constraints, so unary keeps those as plain counts.
    # A region's shipment from one warehouse cannot exceed the warehouse capacity or the region's demand.
    ships = [[None] * n_r for _ in range(n_w)]
    for i in range(n_w):
        for j in range(n_r):
            ub = min(cap, demands[j])
            ge = [Bool(f"ship_{i}_{j}_ge{k}") for k in range(1, ub + 1)]
            # order chain: an amount of at least k + 1 implies at least k
            for k in range(1, ub):
                cons.append(If(ge[k], ge[k - 1]))
            ships[i][j] = sum(ge)

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    cons.append(If(open_[ny], open_[la]))

    # No more than three warehouses can be operational.
    cons.append(sum(open_) <= 3)

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    cons.append(Or([open_[atl], open_[la]]))

    # Every region's demand is met by the shipments from all warehouses together.
    for j in range(n_r):
        cons.append(sum(ships[i][j] for i in range(n_w)) == demands[j])

    # An open warehouse ships at most max_shipping units in total; a closed one ships nothing.
    for i in range(n_w):
        cons.append(sum(ships[i][j] for j in range(n_r)) <= cap * open_[i])

    # Total cost: fixed costs of the opened warehouses plus the shipping costs.
    fixed_part = sum(fixed[i] * open_[i] for i in range(n_w))
    ship_part = sum(cost[i][j] * ships[i][j] for i in range(n_w) for j in range(n_r))
    total = fixed_part + ship_part

    outputs = {
        "open_warehouse": open_,
        "ships": ships,
        "total_cost": total,
    }
    return cons, outputs, ("minimize", total)
