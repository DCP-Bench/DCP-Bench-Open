# Aircraft assignment: choose how many aircraft of each type fly each route so
# every route's passenger demand is met, no type is used beyond its fleet, and
# the total operating cost is minimal.
from pychoco.model import Model


def build(instance):
    availability = instance["availability"]  # aircraft available per type
    demand = instance["demand"]  # passengers to carry per route
    capabilities = instance["capabilities"]  # passengers a type carries on a route
    costs = instance["costs"]  # cost of one aircraft of a type on a route
    n_types = len(availability)
    n_routes = len(demand)

    model = Model()

    # allocation[i][j] = number of aircraft of type i assigned to route j; a
    # type never needs more aircraft on one route than its whole fleet
    allocation = [
        [model.intvar(0, max(availability), name=f"allocation_{i}_{j}") for j in range(n_routes)]
        for i in range(n_types)
    ]

    # a type cannot be assigned more aircraft than are available
    for i in range(n_types):
        model.sum(allocation[i], "<=", availability[i]).post()

    # the aircraft on each route together carry at least the route's demand
    for j in range(n_routes):
        model.scalar([allocation[i][j] for i in range(n_types)], [capabilities[i][j] for i in range(n_types)],
                     ">=", demand[j]).post()

    # total operating cost of the assignment. Choco minimises a single variable,
    # so the cost is tied to one with an equality.
    cells = [allocation[i][j] for i in range(n_types) for j in range(n_routes)]
    cell_costs = [costs[i][j] for i in range(n_types) for j in range(n_routes)]
    total_cost = model.intvar(0, max(availability) * sum(cell_costs), name="total_cost")
    model.scalar(cells, cell_costs, "=", total_cost).post()

    return model, {"allocation": allocation}, ("minimize", total_cost)
