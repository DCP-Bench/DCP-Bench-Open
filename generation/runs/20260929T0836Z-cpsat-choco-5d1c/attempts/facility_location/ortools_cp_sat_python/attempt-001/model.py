# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
from ortools.sat.python import cp_model


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    model = cp_model.CpModel()

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [model.new_bool_var(f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    ships = [[model.new_int_var(0, max_shipping, f"ships_{i}_{j}") for j in range(n_regions)]
             for i in range(n_warehouses)]

    # a warehouse sends at most max_shipping units, and nothing when it is closed
    for i in range(n_warehouses):
        model.add(sum(ships[i]) <= max_shipping * open_warehouse[i])

    # every region receives at least its demand
    for j in range(n_regions):
        model.add(sum(ships[i][j] for i in range(n_warehouses)) >= demands[j])

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    model.add_implication(open_warehouse[new_york], open_warehouse[los_angeles])
    # 2. at most three warehouses are open
    model.add(sum(open_warehouse) <= 3)
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    model.add_bool_or([open_warehouse[atlanta], open_warehouse[los_angeles]])

    # total cost = fixed costs of the open warehouses + cost of everything shipped
    total_cost = model.new_int_var(0, 10000, "total_cost")
    model.add(
        total_cost
        == sum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
        + sum(shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions))
    )
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
