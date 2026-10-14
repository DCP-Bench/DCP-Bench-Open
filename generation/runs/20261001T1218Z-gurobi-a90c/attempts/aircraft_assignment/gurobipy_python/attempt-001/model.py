"""Aircraft assignment: assign aircraft of each type to routes at least cost so that every route's demand is carried."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    availability = instance["availability"]  # per aircraft type: how many aircraft exist
    demand = instance["demand"]              # per route: passengers to carry
    capabilities = instance["capabilities"]  # [type][route]: passengers one aircraft carries on the route
    costs = instance["costs"]                # [type][route]: cost of one aircraft of the type on the route
    types = range(len(availability))
    routes = range(len(demand))

    model = gp.Model("aircraft_assignment")

    # allocation[a, r] is the number of aircraft of type a flying route r; no more than the
    # largest fleet can ever be used (the reference's variable bound).
    allocation = model.addVars(types, routes, lb=0, ub=max(availability), vtype=GRB.INTEGER, name="allocation")

    # An aircraft type cannot be used on more routes than it has aircraft.
    for a in types:
        model.addConstr(allocation.sum(a, "*") <= availability[a], name=f"fleet[{a}]")

    # The aircraft on a route carry at least the route's demand.
    for r in routes:
        model.addConstr(gp.quicksum(capabilities[a][r] * allocation[a, r] for a in types) >= demand[r],
                        name=f"demand[{r}]")

    # Minimise the total cost of the assignment.
    model.setObjective(gp.quicksum(costs[a][r] * allocation[a, r] for a in types for r in routes), GRB.MINIMIZE)

    return model, {"allocation": [[allocation[a, r] for r in routes] for a in types]}
