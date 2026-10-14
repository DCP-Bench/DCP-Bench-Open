# Multi-commodity transportation: ship each product from the origins to the destinations, meeting every demand and respecting supplies and lane limits, at minimum total cost.
from pycsp3 import *

supply = data.supply
demand = data.demand
limit = data.limit
cost = data.cost
num_origins = len(supply)
num_products = len(supply[0])
num_destinations = len(demand)
max_flow = max(max(row) for row in supply + demand)

# ship[i][j][p] = units of product p shipped from origin i to destination j
ship = VarArray(size=[num_origins, num_destinations, num_products], dom=range(max_flow + 1))
# total_cost is the cost of all shipments
total_cost = Var(dom=range(sum(cost[i][j][p] * max_flow for i in range(num_origins) for j in range(num_destinations) for p in range(num_products)) + 1))

satisfy(
    # the shipments of each product from an origin do not exceed its supply
    [Sum(ship[i][j][p] for j in range(num_destinations)) <= supply[i][p] for i in range(num_origins) for p in range(num_products)],
    # the shipments of each product to a destination meet its demand
    [Sum(ship[i][j][p] for i in range(num_origins)) == demand[j][p] for j in range(num_destinations) for p in range(num_products)],
    # all products together on a lane do not exceed the lane limit
    [Sum(ship[i][j][p] for p in range(num_products)) <= limit[i][j] for i in range(num_origins) for j in range(num_destinations)],
    # the total cost is the cost of shipping each product along each lane
    total_cost == Sum(cost[i][j][p] * ship[i][j][p] for i in range(num_origins) for j in range(num_destinations) for p in range(num_products)),
)

# minimise the total cost of shipping all products
minimize(total_cost)
