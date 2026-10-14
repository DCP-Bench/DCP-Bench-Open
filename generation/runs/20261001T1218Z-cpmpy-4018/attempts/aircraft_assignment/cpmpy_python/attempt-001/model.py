# Aircraft assignment: choose how many aircraft of each type fly each route so
# every route's passenger demand is met, no type is used beyond its fleet, and
# the total operating cost is minimal.
import cpmpy as cp


def build(instance):
    availability = instance["availability"]    # aircraft available per type
    demand = instance["demand"]                # passengers to carry per route
    capabilities = instance["capabilities"]    # passengers a type carries on a route
    costs = instance["costs"]                  # cost of one aircraft of a type on a route
    n_types = len(availability)
    n_routes = len(demand)

    # allocation[i, j] = number of aircraft of type i assigned to route j. A type never needs more
    # aircraft on one route than its whole fleet, so the largest fleet bounds every entry.
    allocation = cp.intvar(0, max(availability), shape=(n_types, n_routes), name="allocation")

    model = cp.Model()

    # A type cannot be assigned more aircraft than are available.
    for i in range(n_types):
        model += cp.sum(allocation[i, :]) <= availability[i]

    # The aircraft on each route together carry at least the route's passenger demand.
    for j in range(n_routes):
        model += cp.sum([capabilities[i][j] * allocation[i, j] for i in range(n_types)]) >= demand[j]

    # Minimise the total operating cost of the assignment.
    model.minimize(cp.sum([costs[i][j] * allocation[i, j]
                           for i in range(n_types) for j in range(n_routes)]))

    return model, {"allocation": allocation}
