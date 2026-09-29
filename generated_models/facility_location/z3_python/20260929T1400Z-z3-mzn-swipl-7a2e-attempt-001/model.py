# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
import z3


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    solver = z3.Solver()

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [z3.Bool(f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    ships = [[z3.Int(f"ships_{i}_{j}") for j in range(n_regions)] for i in range(n_warehouses)]
    for i in range(n_warehouses):
        for j in range(n_regions):
            solver.add(ships[i][j] >= 0, ships[i][j] <= max_shipping)

    # a warehouse sends at most max_shipping units, and nothing when it is closed
    for i in range(n_warehouses):
        solver.add(z3.Sum(ships[i]) <= z3.If(open_warehouse[i], max_shipping, 0))

    # every region receives at least its demand
    for j in range(n_regions):
        solver.add(z3.Sum([ships[i][j] for i in range(n_warehouses)]) >= demands[j])

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    solver.add(z3.Implies(open_warehouse[new_york], open_warehouse[los_angeles]))
    # 2. at most three warehouses are open
    solver.add(z3.AtMost(*open_warehouse, 3))
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    solver.add(z3.Or(open_warehouse[atlanta], open_warehouse[los_angeles]))

    # total cost = fixed costs of the open warehouses + cost of everything shipped
    total_cost = z3.Int("total_cost")
    solver.add(total_cost >= 0, total_cost <= 10000)
    solver.add(
        total_cost
        == z3.Sum([z3.If(open_warehouse[i], fixed_costs[i], 0) for i in range(n_warehouses)])
        + z3.Sum([shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions)])
    )

    return (
        solver,
        {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships},
        ("minimize", total_cost),
    )
