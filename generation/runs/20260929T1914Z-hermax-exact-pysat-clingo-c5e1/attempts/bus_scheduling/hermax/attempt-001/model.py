# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
from hermax.model import Model


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    m = Model()
    # x[i] = number of buses that start working in slot i
    x = m.int_vector("x", slots, 0, sum(demands))

    # a bus covers its starting slot and the next one (the day wraps around),
    # so slot i+1 is served by the buses starting in slots i and i+1
    for i in range(slots):
        nxt = (i + 1) % slots
        m &= (x[i] + x[nxt] >= demands[nxt])

    # use as few buses as possible: every bus counted by x[i] >= k pays one
    for i in range(slots):
        for k in range(1, sum(demands) + 1):
            m.obj[1] += ~(x[i] >= k)

    return m, {"x": x}
