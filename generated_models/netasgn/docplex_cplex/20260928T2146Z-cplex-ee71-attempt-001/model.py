"""Project assignment: split each person's hours over the projects to meet every demand at the least cost."""
from docplex.mp.model import Model


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]    # cost[i][j]: hourly cost of person i on project j
    limit = instance["limit"]  # limit[i][j]: most hours person i may work on project j
    people = range(len(supply))
    projects = range(len(demand))

    model = Model("netasgn")

    # assign[i, j] is the hours person i works on project j, at most limit[i][j].
    # The reference model also declares every hour count in 0..10, so that bound
    # is mirrored here.
    assign = {(i, j): model.integer_var(0, min(10, limit[i][j]), name=f"assign_{i}_{j}")
              for i in people for j in projects}

    # Each person works exactly their available hours.
    for i in people:
        model.add_constraint(model.sum(assign[i, j] for j in projects) == supply[i], ctname=f"supply_{i}")

    # Each project receives exactly the hours it requires.
    for j in projects:
        model.add_constraint(model.sum(assign[i, j] for i in people) == demand[j], ctname=f"demand_{j}")

    # Minimise the total cost of the hours assigned.
    total_cost = model.sum(cost[i][j] * assign[i, j] for i in people for j in projects)
    model.minimize(total_cost)

    return model, {"assign": [[assign[i, j] for j in projects] for i in people], "total_cost": total_cost}
