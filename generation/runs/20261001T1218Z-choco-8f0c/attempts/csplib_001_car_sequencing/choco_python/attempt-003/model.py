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
    # (pychoco's count takes the number of occurrences as a variable, so the demand
    # is passed as a variable fixed to that value)
    for t in range(n_types):
        model.count(t, sequence, model.intvar(demand[t], demand[t])).post()

    # the options in the setup table are those of the car type in that slot: the row
    # (car type, options it requires) must be one of the rows of the requires table.
    # One table over all options at once propagates between the type and its options
    # better than one element constraint per option.
    allowed = [[t] + list(requires[t]) for t in range(n_types)]
    for s in range(n_cars):
        model.table([sequence[s]] + setup[s], allowed).post()

    # no station is overloaded: among any per_slots[o] consecutive slots,
    # at most at_most[o] cars need option o
    for o in range(n_options):
        for s in range(n_cars - per_slots[o] + 1):
            model.sum([setup[k][o] for k in range(s, s + per_slots[o])], "<=", at_most[o]).post()

    # Implied constraints (they follow from the ones above, and help the solver prune):
    # the first j slots can hold at most at_most[o] * (j div per_slots[o]) plus the
    # part of the last window (at most at_most[o], and at most j mod per_slots[o])
    # cars with option o, so the remaining slots must hold the rest of the demand
    # for option o.
    for o in range(n_options):
        total_with_option = sum(demand[t] * requires[t][o] for t in range(n_types))
        for j in range(n_cars):
            most_in_first_j = at_most[o] * (j // per_slots[o]) + min(at_most[o], j % per_slots[o])
            needed_after = total_with_option - most_in_first_j
            if needed_after > 0:
                model.sum([setup[k][o] for k in range(j, n_cars)], ">=", needed_after).post()

    return model, {"sequence": sequence}
