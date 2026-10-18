# Car sequencing (CSPLib 001): a number of cars of several types are put in a
# sequence on an assembly line. Each option station may handle at most at_most[o]
# of the cars in any window of per_slots[o] consecutive positions, so the cars that
# require an option must not be bunched together. Output: the car type at each
# position, 0-based.
#
# Encoding: a one-hot Boolean per position and type, a Boolean need[p][o] per
# position and option, and the station capacities written as clauses. A window of
# w positions holds at most k cars needing option o exactly when no k+1 of its
# positions all need o, so each window gives one clause per (k+1)-subset.
# Demands are Boolean sequential counters written as clauses, and each option also
# gets a counter with the capacity bounds that follow from the windows (implied rows).
from itertools import combinations

import cvc5.pythonic as cz


def _or(lits):
    # cvc5 needs at least two arguments for Or; a single literal stands for itself.
    if len(lits) == 1:
        return lits[0]
    return cz.Or(lits)


def _counter(constraints, lits, top, name):
    """Boolean sequential counter. pref[p][j] (1 <= j <= min(p, top)) is true exactly
    when at least j of the first p literals are true; missing entries are false."""
    pref = [{}]
    for p in range(1, len(lits) + 1):
        prev = pref[-1]
        cur = {}
        lit = lits[p - 1]
        for j in range(1, min(p, top) + 1):
            v = cz.Bool(f"{name}_{p}_{j}")
            cur[j] = v
            # v <-> prev[j] or (lit and prev[j-1]), written as clauses
            nv = cz.Not(v)
            a = prev.get(j)
            b = prev.get(j - 1) if j > 1 else None
            constraints.append(_or([nv, a, lit]) if a is not None else _or([nv, lit]))
            if a is not None:
                constraints.append(cz.Or(cz.Not(a), v))
            if j == 1:
                constraints.append(cz.Or(cz.Not(lit), v))
            else:
                if a is not None and b is not None:
                    constraints.append(_or([nv, a, b]))
                elif a is None and b is not None:
                    constraints.append(_or([nv, b]))
                elif a is None and b is None:
                    constraints.append(nv)
                if b is not None:
                    constraints.append(_or([cz.Not(lit), cz.Not(b), v]))
        pref.append(cur)
    return pref


def build(instance):
    demand = instance["demand"]          # number of cars of each type
    requires = instance["requires"]      # requires[type][option] = 1 if the car needs the option
    at_most = instance["at_most"]        # station capacity for each option
    per_slots = instance["per_slots"]    # window length for each option

    n_types = len(demand)
    n_opts = len(at_most)
    # The line length is the total number of cars to produce.
    n_cars = sum(demand)

    # x[p][c] is true when position p carries a car of type c.
    x = [[cz.Bool(f"x_{p}_{c}") for c in range(n_types)] for p in range(n_cars)]
    # need[p][o] is true when the car at position p requires option o.
    need = [[cz.Bool(f"need_{p}_{o}") for o in range(n_opts)] for p in range(n_cars)]

    constraints = []

    # Each position holds exactly one car type.
    for p in range(n_cars):
        constraints.append(_or(x[p]))
        for c in range(n_types):
            for d in range(c + 1, n_types):
                constraints.append(cz.Or(cz.Not(x[p][c]), cz.Not(x[p][d])))

    # The number of cars of each type is its demand: a Boolean counter over the
    # positions reaches the demand and not one more.
    for c in range(n_types):
        d = demand[c]
        pref = _counter(constraints, [x[p][c] for p in range(n_cars)], d + 1, f"dem_{c}")
        if d == 0:
            constraints.extend(cz.Not(x[p][c]) for p in range(n_cars))
            continue
        constraints.append(pref[n_cars][d])
        if (d + 1) in pref[n_cars]:
            constraints.append(cz.Not(pref[n_cars][d + 1]))

    # A position needs option o exactly when its car type requires o.
    for p in range(n_cars):
        for o in range(n_opts):
            types_needing_o = [c for c in range(n_types) if requires[c][o] == 1]
            if types_needing_o:
                constraints.append(need[p][o] == _or([x[p][c] for c in types_needing_o]))
            else:
                constraints.append(cz.Not(need[p][o]))

    # Station capacity: in every window of per_slots[o] consecutive positions, at
    # most at_most[o] cars require option o. Equivalently, no at_most[o]+1 positions
    # of the window all require it, so each such set gives one clause.
    for o in range(n_opts):
        w = per_slots[o]
        k = at_most[o]
        if k + 1 > w:
            continue
        for start in range(n_cars - w + 1):
            window = range(start, start + w)
            for subset in combinations(window, k + 1):
                constraints.append(_or([cz.Not(need[p][o]) for p in subset]))

    # Implied capacity bounds (follow from the station windows): any m consecutive
    # positions hold at most cap(m) = (m // w) * k + min(k, m % w) cars needing
    # option o. The demand fixes how many cars need o in total, so the first n - m
    # positions hold at least total_o - cap(m) of them, and the first m at most cap(m).
    for o in range(n_opts):
        w = per_slots[o]
        k = at_most[o]
        total_o = sum(demand[c] for c in range(n_types) if requires[c][o] == 1)
        pref = _counter(constraints, [need[p][o] for p in range(n_cars)], total_o + 1, f"opt_{o}")
        if total_o > 0:
            constraints.append(pref[n_cars][total_o])
        if (total_o + 1) in pref[n_cars]:
            constraints.append(cz.Not(pref[n_cars][total_o + 1]))
        for m in range(1, n_cars + 1):
            cap = (m // w) * k + min(k, m % w)
            if (cap + 1) in pref[m]:
                constraints.append(cz.Not(pref[m][cap + 1]))
            low = total_o - cap
            if low > 0 and (n_cars - m) >= 1:
                if low in pref[n_cars - m]:
                    constraints.append(pref[n_cars - m][low])
                else:
                    constraints.append(cz.BoolVal(False))

    # Output: the car type at each position.
    sequence = [
        cz.Sum([cz.If(x[p][c], c, 0) for c in range(n_types)]) for p in range(n_cars)
    ]
    solver = cz.SolverFor("QF_LIA")
    solver.add(*constraints)
    return solver, {"sequence": sequence}
