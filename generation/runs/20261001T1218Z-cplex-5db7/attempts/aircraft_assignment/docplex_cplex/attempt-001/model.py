"""Aircraft assignment: assign aircraft of several types to routes at the lowest total cost.

Each type has a limited number of aircraft, each route has a passenger demand, and each
(type, route) pair has a seat capacity and a cost per aircraft. The model chooses how many
aircraft of each type fly each route so that every demand is met.
"""
from docplex.mp.model import Model


def build(instance):
    availability = instance["availability"]  # availability[a]: aircraft available of type a
    demand = instance["demand"]              # demand[r]: passengers on route r
    capabilities = instance["capabilities"]  # capabilities[a][r]: seats of one type a aircraft on route r
    costs = instance["costs"]                # costs[a][r]: cost of one type a aircraft on route r

    num_aircraft = len(availability)
    num_routes = len(demand)
    types = range(num_aircraft)
    routes = range(num_routes)

    model = Model("aircraft_assignment")

    # allocation[a][r] is the number of aircraft of type a assigned to route r; at most
    # max(availability) of them, as no type has more aircraft than that.
    allocation = [[model.integer_var(0, max(availability), name=f"allocation_{a}_{r}")
                   for r in routes] for a in types]

    # Objective: minimize the total cost of the assignment.
    model.minimize(model.sum(costs[a][r] * allocation[a][r] for a in types for r in routes))

    # The aircraft of a type assigned to all routes do not exceed its availability.
    for a in types:
        model.add_constraint(model.sum(allocation[a][r] for r in routes) <= availability[a])

    # The seats on each route cover its demand.
    for r in routes:
        model.add_constraint(
            model.sum(capabilities[a][r] * allocation[a][r] for a in types) >= demand[r])

    return model, {"allocation": allocation}
