"""Assignment: give every task to a different person at the least total cost; people may stay idle."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    cost = instance["cost"]  # cost[i][j]: cost of person j doing task i
    tasks = range(len(cost))
    people = range(len(cost[0]))

    model = gp.Model("assignment_costs")

    # x[i, j] is 1 when task i is assigned to person j.
    x = model.addVars(tasks, people, vtype=GRB.BINARY, name="x")

    # Each task is assigned to exactly one person.
    for i in tasks:
        model.addConstr(x.sum(i, "*") == 1, name=f"task[{i}]")

    # Each person takes at most one task.
    for j in people:
        model.addConstr(x.sum("*", j) <= 1, name=f"person[{j}]")

    # Minimise the total cost of the assignment.
    model.setObjective(gp.quicksum(cost[i][j] * x[i, j] for i in tasks for j in people), GRB.MINIMIZE)

    return model, {"x": [[x[i, j] for j in people] for i in tasks]}
