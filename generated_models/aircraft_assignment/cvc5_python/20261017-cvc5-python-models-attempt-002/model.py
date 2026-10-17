# Aircraft assignment: assign aircraft of several types to routes so that every
# route's passenger demand is met, the availability of each aircraft type is not
# exceeded, and the total operational cost is minimised.
# allocation[i][j] is the number of aircraft of type i assigned to route j.
# Sizes and all data come from the instance.

import cvc5.pythonic as cz


def build(instance):
    availability = instance["availability"]
    demand = instance["demand"]
    capabilities = instance["capabilities"]
    costs = instance["costs"]

    n_types = len(availability)
    n_routes = len(demand)

    # Number of aircraft of each type on each route, bounded by the type's availability.
    alloc = [[cz.Int(f"a_{i}_{j}") for j in range(n_routes)] for i in range(n_types)]
    constraints = []
    for i in range(n_types):
        for j in range(n_routes):
            constraints.append(alloc[i][j] >= 0)
            constraints.append(alloc[i][j] <= availability[i])

    # Each aircraft type can fly at most its available number of units in total over all routes.
    for i in range(n_types):
        constraints.append(cz.Sum([alloc[i][j] for j in range(n_routes)]) <= availability[i])

    # Every route's passenger demand must be met by the seats of the aircraft assigned to it.
    for j in range(n_routes):
        constraints.append(
            cz.Sum([capabilities[i][j] * alloc[i][j] for i in range(n_types)]) >= demand[j]
        )

    # Total operational cost of all assignments, to be minimised.
    total_cost = cz.Sum([costs[i][j] * alloc[i][j] for i in range(n_types) for j in range(n_routes)])

    outputs = {"allocation": [[alloc[i][j] for j in range(n_routes)] for i in range(n_types)]}
    return constraints, outputs, ("minimize", total_cost)
