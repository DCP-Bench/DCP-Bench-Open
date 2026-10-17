# Aircraft assignment: assign aircraft of several types to several routes so that
# every route's passenger demand is met, each aircraft type stays within its
# availability, and the total operational cost is minimised.
# allocation[i][j] is the number of aircraft of type i assigned to route j.
import mip


def build(instance):
    availability = instance["availability"]
    demand = instance["demand"]
    capabilities = instance["capabilities"]
    costs = instance["costs"]

    n_types = len(availability)
    n_routes = len(demand)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Each aircraft type has a limited number of available units.
    alloc = [
        [
            model.add_var(
                name=f"alloc_{i}_{j}",
                lb=0,
                ub=availability[i],
                var_type=mip.INTEGER,
            )
            for j in range(n_routes)
        ]
        for i in range(n_types)
    ]

    # Each aircraft type has a limited number of available units.
    for i in range(n_types):
        model += mip.xsum(alloc[i][j] for j in range(n_routes)) <= availability[i]

    # Each route has a specific passenger demand that must be satisfied.
    # For each aircraft type and route, we are given the passenger capacity.
    for j in range(n_routes):
        model += (
            mip.xsum(capabilities[i][j] * alloc[i][j] for i in range(n_types))
            >= demand[j]
        )

    # The goal is to minimize the overall cost.
    model.objective = mip.xsum(
        costs[i][j] * alloc[i][j] for i in range(n_types) for j in range(n_routes)
    )

    return model, {"allocation": alloc}
