from pycsp3 import *

# assign aircraft of each type to routes, minimising the total operational cost
n_types = len(data.availability)
n_routes = len(data.demand)

# allocation[i][j] is the number of aircraft of type i assigned to route j
allocation = VarArray(size=[n_types, n_routes], dom=range(0, max(data.availability) + 1))

satisfy(
    # the aircraft of each type assigned to all routes must not exceed the units available of that type
    [Sum(allocation[i]) <= data.availability[i] for i in range(n_types)],
    # each route must receive at least its passenger demand in passenger capacity
    [Sum(data.capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= data.demand[j] for j in range(n_routes)]
)

# minimise the total operational cost of all assigned aircraft
minimize(Sum(data.costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)))
