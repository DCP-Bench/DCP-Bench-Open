# Facility location: choose which warehouses to open and how many units each open
# warehouse ships to each region, minimising fixed plus shipping costs.
from paramita.modelling import Bool, If, Or


def build(instance):
    cities = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cost = instance["shipping_costs"]
    demands = instance["demands"]
    cap = instance["max_shipping"]
    n_w, n_r = len(cities), len(demands)
    ny, la, atl = cities.index("New York"), cities.index("Los Angeles"), cities.index("Atlanta")

    # open[i] = 1 if the warehouse in city i is opened
    open_ = [Bool(f"open_{i}") for i in range(n_w)]

    # Shipments are binary numbers. A shipment from warehouse i to region j is at most
    # min(max_shipping, demand_j), so that many bits cover it (data-derived bound).
    # Binary keeps the number of Bools and the objective literals small.
    ub = [min(cap, demands[j]) for j in range(n_r)]
    bits = [[[Bool(f"ship_{i}_{j}_b{k}") for k in range(max(1, ub[j].bit_length()))]
             for j in range(n_r)] for i in range(n_w)]
    ships = [[sum((1 << k) * b for k, b in enumerate(bits[i][j])) for j in range(n_r)]
             for i in range(n_w)]

    cons = []

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    cons.append(If(open_[ny], open_[la]))

    # No more than three warehouses can be operational.
    cons.append(sum(open_) <= 3)

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    cons.append(Or([open_[atl], open_[la]]))

    # Every region's demand is met by the shipments from all warehouses together,
    # and one shipment never exceeds min(max_shipping, demand).
    for j in range(n_r):
        cons.append(sum(ships[i][j] for i in range(n_w)) == demands[j])
        for i in range(n_w):
            cons.append(ships[i][j] <= ub[j])

    # An open warehouse ships at most max_shipping units in total; a closed one ships nothing.
    for i in range(n_w):
        cons.append(sum(ships[i][j] for j in range(n_r)) <= cap * open_[i])

    # Redundant: a closed warehouse ships nothing to any single region (lets the solver
    # propagate the closure per cell).
    for i in range(n_w):
        for j in range(n_r):
            cons.append(ships[i][j] <= ub[j] * open_[i])

    # Redundant: the open warehouses together can carry the total demand.
    cons.append(sum(cap * open_[i] for i in range(n_w)) >= sum(demands))

    # Total cost: fixed costs of the opened warehouses plus the shipping costs.
    # Every region receives exactly its demand, so cost[i][j] can be replaced by
    # cost[i][j] - cheapest[j] plus the constant demand_j * cheapest[j]. The cheapest
    # warehouse of a region then adds no objective weight and the other weights are smaller.
    cheapest = [min(cost[i][j] for i in range(n_w)) for j in range(n_r)]
    base = sum(demands[j] * cheapest[j] for j in range(n_r))
    extra = sum((cost[i][j] - cheapest[j]) * ships[i][j] for i in range(n_w) for j in range(n_r))
    total = sum(fixed[i] * open_[i] for i in range(n_w)) + extra + base
    # objective without the constant, for the solver
    objective = sum(fixed[i] * open_[i] for i in range(n_w)) + extra

    outputs = {
        "open_warehouse": open_,
        "ships": ships,
        "total_cost": total,
    }
    return cons, outputs, ("minimize", objective)
