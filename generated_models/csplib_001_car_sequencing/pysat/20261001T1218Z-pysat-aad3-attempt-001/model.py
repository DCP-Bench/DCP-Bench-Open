# Car sequencing: order the cars on an assembly line so that every option's
# station copes with its load, i.e. among any per_slots[o] consecutive cars at
# most at_most[o] need option o, while each car type is built as often as demanded.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    at_most = instance["at_most"]      # a station can cope with at most this many cars ...
    per_slots = instance["per_slots"]  # ... in any window of this many consecutive slots
    demand = instance["demand"]        # number of cars wanted of each type
    requires = instance["requires"]    # requires[t][o] = 1 if type t needs option o
    n_cars = sum(demand)               # one slot per car to build
    n_types = len(demand)
    n_options = len(at_most)

    pool = IDPool()
    # sequence[s] = the type of the car in slot s (types are numbered from 0).
    # The direct encoding gives one literal per (slot, type): sequence[s].equals(t)
    # is true exactly when slot s holds a car of type t, and exactly one is true.
    sequence = [Integer(f"sequence{s}", 0, n_types - 1, vpool=pool) for s in range(n_cars)]
    engine = IntegerEngine(vars=sequence, vpool=pool)
    cnf = engine.clausify()
    is_type = [[sequence[s].equals(t) for t in range(n_types)] for s in range(n_cars)]

    # the number of cars of each type in the sequence equals the demand for that type
    for t in range(n_types):
        cnf.extend(CardEnc.equals(lits=[is_type[s][t] for s in range(n_cars)], bound=demand[t],
                                  vpool=pool, encoding=EncType.totalizer).clauses)

    for o in range(n_options):
        # needs[s] is true when the car in slot s requires option o: it is true exactly
        # when the slot holds one of the car types whose requires row has a 1 for o
        needing = [t for t in range(n_types) if requires[t][o]]
        needs = []
        for s in range(n_cars):
            lit = pool.id(("needs", s, o))
            for t in needing:
                cnf.append([-is_type[s][t], lit])
            cnf.append([-lit] + [is_type[s][t] for t in needing])
            needs.append(lit)
        # the station for option o is never overloaded: in every window of
        # per_slots[o] consecutive slots at most at_most[o] cars need the option
        for start in range(n_cars - per_slots[o] + 1):
            window = needs[start:start + per_slots[o]]
            if len(window) <= at_most[o]:
                continue  # the window cannot be overloaded
            cnf.extend(CardEnc.atmost(lits=window, bound=at_most[o], vpool=pool,
                                      encoding=EncType.seqcounter).clauses)

    return cnf, {"sequence": sequence}
