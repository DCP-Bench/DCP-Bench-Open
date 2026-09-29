# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
from ortools.sat.python import cp_model


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    model = cp_model.CpModel()

    # x[i] = number of buses that start working in slot i
    x = [model.new_int_var(0, sum(demands), f"x_{i}") for i in range(slots)]

    # a bus covers its starting slot and the next one (the day wraps around),
    # so slot i+1 is served by the buses starting in slots i and i+1
    for i in range(slots):
        nxt = (i + 1) % slots
        model.add(x[i] + x[nxt] >= demands[nxt])

    # use as few buses as possible
    model.minimize(sum(x))

    return model, {"x": x}
