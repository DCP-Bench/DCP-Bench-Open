# Facility location: choose which warehouses to open (New York, Los Angeles,
# Chicago, Atlanta) and how many units each open warehouse ships to each region,
# so that every regional demand is met at minimal total cost.
import mip


def build(instance):
    warehouse_s = instance["warehouse_s"]
    fixed_costs = instance["fixed_costs"]
    shipping_costs = instance["shipping_costs"]
    demands = instance["demands"]
    max_shipping = instance["max_shipping"]
    n_w = len(fixed_costs)  # number of warehouses
    n_r = len(demands)  # number of regions

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # open_warehouse[i] = 1 if warehouse i is opened
    open_w = [model.add_var(f"open_{i}", var_type=mip.BINARY) for i in range(n_w)]
    # ships[i][j] = units shipped from warehouse i to region j. The upper bound
    # comes from the data: no region needs more than its demand, and no warehouse
    # ships more than max_shipping units.
    ships = [
        [
            model.add_var(
                f"ships_{i}_{j}",
                lb=0,
                ub=min(demands[j], max_shipping),
                var_type=mip.INTEGER,
            )
            for j in range(n_r)
        ]
        for i in range(n_w)
    ]
    # total_cost: the objective, bounded by all fixed costs plus the most
    # expensive unit cost times all demand
    max_unit_cost = max(max(row) for row in shipping_costs)
    total = model.add_var(
        "total_cost",
        lb=0,
        ub=sum(fixed_costs) + max_unit_cost * sum(demands),
        var_type=mip.INTEGER,
    )

    # the shipments to each region meet its demand exactly
    for j in range(n_r):
        model += mip.xsum(ships[i][j] for i in range(n_w)) == demands[j]

    # a warehouse that is opened can ship at most max_shipping units in total;
    # a warehouse that is not opened ships nothing
    for i in range(n_w):
        model += (
            mip.xsum(ships[i][j] for j in range(n_r))
            <= max_shipping * open_w[i]
        )

    # restriction 1: if the New York warehouse is opened, Los Angeles must be too
    ny = warehouse_s.index("New York")
    la = warehouse_s.index("Los Angeles")
    model += open_w[ny] <= open_w[la]

    # restriction 2: no more than three warehouses can be operational
    model += mip.xsum(open_w) <= 3

    # restriction 3: either Atlanta or Los Angeles must be opened
    atl = warehouse_s.index("Atlanta")
    model += open_w[atl] + open_w[la] >= 1

    # total_cost = fixed costs of the opened warehouses + shipping costs
    model += (
        total
        == mip.xsum(fixed_costs[i] * open_w[i] for i in range(n_w))
        + mip.xsum(
            shipping_costs[i][j] * ships[i][j]
            for i in range(n_w)
            for j in range(n_r)
        )
    )

    model.objective = total
    return model, {
        "open_warehouse": open_w,
        "ships": ships,
        "total_cost": total,
    }
