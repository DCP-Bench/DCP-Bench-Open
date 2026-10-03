"""Bus driver scheduling: choose a set of shifts so that every piece of work is covered by
exactly one chosen shift, using as few shifts as possible (set partitioning).

The model reports x, with x[i] = 1 when shift i is chosen.
"""
from docplex.mp.model import Model


def build(instance):
    num_work = instance["num_work"]      # number of pieces of work
    num_shifts = instance["num_shifts"]  # number of possible shifts
    shifts = instance["shifts"]          # shifts[i] lists the pieces of work shift i covers

    model = Model("bus_driver_scheduling")

    # x[i] is 1 if shift i is selected.
    x = [model.binary_var(name=f"x_{i}") for i in range(num_shifts)]

    # Each piece of work is covered by exactly one selected shift.
    for t in range(num_work):
        model.add_constraint(model.sum(x[i] for i in range(num_shifts) if t in shifts[i]) == 1)

    # Objective: the fewest shifts.
    model.minimize(model.sum(x))

    return model, {"x": x}
