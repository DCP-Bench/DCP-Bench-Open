# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
from pychoco.model import Model


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    model = Model()

    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = [model.boolvar(name=f"open_{i}") for i in range(n_warehouses)]
    # ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    ships = [[model.intvar(0, max_shipping, name=f"ships_{i}_{j}") for j in range(n_regions)]
             for i in range(n_warehouses)]

    # a warehouse sends at most max_shipping units, and nothing when it is closed
    for i in range(n_warehouses):
        model.scalar(ships[i] + [open_warehouse[i]], [1] * n_regions + [-max_shipping], "<=", 0).post()

    # every region receives at least its demand
    for j in range(n_regions):
        model.sum([ships[i][j] for i in range(n_warehouses)], ">=", demands[j]).post()

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    model.arithm(open_warehouse[new_york], "<=", open_warehouse[los_angeles]).post()
    # 2. at most three warehouses are open
    model.sum(open_warehouse, "<=", 3).post()
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    model.arithm(open_warehouse[atlanta], "+", open_warehouse[los_angeles], ">=", 1).post()

    # total cost = fixed costs of the open warehouses + cost of everything shipped
    total_cost = model.intvar(0, 10000, name="total_cost")
    flat_ships = [ships[i][j] for i in range(n_warehouses) for j in range(n_regions)]
    flat_costs = [shipping_costs[i][j] for i in range(n_warehouses) for j in range(n_regions)]
    model.scalar(flat_ships + open_warehouse, flat_costs + fixed_costs, "=", total_cost).post()

    return (
        model,
        {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships},
        ("minimize", total_cost),
    )
