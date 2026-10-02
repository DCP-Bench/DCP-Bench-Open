"""Aircraft assignment: decide how many aircraft of each type fly each route so
that every route's passenger demand is met at the least total operating cost.

Each aircraft type has a limited number of units. A unit of type i on route j
carries capabilities[i][j] passengers and costs costs[i][j].
"""
import pulp


def build(instance):
    availability = instance["availability"]  # units available of each aircraft type
    demand = instance["demand"]              # passengers to carry on each route
    capabilities = instance["capabilities"]  # passengers one aircraft of type i carries on route j
    costs = instance["costs"]                # cost of flying one aircraft of type i on route j

    n_types = len(availability)
    n_routes = len(demand)

    problem = pulp.LpProblem("aircraft_assignment", pulp.LpMinimize)

    # allocation[i][j] = number of aircraft of type i assigned to route j (declared
    # output). A type cannot put more aircraft on one route than it has in total,
    # so availability[i] bounds each entry.
    allocation = [[pulp.LpVariable(f"allocation_{i}_{j}", 0, availability[i], cat="Integer")
                   for j in range(n_routes)] for i in range(n_types)]

    # objective: minimise the total operating cost of the assignment
    problem += pulp.lpSum(costs[i][j] * allocation[i][j]
                          for i in range(n_types) for j in range(n_routes))

    # an aircraft type cannot be assigned beyond the units it has available
    for i in range(n_types):
        problem += pulp.lpSum(allocation[i]) <= availability[i]

    # the passengers carried on each route cover the route's demand
    for j in range(n_routes):
        problem += pulp.lpSum(capabilities[i][j] * allocation[i][j]
                              for i in range(n_types)) >= demand[j]

    return problem, {"allocation": allocation}
