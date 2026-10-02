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
    # slot[s][t] = the car in slot s is of type t: the same choice as `sequence`
    # in one-hot form, which the counting below works on
    slot = [m.bool_vector(f"slot_{s}", n_types) for s in range(n_cars)]
    for s in range(n_cars):
        m &= slot[s].exactly_one()
        for t in range(n_types):
            m &= (~slot[s][t] | (sequence[s] == t))
            m &= (slot[s][t] | ~(sequence[s] == t))

    # the number of cars of each type in the sequence equals its demand
    for t in range(n_types):
        m &= (sum(slot[s][t] for s in range(n_cars)) == demand[t])

    # needs[s][o] says the car in slot s needs option o. It is true exactly when
    # the car's type is one of the types that need the option.
    needing = [[t for t in range(n_types) if requires[t][o]] for o in range(n_options)]
    needs = []
    for s in range(n_cars):
        row = []
        for o in range(n_options):
            flag = m.bool(f"needs_{s}_{o}")
            for t in range(n_types):
                if requires[t][o]:
                    m &= (~slot[s][t] | flag)  # a type that needs the option sets it
            if needing[o]:
                clause = ~flag
                for t in needing[o]:
                    clause = clause | slot[s][t]  # ... and only such a type does
                m &= clause
            else:
                m &= ~flag
            row.append(flag)
        needs.append(row)

    # No station is overloaded: in every window of per_slots[o] consecutive slots
    # at most at_most[o] cars need option o.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            m &= (sum(needs[s][o] for s in range(start, start + per_slots[o])) <= at_most[o])

    # Implied counting constraints, which follow from the demands and the windows
    # above and are stated because they let the solver see early that an
    # arrangement cannot be completed. Option o is needed by `total` cars. Any L
    # consecutive slots hold at most at_most * (L // per_slots) + min(at_most,
    # L % per_slots) of them (whole windows plus a remainder), so the slots before
    # a position must hold the rest, and so must the slots after it.
    for o in range(n_options):
        total = sum(demand[t] for t in needing[o])
        for position in range(1, n_cars):
            def room(length):
                return at_most[o] * (length // per_slots[o]) + min(at_most[o], length % per_slots[o])
            before_needed = total - room(n_cars - position)  # slots 0 .. position-1
            if before_needed > 0:
                m &= (sum(needs[s][o] for s in range(position)) >= before_needed)
            after_needed = total - room(position)  # slots position .. n_cars-1
            if after_needed > 0:
                m &= (sum(needs[s][o] for s in range(position, n_cars)) >= after_needed)

    return m, {"sequence": sequence}
