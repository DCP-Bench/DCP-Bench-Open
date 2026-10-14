# Car sequencing: put the cars of the demanded types into an assembly-line order so that
# no option station sees more than its allowed number of cars in any window of consecutive slots.
from exact import Exact


def build(instance):
    at_most = instance["at_most"]  # option o may appear at most at_most[o] times ...
    per_slots = instance["per_slots"]  # ... in any window of per_slots[o] consecutive slots
    demand = instance["demand"]  # number of cars wanted of each type
    requires = instance["requires"]  # requires[t][o] = 1 if a car of type t needs option o
    n_types = len(demand)
    n_options = len(at_most)
    n_cars = sum(demand)  # one slot per car to build

    solver = Exact()

    # is_type[s][t] = 1 when slot s holds a car of type t. Exact has no all-different or
    # element constraint, so the type of a slot is chosen through these 0/1 indicators.
    is_type = [[f"slot_{s}_is_type_{t}" for t in range(n_types)] for s in range(n_cars)]
    for s in range(n_cars):
        for t in range(n_types):
            solver.addVariable(is_type[s][t], 0, 1)
        # every slot gets exactly one car type
        solver.addConstraint([(1, is_type[s][t]) for t in range(n_types)], True, 1, True, 1)

    # sequence[s] is the car type in slot s (domain: the types 0..n_types-1), tied to the indicators
    sequence = [f"sequence_{s}" for s in range(n_cars)]
    for s in range(n_cars):
        solver.addVariable(sequence[s], 0, n_types - 1)
        solver.addConstraint([(t, is_type[s][t]) for t in range(1, n_types)] + [(-1, sequence[s])],
                             True, 0, True, 0)

    # the number of cars of each type in the sequence equals the demand for that type
    for t in range(n_types):
        solver.addConstraint([(1, is_type[s][t]) for s in range(n_cars)], True, demand[t], True, demand[t])

    # capacity of each option station: among any per_slots[o] consecutive slots, at most
    # at_most[o] cars may require option o
    for o in range(n_options):
        needing = [t for t in range(n_types) if requires[t][o]]
        if not needing:
            continue  # no car type needs this option, so its station is never loaded
        for start in range(n_cars - per_slots[o] + 1):
            window = range(start, start + per_slots[o])
            solver.addConstraint([(1, is_type[s][t]) for s in window for t in needing],
                                 False, 0, True, at_most[o])

    return solver, {"sequence": sequence}
