# Car sequencing: arrange the cars on an assembly line so that no station
# (one per option) has to cope with more cars than it can handle in any
# window of consecutive slots.
import functools
import itertools
import math
import operator

from hermax.model import Model


def define(m, inputs, function):
    """A new literal that equals function(*inputs) for 0/1 inputs, as clauses."""
    out = m.bool()
    for values in itertools.product((0, 1), repeat=len(inputs)):
        clause = [~lit if value else lit for lit, value in zip(inputs, values)]
        clause.append(out if function(*values) else ~out)
        m &= functools.reduce(operator.or_, clause)
    return out


def literal_and(m, x, y):
    """x AND y for literals or the constants True / False."""
    if x is False or y is False:
        return False
    if x is True:
        return y
    if y is True:
        return x
    return define(m, [x, y], lambda a, b: a & b)


def literal_or(m, x, y):
    """x OR y for literals or the constants True / False."""
    if x is True or y is True:
        return True
    if x is False:
        return y
    if y is False:
        return x
    return define(m, [x, y], lambda a, b: a | b)


def require(m, literal):
    """Post a literal that may also be the constant True / False."""
    if literal is True:
        return
    if literal is False:
        flag = m.bool()  # the requirement can never hold
        m &= flag
        m &= ~flag
        return
    m &= literal


def forbid(m, literal):
    """Post the negation of a literal that may also be the constant True / False."""
    if literal is False:
        return
    if literal is True:
        require(m, False)
        return
    m &= ~literal


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
            for t in needing[o]:
                m &= (~slot[s][t] | flag)  # a type that needs the option sets it
            clause = ~flag
            for t in needing[o]:
                clause = clause | slot[s][t]  # ... and only such a type does
            m &= clause
            row.append(flag)
        needs.append(row)

    # No station is overloaded: in every window of per_slots[o] consecutive slots
    # at most at_most[o] cars need option o. "At most k of the window" is stated
    # by forbidding every set of k + 1 slots of the window from all needing the
    # option, one short clause per set, unless there are very many such sets.
    for o in range(n_options):
        window = per_slots[o]
        for start in range(n_cars - window + 1):
            flags = [needs[s][o] for s in range(start, start + window)]
            if at_most[o] >= window:
                continue  # the window can never be overloaded
            if math.comb(window, at_most[o] + 1) <= 300:
                for subset in itertools.combinations(flags, at_most[o] + 1):
                    m &= functools.reduce(operator.or_, [~f for f in subset])
            else:
                m &= (sum(flags) <= at_most[o])

    # Implied counting constraints, which follow from the demands and the windows
    # above and are stated because they let the solver see early that an
    # arrangement cannot be completed. Option o is needed by `total` cars. Any L
    # consecutive slots hold at most at_most * (L // per_slots) + min(at_most,
    # L % per_slots) of them (whole windows plus a remainder). So the first
    # `position` slots hold at most room(position) of them, and, since all `total`
    # must be placed, at least total - room(n_cars - position).
    # upto[s][k] says that at least k cars among slots 0..s need the option.
    def room(o, length):
        return at_most[o] * (length // per_slots[o]) + min(at_most[o], length % per_slots[o])

    for o in range(n_options):
        total = sum(demand[t] for t in needing[o])
        if total == 0:
            continue
        upto = []
        for s in range(n_cars):
            row = {}
            for k in range(1, min(total, s + 1) + 1):
                # at least k among slots 0..s: at least k among 0..s-1, or this
                # slot needs the option and at least k-1 among 0..s-1
                before_k = upto[s - 1].get(k, False) if s > 0 else False
                before_km1 = True if k == 1 else (upto[s - 1].get(k - 1, False) if s > 0 else False)
                row[k] = literal_or(m, before_k, literal_and(m, needs[s][o], before_km1))
            upto.append(row)
        for position in range(1, n_cars):
            counted = upto[position - 1]  # slots 0 .. position-1
            lowest = total - room(o, n_cars - position)
            if lowest > 0:
                require(m, counted.get(lowest, False))
            highest = room(o, position)
            if highest + 1 in counted:
                forbid(m, counted[highest + 1])

    return m, {"sequence": sequence}
