# Car sequencing: order the cars on an assembly line so that no option's station
# is asked to handle more cars than its capacity allows in any window of slots.
from pychoco.model import Model


def build(instance):
    at_most = instance["at_most"]  # at most this many cars with option o ...
    per_slots = instance["per_slots"]  # ... in any window of this many consecutive slots
    demand = instance["demand"]  # how many cars of each type are to be built
    requires = instance["requires"]  # requires[t][o] = 1 if car type t needs option o

    n_cars = sum(demand)  # one slot per car
    n_options = len(at_most)
    n_types = len(demand)

    model = Model()

    # sequence[s] = the car type placed in slot s
    sequence = [model.intvar(0, n_types - 1, name=f"sequence_{s}") for s in range(n_cars)]
    # setup[s][o] = 1 if the car in slot s needs option o
    setup = [[model.boolvar(name=f"setup_{s}_{o}") for o in range(n_options)] for s in range(n_cars)]

    # the number of cars of each type in the sequence equals the demand for that type
    for t in range(n_types):
        model.count(t, sequence, demand[t]).post()

    # the options in the setup table are those of the car type in that slot
    # (element over the column of the requires table for option o)
    for s in range(n_cars):
        for o in range(n_options):
            model.element(setup[s][o], [requires[t][o] for t in range(n_types)], sequence[s]).post()

    # no station is overloaded: among any per_slots[o] consecutive slots,
    # at most at_most[o] cars need option o
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            model.sum([setup[k][o] for k in range(s, s + per_slots[o])], "<=", at_most[o]).post()

    return model, {"sequence": sequence}
