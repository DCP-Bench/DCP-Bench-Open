# Facility location: choose which warehouses to open and how many units each
# open warehouse ships to each region, minimising fixed plus shipping costs.
import cvc5.pythonic as cz


def build(instance):
    cities = instance["warehouse_s"]
    fixed = instance["fixed_costs"]
    cap = instance["max_shipping"]
    demands = instance["demands"]
    cost = instance["shipping_costs"]

    n_w = len(cities)
    n_r = len(demands)
    idx = {name: i for i, name in enumerate(cities)}
    ny, la, atl = idx["New York"], idx["Los Angeles"], idx["Atlanta"]

    open_w = [cz.Bool(f"open_{i}") for i in range(n_w)]
    ships = [[cz.Int(f"ships_{i}_{j}") for j in range(n_r)] for i in range(n_w)]

    constraints = []

    # Units shipped are not negative, and no warehouse ships more than its capacity.
    for i in range(n_w):
        for j in range(n_r):
            constraints.append(ships[i][j] >= 0)
    for i in range(n_w):
        constraints.append(
            cz.Sum([ships[i][j] for j in range(n_r)]) <= cz.If(open_w[i], cap, 0)
        )

    # Each region's demand is met exactly by the warehouses.
    # A closed warehouse ships nothing, which the capacity row above already enforces.
    for j in range(n_r):
        constraints.append(cz.Sum([ships[i][j] for i in range(n_w)]) == demands[j])

    # If the New York warehouse is opened, then the Los Angeles warehouse must also be opened.
    constraints.append(cz.Implies(open_w[ny], open_w[la]))

    # No more than three warehouses can be operational in any given week.
    constraints.append(
        cz.Sum([cz.If(open_w[i], 1, 0) for i in range(n_w)]) <= 3
    )

    # Either the Atlanta or the Los Angeles warehouse must be opened.
    constraints.append(cz.Or(open_w[atl], open_w[la]))

    total = cz.Sum(
        [cz.If(open_w[i], fixed[i], 0) for i in range(n_w)]
        + [cost[i][j] * ships[i][j] for i in range(n_w) for j in range(n_r)]
    )

    outputs = {
        "open_warehouse": open_w,
        "ships": ships,
        "total_cost": total,
    }
    return constraints, outputs, ("minimize", total)
