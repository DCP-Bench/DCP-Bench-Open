# Aircraft assignment: decide how many aircraft of each type fly each route so that every
# route's demand is met, no type is used more than it is available, at the lowest total cost.
# PySAT only decides satisfiability, so the cost to minimise is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    availability = instance["availability"]
    demand = instance["demand"]
    capabilities = instance["capabilities"]
    costs = instance["costs"]
    n_types, n_routes = len(availability), len(demand)

    pool = IDPool()
    # allocation[a][r] = number of aircraft of type a on route r
    allocation = [[Integer(f"allocation{a}_{r}", 0, max(availability), vpool=pool)
                   for r in range(n_routes)] for a in range(n_types)]
    engine = IntegerEngine(vars=[v for row in allocation for v in row], vpool=pool)

    # a type is not used more than the aircraft available
    for a in range(n_types):
        engine.add_linear(sum(allocation[a]) <= availability[a])
    # the capacity assigned to a route meets its demand
    for r in range(n_routes):
        engine.add_linear(sum(capabilities[a][r] * allocation[a][r] for a in range(n_types)) >= demand[r])

    cost = sum(costs[a][r] * allocation[a][r] for a in range(n_types) for r in range(n_routes))
    return engine.clausify(), {"allocation": allocation}, ("minimize", cost)
