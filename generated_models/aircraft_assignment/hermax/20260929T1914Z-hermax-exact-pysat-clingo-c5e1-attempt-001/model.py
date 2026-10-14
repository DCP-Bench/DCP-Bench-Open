# Aircraft assignment: choose how many aircraft of each type fly each route so
# every route's passenger demand is met, no type is used beyond its fleet, and
# the total operating cost is minimal.
from hermax.model import Model


def build(instance):
    availability = instance["availability"]  # aircraft available per type
    demand = instance["demand"]  # passengers to carry per route
    capabilities = instance["capabilities"]  # passengers a type carries on a route
    costs = instance["costs"]  # cost of one aircraft of a type on a route
    n_types = len(availability)
    n_routes = len(demand)
    most = max(availability)

    m = Model()
    # allocation[i][j] = number of aircraft of type i assigned to route j; a type
    # never needs more aircraft on one route than its whole fleet
    allocation = m.int_matrix("allocation", n_types, n_routes, 0, most)

    # a type cannot be assigned more aircraft than are available
    for i in range(n_types):
        m &= (sum(allocation[i][j] for j in range(n_routes)) <= availability[i])

    # the aircraft on each route together carry at least the route's demand
    for j in range(n_routes):
        m &= (sum(capabilities[i][j] * allocation[i][j] for i in range(n_types)) >= demand[j])

    # Minimise the total operating cost. Each aircraft costs its route cost, so the
    # k-th aircraft of a type on a route pays that cost exactly when it is used, that
    # is when allocation >= k holds: the soft clause is the negated literal.
    for i in range(n_types):
        for j in range(n_routes):
            for k in range(1, most + 1):
                m.obj[costs[i][j]] += ~(allocation[i][j] >= k)

    return m, {"allocation": allocation}
