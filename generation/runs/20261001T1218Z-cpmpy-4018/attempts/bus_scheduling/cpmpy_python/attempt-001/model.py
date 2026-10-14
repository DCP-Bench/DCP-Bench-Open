# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
import cpmpy as cp


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    # x[i] = number of buses that start working in slot i; the total demand bounds any one slot.
    x = cp.intvar(0, sum(demands), shape=slots, name="x")

    model = cp.Model()

    # A bus covers its starting slot and the next one (the day wraps around), so slot i+1 is
    # served by the buses starting in slots i and i+1 and must reach its demand.
    for i in range(slots):
        nxt = (i + 1) % slots
        model += x[i] + x[nxt] >= demands[nxt]

    # Use as few buses as possible.
    model.minimize(cp.sum(x))

    return model, {"x": x}
