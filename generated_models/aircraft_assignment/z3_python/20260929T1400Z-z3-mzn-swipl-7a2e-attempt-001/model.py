# Aircraft assignment: choose how many aircraft of each type fly each route so
# every route's passenger demand is met, no type is used beyond its fleet, and
# the total operating cost is minimal.
import z3


def build(instance):
    availability = instance["availability"]  # aircraft available per type
    demand = instance["demand"]  # passengers to carry per route
    capabilities = instance["capabilities"]  # passengers a type carries on a route
    costs = instance["costs"]  # cost of one aircraft of a type on a route
    n_types = len(availability)
    n_routes = len(demand)

    solver = z3.Solver()

    # allocation[i][j] = number of aircraft of type i assigned to route j; a
    # type never needs more aircraft on one route than its whole fleet
    allocation = [[z3.Int(f"allocation_{i}_{j}") for j in range(n_routes)] for i in range(n_types)]
    for i in range(n_types):
        for j in range(n_routes):
            solver.add(allocation[i][j] >= 0, allocation[i][j] <= max(availability))

    # a type cannot be assigned more aircraft than are available
    for i in range(n_types):
        solver.add(z3.Sum(allocation[i]) <= availability[i])

    # the aircraft on each route together carry at least the route's demand
    for j in range(n_routes):
        solver.add(z3.Sum([capabilities[i][j] * allocation[i][j] for i in range(n_types)]) >= demand[j])

    # minimise the total operating cost of the assignment
    total_cost = z3.Sum([costs[i][j] * allocation[i][j] for i in range(n_types) for j in range(n_routes)])

    return solver, {"allocation": allocation}, ("minimize", total_cost)
