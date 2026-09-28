"""Facility location: open warehouses and ship to regions at the least weekly cost, under three opening rules."""
from docplex.mp.model import Model


def build(instance):
    fixed_costs = instance["fixed_costs"]
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: per unit, warehouse i to region j
    demands = instance["demands"]
    max_shipping = instance["max_shipping"]
    warehouses = range(len(instance["warehouse_s"]))
    regions = range(len(demands))
    # The warehouses are, in order, New York, Los Angeles, Chicago and Atlanta.
    new_york, los_angeles, chicago, atlanta = warehouses

    model = Model("facility_location")

    # open_warehouse[i] is 1 when warehouse i is open; ships[i, j] is the units
    # it sends to region j each week.
    open_warehouse = model.binary_var_list(len(warehouses), name="open_warehouse")
    ships = model.integer_var_matrix(warehouses, regions, 0, max_shipping, name="ships")

    # A warehouse ships at most max_shipping units a week, and nothing when closed.
    for i in warehouses:
        model.add_constraint(model.sum(ships[i, j] for j in regions) <= max_shipping * open_warehouse[i],
                             ctname=f"shipping_{i}")

    # Every region receives at least its weekly demand.
    for j in regions:
        model.add_constraint(model.sum(ships[i, j] for i in warehouses) >= demands[j], ctname=f"demand_{j}")

    # 1. If the New York warehouse is opened, the Los Angeles one is opened too.
    model.add_constraint(open_warehouse[new_york] <= open_warehouse[los_angeles], ctname="new_york_needs_la")
    # 2. At most three warehouses are open.
    model.add_constraint(model.sum(open_warehouse) <= 3, ctname="at_most_three")
    # 3. The Atlanta or the Los Angeles warehouse is open.
    model.add_constraint(open_warehouse[atlanta] + open_warehouse[los_angeles] >= 1, ctname="atlanta_or_la")

    # total_cost is the fixed cost of the open warehouses plus the shipping cost.
    # The reference model gives it the domain 0..10000, which is mirrored here.
    total_cost = model.integer_var(0, 10000, name="total_cost")
    model.add_constraint(total_cost == model.dot(open_warehouse, fixed_costs)
                         + model.sum(shipping_costs[i][j] * ships[i, j] for i in warehouses for j in regions),
                         ctname="cost")

    # Minimise the total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost,
                   "open_warehouse": open_warehouse,
                   "ships": [[ships[i, j] for j in regions] for i in warehouses]}
