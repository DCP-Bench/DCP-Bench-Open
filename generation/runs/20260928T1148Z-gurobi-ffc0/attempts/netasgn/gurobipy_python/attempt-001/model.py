"""Project assignment: split each person's hours over the projects to meet every demand at the least cost."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]    # cost[i][j]: hourly cost of person i on project j
    limit = instance["limit"]  # limit[i][j]: most hours person i may work on project j
    people = range(len(supply))
    projects = range(len(demand))

    model = gp.Model("netasgn")

    # assign[i, j] is the hours person i works on project j, at most limit[i][j].
    # The reference model also declares every hour count in 0..10, so that bound
    # is mirrored here.
    assign = model.addVars(people, projects, lb=0, vtype=GRB.INTEGER, name="assign")
    for i in people:
        for j in projects:
            assign[i, j].UB = min(10, limit[i][j])

    # Each person works exactly their available hours.
    for i in people:
        model.addConstr(assign.sum(i, "*") == supply[i], name=f"supply[{i}]")

    # Each project receives exactly the hours it requires.
    for j in projects:
        model.addConstr(assign.sum("*", j) == demand[j], name=f"demand[{j}]")

    # Minimise the total cost of the hours assigned.
    total_cost = gp.quicksum(cost[i][j] * assign[i, j] for i in people for j in projects)
    model.setObjective(total_cost, GRB.MINIMIZE)

    return model, {"assign": [[assign[i, j] for j in projects] for i in people],
                   "total_cost": total_cost}
