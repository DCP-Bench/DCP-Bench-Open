# Aircraft assignment: assign aircraft of each type to each route so that every
# route's passenger demand is met, the number of aircraft of each type stays within
# its availability, and the total operational cost is minimised.
from pyscipopt import Model, quicksum


def build(instance):
    availability = instance["availability"]  # aircraft available per type
    demand = instance["demand"]              # passengers to carry per route
    capabilities = instance["capabilities"]  # seats per aircraft, [type][route]
    costs = instance["costs"]                # operational cost per aircraft, [type][route]

    n_types = len(availability)
    n_routes = len(demand)

    m = Model("aircraft_assignment")

    # allocation[i][j] = number of aircraft of type i assigned to route j
    x = [[m.addVar(name=f"x_{i}_{j}", vtype="I", lb=0, ub=availability[i])
          for j in range(n_routes)] for i in range(n_types)]

    # the aircraft of each type assigned to all routes cannot exceed its availability
    for i in range(n_types):
        m.addCons(quicksum(x[i][j] for j in range(n_routes)) <= availability[i])

    # the seats of all aircraft assigned to a route must cover its passenger demand
    for j in range(n_routes):
        m.addCons(quicksum(capabilities[i][j] * x[i][j] for i in range(n_types)) >= demand[j])

    # minimise the total operational cost of the assigned aircraft
    m.setObjective(quicksum(costs[i][j] * x[i][j]
                            for i in range(n_types) for j in range(n_routes)),
                   "minimize")

    return m, {"allocation": x}
