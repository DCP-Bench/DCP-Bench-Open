# Aircraft assignment: choose how many aircraft of each type fly each route so
# every route's passenger demand is met, no type is used beyond its fleet, and
# the total operating cost is minimal.
from ortools.sat.python import cp_model


def build(instance):
    availability = instance["availability"]  # aircraft available per type
    demand = instance["demand"]  # passengers to carry per route
    capabilities = instance["capabilities"]  # passengers a type carries on a route
    costs = instance["costs"]  # cost of one aircraft of a type on a route
    n_types = len(availability)
    n_routes = len(demand)

    model = cp_model.CpModel()

    # allocation[i][j] = number of aircraft of type i assigned to route j; a
    # type never needs more aircraft on one route than its whole fleet
    allocation = [
        [model.new_int_var(0, max(availability), f"allocation_{i}_{j}") for j in range(n_routes)]
        for i in range(n_types)
    ]

    # a type cannot be assigned more aircraft than are available
    for i in range(n_types):
        model.add(sum(allocation[i]) <= availability[i])

    # the aircraft on each route together carry at least the route's demand
    for j in range(n_routes):
        model.add(sum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= demand[j])

    # minimise the total operating cost of the assignment
    model.minimize(sum(costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)))

    return model, {"allocation": allocation}
