# Facility location: decide which of four candidate warehouses to open and how
# many units each ships to each region, meeting every region's demand at the
# least total cost (fixed cost of the open warehouses plus shipping cost),
# subject to three rules about which warehouses may be open together.
from hermax.model import Model


def build(instance):
    names = instance["warehouse_s"]  # warehouse cities
    fixed_costs = instance["fixed_costs"]  # weekly fixed cost of each warehouse
    max_shipping = instance["max_shipping"]  # most units one warehouse can send per week
    demands = instance["demands"]  # weekly demand of each region
    shipping_costs = instance["shipping_costs"]  # cost per unit from warehouse i to region j
    n_warehouses = len(names)
    n_regions = len(demands)
    new_york, los_angeles, atlanta = (names.index(city) for city in ("New York", "Los Angeles", "Atlanta"))

    m = Model()
    # open_warehouse[i] is true when warehouse i is open
    open_warehouse = m.bool_vector("open_warehouse", n_warehouses)
    # ships[i][j] = units sent from warehouse i to region j (0 for a closed warehouse)
    ships = m.int_matrix("ships", n_warehouses, n_regions, 0, max_shipping)

    # a warehouse sends at most max_shipping units, and nothing when it is closed
    for i in range(n_warehouses):
        m &= (sum(ships[i][j] for j in range(n_regions)) <= max_shipping * open_warehouse[i])

    # every region receives at least its demand
    for j in range(n_regions):
        m &= (sum(ships[i][j] for i in range(n_warehouses)) >= demands[j])

    # 1. if the New York warehouse is open, the Los Angeles one must be open too
    m &= open_warehouse[new_york].implies(open_warehouse[los_angeles])
    # 2. at most three warehouses are open
    m &= (sum(1 * open_warehouse[i] for i in range(n_warehouses)) <= 3)
    # 3. the Atlanta or the Los Angeles warehouse (or both) must be open
    m &= (open_warehouse[atlanta] | open_warehouse[los_angeles])

    # Minimise the total cost: every unit shipped pays its shipping cost exactly when
    # ships >= k holds, and every open warehouse pays its fixed cost.
    for i in range(n_warehouses):
        m.obj[fixed_costs[i]] += ~open_warehouse[i]
        for j in range(n_regions):
            for k in range(1, max_shipping + 1):
                m.obj[shipping_costs[i][j]] += ~(ships[i][j] >= k)

    # total_cost is a declared output: the same sum built from scaled integers
    fixed = []
    for i in range(n_warehouses):
        flag = m.int(f"open_flag_{i}", 0, 1)
        m &= (~open_warehouse[i] | (flag == 1))
        m &= (open_warehouse[i] | (flag == 0))
        fixed.append(m.scale(flag, fixed_costs[i]))
    shipped = [m.scale(ships[i][j], shipping_costs[i][j]) for i in range(n_warehouses) for j in range(n_regions)]
    total_cost = m.sum_var(fixed + shipped)

    return m, {"total_cost": total_cost, "open_warehouse": open_warehouse, "ships": ships}
