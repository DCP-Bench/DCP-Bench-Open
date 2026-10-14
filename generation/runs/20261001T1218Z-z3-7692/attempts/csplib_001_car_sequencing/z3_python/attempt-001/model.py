# Car sequencing: order the cars on an assembly line so that no option station
# is overloaded and every car type is built as often as demanded.
import z3


def build(instance):
    at_most = instance["at_most"]      # option o: at most at_most[o] cars ...
    per_slots = instance["per_slots"]  # ... in any window of per_slots[o] consecutive slots
    demand = instance["demand"]        # demand[t]: number of cars of type t
    requires = instance["requires"]    # requires[t][o] = 1 if type t needs option o

    n_cars = sum(demand)
    n_types = len(demand)
    n_options = len(at_most)

    # sequence[s] is the car type built in slot s (types are numbered from 0).
    sequence = [z3.Int(f"sequence_{s}") for s in range(n_cars)]
    # is_type[s][t] is true exactly when slot s holds a car of type t. Z3 has no
    # Element/Count, so the pseudo-Boolean constraints below work on these literals.
    is_type = [[z3.Bool(f"is_type_{s}_{t}") for t in range(n_types)] for s in range(n_cars)]

    solver = z3.Solver()

    # Each slot holds a car type in 0..n_types-1, and the Boolean literals agree
    # with the integer type of the slot.
    for s in range(n_cars):
        solver.add(sequence[s] >= 0, sequence[s] <= n_types - 1)
        for t in range(n_types):
            solver.add(is_type[s][t] == (sequence[s] == t))

    # The number of cars of each type in the sequence equals the demand for that type.
    for t in range(n_types):
        solver.add(z3.PbEq([(is_type[s][t], 1) for s in range(n_cars)], demand[t]))

    # Capacity of each option station: in any window of per_slots[o] consecutive
    # slots, at most at_most[o] cars may require option o.
    for o in range(n_options):
        needing = [t for t in range(n_types) if requires[t][o] == 1]
        if not needing:
            continue  # no car type needs this option, so its station is never loaded
        for start in range(n_cars - per_slots[o] + 1):
            window = [(is_type[s][t], 1)
                      for s in range(start, start + per_slots[o]) for t in needing]
            solver.add(z3.PbLe(window, at_most[o]))

    return solver, {"sequence": sequence}
