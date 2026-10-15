# Aircraft assignment: assign multiple types of aircraft to a set of routes
# to minimize the total operational cost, meeting every route's passenger
# demand within each aircraft type's availability.
# allocation[i][j] = number of aircraft of type i assigned to route j.
# Each allocation is a unary (order) integer: ge[i][j][k] is true exactly when
# allocation[i][j] >= k + 1, with the upper bound taken from the type's availability.

from paramita.modelling import Bool, If


def build(instance):
    avail = instance["availability"]
    cap = instance["capabilities"]
    cost = instance["costs"]
    demand = instance["demand"]
    n_types = len(avail)
    n_routes = len(demand)

    ge = [
        [[Bool(f"ge_{i}_{j}_{k}") for k in range(avail[i])] for j in range(n_routes)]
        for i in range(n_types)
    ]
    x = [[sum(ge[i][j]) for j in range(n_routes)] for i in range(n_types)]

    cons = []

    # unary order: allocation >= k + 1 implies allocation >= k
    for i in range(n_types):
        for j in range(n_routes):
            for k in range(avail[i] - 1):
                cons.append(If(ge[i][j][k + 1], ge[i][j][k]))

    # Each aircraft type has a limited number of available units:
    # the aircraft of type i assigned over all routes do not exceed availability[i].
    for i in range(n_types):
        cons.append(sum(x[i][j] for j in range(n_routes)) <= avail[i])

    # Each route has a specific passenger demand that must be satisfied:
    # the seats of all assigned aircraft on route j cover demand[j].
    for j in range(n_routes):
        cons.append(sum(cap[i][j] * x[i][j] for i in range(n_types)) >= demand[j])

    # Objective: minimize the total operational cost over all assignments.
    total = sum(cost[i][j] * x[i][j] for i in range(n_types) for j in range(n_routes))

    return cons, {"allocation": x}, ("minimize", total)
