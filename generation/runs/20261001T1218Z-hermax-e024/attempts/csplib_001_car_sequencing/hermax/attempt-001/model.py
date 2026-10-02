# Car sequencing: arrange the cars on an assembly line so that no station
# (one per option) has to cope with more cars than it can handle in any
# window of consecutive slots.
from hermax.model import Model


def build(instance):
    at_most = instance["at_most"]  # a station copes with at most this many cars ...
    per_slots = instance["per_slots"]  # ... in any run of this many consecutive slots
    demand = instance["demand"]  # how many cars of each type must be built
    requires = instance["requires"]  # requires[t][o] = 1 if type t needs option o
    n_cars = sum(demand)
    n_types = len(demand)
    n_options = len(at_most)

    m = Model()
    # sequence[s] = the type of the car in slot s (types are numbered from 0)
    sequence = m.int_vector("sequence", n_cars, 0, n_types - 1)

    # the number of cars of each type in the sequence equals its demand
    for t in range(n_types):
        m &= (sum((sequence[s] == t) for s in range(n_cars)) == demand[t])

    # No station is overloaded: in every window of per_slots[o] consecutive slots
    # at most at_most[o] cars may need option o. Each slot holds exactly one car
    # type, so counting the (slot, type) pairs whose type needs the option counts
    # the cars needing it, without any auxiliary variable per slot and option.
    for o in range(n_options):
        needing = [t for t in range(n_types) if requires[t][o]]
        if not needing:
            continue  # no car type needs this option, so its station is never loaded
        for start in range(n_cars - per_slots[o] + 1):
            m &= (sum((sequence[s] == t)
                      for s in range(start, start + per_slots[o])
                      for t in needing) <= at_most[o])

    return m, {"sequence": sequence}
