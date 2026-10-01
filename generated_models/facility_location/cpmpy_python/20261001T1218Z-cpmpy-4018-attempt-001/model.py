# Facility location: choose which of four warehouses (New York, Los Angeles, Chicago,
# Atlanta) to open and how many units each ships to each region, meeting every region's
# demand at the least total of fixed and shipping costs, under three opening rules.
import cpmpy as cp


def build(instance):
    names = instance["warehouse_s"]              # warehouse names, in index order
    fixed_costs = instance["fixed_costs"]        # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]      # most units one open warehouse can ship per week
    demands = instance["demands"]                # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # shipping_costs[i][j]: cost per unit from warehouse i to region j
    num_warehouses = len(names)
    num_regions = len(demands)

    # The opening rules below are about named cities; find their indices from the instance.
    new_york = names.index("New York")
    los_angeles = names.index("Los Angeles")
    atlanta = names.index("Atlanta")

    # open_warehouse[i] is true when warehouse i is open.
    open_warehouse = cp.boolvar(shape=num_warehouses, name="open_warehouse")
    # ships[i][j] is the number of units sent from warehouse i to region j.
    ships = cp.intvar(0, max_shipping, shape=(num_warehouses, num_regions), name="ships")
    # Upper bound on the cost: all fixed costs plus the full shipping capacity at every route's price.
    cost_bound = sum(fixed_costs) + max_shipping * sum(sum(row) for row in shipping_costs)
    total_cost = cp.intvar(0, cost_bound, name="total_cost")

    costs = cp.cpm_array(shipping_costs)

    model = cp.Model()

    # A warehouse ships at most max_shipping units per week, and nothing when it is closed.
    for i in range(num_warehouses):
        model += cp.sum(ships[i, :]) <= max_shipping * open_warehouse[i]

    # Every region receives at least its weekly demand.
    for j in range(num_regions):
        model += cp.sum(ships[:, j]) >= demands[j]

    # Total cost: fixed cost of every open warehouse plus the cost of every unit shipped.
    model += total_cost == cp.sum(
        [open_warehouse[i] * fixed_costs[i] + cp.sum([ships[i, j] * costs[i, j] for j in range(num_regions)])
         for i in range(num_warehouses)])

    # Rule 1: if the New York warehouse is opened, the Los Angeles warehouse must be opened too.
    model += open_warehouse[new_york].implies(open_warehouse[los_angeles])

    # Rule 2: at most three warehouses can be open.
    model += cp.sum(open_warehouse) <= 3

    # Rule 3: the Atlanta or the Los Angeles warehouse (or both) must be open.
    model += open_warehouse[atlanta] | open_warehouse[los_angeles]

    # Minimise the total cost.
    model.minimize(total_cost)

    return model, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
