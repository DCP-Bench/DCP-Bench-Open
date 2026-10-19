# Car sequencing (CSPLib 001): order cars of several types on an assembly line so
# that each option station is never asked to handle more than its capacity in any
# window of consecutive positions. Output: the car type at each position.
# Encoding: capacity windows are written as differences of running counts, which
# keeps every linear row to two terms (a per-option prefix count).
import cvc5.pythonic as cz


def _or(lits):
    # cvc5 needs at least two arguments for Or.
    if len(lits) == 1:
        return lits[0]
    return cz.Or(lits)


def build(instance):
    demand = instance["demand"]          # number of cars of each type
    requires = instance["requires"]      # requires[type][option] = 1 if the car needs the option
    at_most = instance["at_most"]        # station capacity for each option
    per_slots = instance["per_slots"]    # window length for each option

    n_types = len(demand)
    n_opts = len(at_most)
    n_cars = sum(demand)                 # the line length is the total number of cars

    # x[p][c] is true when position p carries a car of type c.
    x = [[cz.Bool(f"x_{p}_{c}") for c in range(n_types)] for p in range(n_cars)]
    # need[p][o] is true when the car at position p requires option o.
    need = [[cz.Bool(f"need_{p}_{o}") for o in range(n_opts)] for p in range(n_cars)]
    # cnt[o][p] counts the cars among positions 0..p-1 that require option o.
    cnt = [[cz.Int(f"cnt_{o}_{p}") for p in range(n_cars + 1)] for o in range(n_opts)]

    constraints = []

    # Each position holds exactly one car type.
    for p in range(n_cars):
        constraints.append(_or(x[p]))
        for c in range(n_types):
            for d in range(c + 1, n_types):
                constraints.append(cz.Or(cz.Not(x[p][c]), cz.Not(x[p][d])))

    # The number of cars of each type is its demand.
    for c in range(n_types):
        constraints.append(
            cz.Sum([cz.If(x[p][c], 1, 0) for p in range(n_cars)]) == demand[c]
        )

    # A position needs option o exactly when its car type requires o.
    for p in range(n_cars):
        for o in range(n_opts):
            types_needing_o = [c for c in range(n_types) if requires[c][o] == 1]
            if types_needing_o:
                constraints.append(need[p][o] == _or([x[p][c] for c in types_needing_o]))
            else:
                constraints.append(cz.Not(need[p][o]))

    # Running counts per option: cnt[o][0] = 0 and each step adds the position's need.
    for o in range(n_opts):
        constraints.append(cnt[o][0] == 0)
        for p in range(n_cars):
            constraints.append(cnt[o][p + 1] == cnt[o][p] + cz.If(need[p][o], 1, 0))

    # Station capacity: in every window of per_slots[o] consecutive positions,
    # at most at_most[o] cars require option o. A window is the difference of two
    # running counts.
    for o in range(n_opts):
        w = per_slots[o]
        for start in range(n_cars - w + 1):
            constraints.append(cnt[o][start + w] - cnt[o][start] <= at_most[o])

    # Output: the car type at each position.
    sequence = [
        cz.Sum([cz.If(x[p][c], c, 0) for c in range(n_types)]) for p in range(n_cars)
    ]
    solver = cz.SolverFor("QF_LIA")
    solver.add(*constraints)
    return solver, {"sequence": sequence}
