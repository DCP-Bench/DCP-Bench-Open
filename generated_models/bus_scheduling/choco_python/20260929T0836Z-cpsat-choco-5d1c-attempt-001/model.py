# Bus scheduling: the day is cut into equal time slots and a bus works two
# consecutive slots. Choose how many buses start in each slot so that every
# slot's demand is met with as few buses as possible.
from pychoco.model import Model


def build(instance):
    demands = instance["demands"]  # buses needed in each slot
    slots = len(demands)

    model = Model()

    # x[i] = number of buses that start working in slot i
    x = [model.intvar(0, sum(demands), name=f"x_{i}") for i in range(slots)]

    # a bus covers its starting slot and the next one (the day wraps around),
    # so slot i+1 is served by the buses starting in slots i and i+1
    for i in range(slots):
        nxt = (i + 1) % slots
        model.arithm(x[i], "+", x[nxt], ">=", demands[nxt]).post()

    # use as few buses as possible (Choco minimises one variable, so the total is tied to it)
    total = model.intvar(0, sum(demands) * slots, name="total_buses")
    model.sum(x, "=", total).post()

    return model, {"x": x}, ("minimize", total)
