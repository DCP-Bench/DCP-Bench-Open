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

    # is_type[s][t] is true exactly when slot s holds a car of type t (types are numbered
    # from 0). The model is purely Boolean, with pseudo-Boolean constraints for the
    # counts, because Z3 has no Element/Count and its integer reasoning is much slower
    # on this problem than its Boolean search.
    is_type = [[z3.Bool(f"is_type_{s}_{t}") for t in range(n_types)] for s in range(n_cars)]
    # setup[s][o] is true when the car in slot s needs option o.
    setup = [[z3.Bool(f"setup_{s}_{o}") for o in range(n_options)] for s in range(n_cars)]

    solver = z3.Solver()

    # Each slot holds exactly one car type.
    for s in range(n_cars):
        solver.add(z3.PbEq([(is_type[s][t], 1) for t in range(n_types)], 1))

    # The options of a slot are those of the car type placed in it.
    for s in range(n_cars):
        for o in range(n_options):
            needing = [is_type[s][t] for t in range(n_types) if requires[t][o] == 1]
            solver.add(setup[s][o] == (z3.Or(needing) if needing else z3.BoolVal(False)))

    # The number of cars of each type in the sequence equals the demand for that type.
    for t in range(n_types):
        solver.add(z3.PbEq([(is_type[s][t], 1) for s in range(n_cars)], demand[t]))

    # Capacity of each option station: in any window of per_slots[o] consecutive
    # slots, at most at_most[o] cars may require option o.
    for o in range(n_options):
        for start in range(n_cars - per_slots[o] + 1):
            window = [(setup[s][o], 1) for s in range(start, start + per_slots[o])]
            solver.add(z3.PbLe(window, at_most[o]))

    # Implied constraints that tighten the search (they follow from the groups above).
    # With p = at_most[o] and q = per_slots[o], any r consecutive slots hold at most
    # (r // q) * p + min(p, r % q) cars needing option o (full windows of q slots, plus
    # a shorter rest). That caps the first r slots, and, with total_o the number of cars
    # needing option o, forces the first n_cars - r slots to hold the cars the last r
    # slots cannot take.
    for o in range(n_options):
        total = sum(demand[t] for t in range(n_types) if requires[t][o] == 1)
        p, q = at_most[o], per_slots[o]
        if n_cars < q:
            continue  # the line is shorter than one window, so no window rule applies
        for r in range(1, n_cars):
            room = (r // q) * p + min(p, r % q)
            solver.add(z3.PbLe([(setup[s][o], 1) for s in range(r)], room))
            if total - room > 0:
                solver.add(z3.PbGe([(setup[s][o], 1) for s in range(n_cars - r)], total - room))

    # sequence[s] is the car type built in slot s: the type whose Boolean is true.
    sequence = []
    for s in range(n_cars):
        value = z3.IntVal(n_types - 1)
        for t in range(n_types - 2, -1, -1):
            value = z3.If(is_type[s][t], t, value)
        sequence.append(value)

    return solver, {"sequence": sequence}
