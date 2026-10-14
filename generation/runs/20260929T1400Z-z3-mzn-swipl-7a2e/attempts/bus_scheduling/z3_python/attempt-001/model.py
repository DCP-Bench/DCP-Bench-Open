# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
import z3


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    solver = z3.Solver()

    # x[i] = number of buses that start working in slot i
    x = [z3.Int(f"x_{i}") for i in range(slots)]
    for i in range(slots):
        solver.add(x[i] >= 0, x[i] <= sum(demands))

    # a bus covers its starting slot and the next one (the day wraps around),
    # so slot i+1 is served by the buses starting in slots i and i+1
    for i in range(slots):
        nxt = (i + 1) % slots
        solver.add(x[i] + x[nxt] >= demands[nxt])

    # use as few buses as possible
    return solver, {"x": x}, ("minimize", z3.Sum(x))
