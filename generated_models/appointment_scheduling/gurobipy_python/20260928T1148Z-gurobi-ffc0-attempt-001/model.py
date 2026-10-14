"""Appointment scheduling: give each person their own interview slot at a time they are free."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    free = instance["m"]  # free[i][j] is 1 if person i is free in slot j
    n = len(free)
    people = range(n)

    model = gp.Model("appointment_scheduling")

    # x[i, j] is 1 when person i is interviewed in slot j.
    x = model.addVars(people, people, vtype=GRB.BINARY, name="x")

    for i in people:
        # Person i is interviewed in exactly one slot in which they are free.
        model.addConstr(gp.quicksum(free[i][j] * x[i, j] for j in people) == 1, name=f"free[{i}]")
        # Person i gets exactly one slot.
        model.addConstr(x.sum(i, "*") == 1, name=f"person[{i}]")
        # Slot i goes to exactly one person.
        model.addConstr(x.sum("*", i) == 1, name=f"slot[{i}]")

    return model, {"x": [[x[i, j] for j in people] for i in people]}
