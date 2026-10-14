"""Bus scheduling: the fewest buses that meet the demand in every 4-hour slot of the day.

A bus works 8 successive hours, so a bus that starts in slot i covers slots i and i + 1, and
the day wraps around from the last slot to the first. demands[i] is the number of buses
needed in slot i.
"""
from docplex.mp.model import Model


def build(instance):
    demands = instance["demands"]  # demands[i]: buses needed in the i-th 4-hour slot
    slots = len(demands)

    model = Model("bus_scheduling")

    # x[i] is the number of buses that start working in slot i. There are never more than
    # the total demand of them.
    x = [model.integer_var(0, sum(demands), name=f"x_{i}") for i in range(slots)]

    # The buses on duty in slot i + 1 are those that started in slot i and in slot i + 1; they
    # must meet the demand of slot i + 1. Slot numbers wrap around.
    for i in range(slots):
        model.add_constraint(x[i] + x[(i + 1) % slots] >= demands[(i + 1) % slots])

    # Objective: minimize the total number of buses.
    model.minimize(model.sum(x))

    return model, {"x": x}
