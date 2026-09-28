"""Appointment scheduling: give each person their own interview slot at a time they are free."""
from docplex.mp.model import Model


def build(instance):
    free = instance["m"]  # free[i][j] is 1 if person i is free in slot j
    people = range(len(free))

    model = Model("appointment_scheduling")

    # x[i, j] is 1 when person i is interviewed in slot j.
    x = model.binary_var_matrix(people, people, name="x")

    for i in people:
        # Person i is interviewed in exactly one slot in which they are free.
        model.add_constraint(model.sum(free[i][j] * x[i, j] for j in people) == 1, ctname=f"free_{i}")
        # Person i gets exactly one slot.
        model.add_constraint(model.sum(x[i, j] for j in people) == 1, ctname=f"person_{i}")
        # Slot i goes to exactly one person.
        model.add_constraint(model.sum(x[j, i] for j in people) == 1, ctname=f"slot_{i}")

    return model, {"x": [[x[i, j] for j in people] for i in people]}
