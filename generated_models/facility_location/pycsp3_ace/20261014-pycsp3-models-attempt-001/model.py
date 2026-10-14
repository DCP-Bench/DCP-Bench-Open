from pycsp3 import *

# Facility location: warehouses in four cities can be opened. Each open warehouse can
# ship at most max_shipping units in total. Each region's demand must be met exactly.

fixed_costs = data.fixed_costs
shipping_costs = data.shipping_costs
demands = data.demands
max_shipping = data.max_shipping
n_warehouses = len(fixed_costs)
n_regions = len(demands)
# warehouse order: 0 New York, 1 Los Angeles, 2 Chicago, 3 Atlanta

# open_warehouse[i] is 1 when warehouse i is opened
open_warehouse = VarArray(size=n_warehouses, dom={0, 1})
# ships[i][j] is the number of units shipped from warehouse i to region j. A warehouse
# never ships more to a region than the region demands, nor more than max_shipping.
ships = VarArray(size=[n_warehouses, n_regions], dom=range(0, max_shipping + 1))
# total_cost is the fixed cost of the open warehouses plus the shipping cost
total_cost = Var(dom=range(0, sum(fixed_costs) + sum(demands[j] * max(shipping_costs[i][j]
                 for i in range(n_warehouses)) for j in range(n_regions)) + 1))

satisfy(
    # if New York is opened, then Los Angeles must also be opened
    imply(open_warehouse[0] == 1, open_warehouse[1] == 1),

    # no more than three warehouses can be operational
    Sum(open_warehouse) <= 3,

    # either Atlanta or Los Angeles must be opened
    Sum(open_warehouse[3], open_warehouse[1]) >= 1,

    # a warehouse ships only when it is open, and at most max_shipping units in total
    [Sum(ships[i]) <= max_shipping * open_warehouse[i] for i in range(n_warehouses)],

    # no region receives more than its demand from one warehouse
    [ships[i][j] <= demands[j] for i in range(n_warehouses) for j in range(n_regions)],

    # a closed warehouse ships nothing
    [ships[i][j] <= demands[j] * open_warehouse[i] for i in range(n_warehouses) for j in range(n_regions)],

    # the open warehouses have enough capacity for the total demand
    sum(demands) <= max_shipping * Sum(open_warehouse),

    # the demand of each region is met exactly by the warehouses
    [Sum(ships[i][j] for i in range(n_warehouses)) == demands[j] for j in range(n_regions)],

    # the total cost is the fixed costs of the open warehouses plus the shipping costs
    total_cost == Sum(fixed_costs[i] * open_warehouse[i] for i in range(n_warehouses))
    + Sum(shipping_costs[i][j] * ships[i][j] for i in range(n_warehouses) for j in range(n_regions)),
)

# minimise the total cost
minimize(total_cost)
