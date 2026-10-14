# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
from exact import Exact


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    solver = Exact()
    # open_warehouse[i] is 1 when warehouse i is open
    open_warehouse = [f"open_{i}" for i in range(n_warehouses)]
    # ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    ships = [[f"ships_{i}_{j}" for j in range(n_regions)] for i in range(n_warehouses)]
    for i in range(n_warehouses):
        solver.addVariable(open_warehouse[i], 0, 1)
        for name in ships[i]:
            solver.addVariable(name, 0, max_shipping)

    # a warehouse sends at most max_shipping units, and nothing when it is closed
    for i in range(n_warehouses):
        solver.addConstraint([(1, name) for name in ships[i]] + [(-max_shipping, open_warehouse[i])],
                             False, 0, True, 0)

    # every region receives at least its demand
    for j in range(n_regions):
        solver.addConstraint([(1, ships[i][j]) for i in range(n_warehouses)], True, demands[j])

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    solver.addConstraint([(1, open_warehouse[los_angeles]), (-1, open_warehouse[new_york])], True, 0)
    # 2. at most three warehouses are open
    solver.addConstraint([(1, name) for name in open_warehouse], False, 0, True, 3)
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    solver.addConstraint([(1, open_warehouse[atlanta]), (1, open_warehouse[los_angeles])], True, 1)

    # total cost = fixed costs of the open warehouses + cost of everything shipped
    terms = [(fixed_costs[i], open_warehouse[i]) for i in range(n_warehouses)]
    terms += [(shipping_costs[i][j], ships[i][j]) for i in range(n_warehouses) for j in range(n_regions)]
    solver.addVariable("total_cost", 0, 10000)
    solver.addConstraint(terms + [(-1, "total_cost")], True, 0, True, 0)

    return (solver, {"total_cost": "total_cost", "open_warehouse": open_warehouse, "ships": ships},
            ("minimize", terms))
