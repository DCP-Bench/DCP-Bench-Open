# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
from exact import Exact


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    solver = Exact()
    # x[i] = number of buses that start working in slot i
    x = [f"x_{i}" for i in range(slots)]
    for name in x:
        solver.addVariable(name, 0, sum(demands))

    # a bus covers its starting slot and the next one (the day wraps around),
    # so slot i+1 is served by the buses starting in slots i and i+1
    for i in range(slots):
        nxt = (i + 1) % slots
        solver.addConstraint([(1, x[i]), (1, x[nxt])], True, demands[nxt])

    # use as few buses as possible
    return solver, {"x": x}, ("minimize", [(1, name) for name in x])
