# Aircraft assignment: decide how many aircraft of each type fly each route so
# that every route's passenger demand is met, no type is used beyond its
# availability, and the total operating cost is minimal.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    availability = instance["availability"]
    demand = instance["demand"]
    capabilities = instance["capabilities"]
    costs = instance["costs"]
    num_aircraft = len(availability)
    num_routes = len(demand)

    pool = IDPool()
    # allocation[a][r] is the number of aircraft of type a assigned to route r.
    # A type can never put more than its availability on one route, so that is
    # the upper bound (at least 1, so no domain is a single value; the
    # availability constraint below still holds a type with none at 0).
    # The domains are a handful of values, so the direct
    # encoding (one literal per value) is small and gives the cost literals.
    allocation = [[Integer(f"allocation_{a}_{r}", 0, max(availability[a], 1), vpool=pool)
                   for r in range(num_routes)] for a in range(num_aircraft)]
    engine = IntegerEngine(vars=[x for row in allocation for x in row], vpool=pool)

    # The aircraft of each type assigned over all routes do not exceed its availability.
    for a in range(num_aircraft):
        engine.add_linear(sum(allocation[a][r] for r in range(num_routes)) <= availability[a])

    # The seats flown on each route cover its passenger demand.
    for r in range(num_routes):
        engine.add_linear(sum(capabilities[a][r] * allocation[a][r]
                              for a in range(num_aircraft)) >= demand[r])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise the total cost: putting v aircraft of type a on route r pays
    # v * costs[a][r]. A negative cost is paid as its shortfall from the most
    # aircraft the variable allows, which differs from the cost by a constant.
    for a in range(num_aircraft):
        for r in range(num_routes):
            x = allocation[a][r]
            c = costs[a][r]
            ub = max(availability[a], 1)
            for v in range(0, ub + 1):
                w = c * v if c > 0 else -c * (ub - v)
                if w > 0:
                    formula.append([-x.equals(v)], weight=w)

    return formula, {"allocation": allocation}
