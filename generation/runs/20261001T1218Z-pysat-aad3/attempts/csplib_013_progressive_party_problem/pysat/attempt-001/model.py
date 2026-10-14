# Progressive party: some boats host and the other crews visit a host boat in each period,
# within capacity, never meeting another crew twice, using as few host boats as possible.
# PySAT only decides satisfiability, so the number of hosts is returned as the objective
# (the runner refuses a returned objective instead of ignoring it).
from itertools import combinations

from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]
    crew_size = instance["crew_size"]

    pool = IDPool()
    is_host = [pool.id(("host", b)) for b in range(n_boats)]
    # visits[p][c] = the boat that crew c is on during period p
    visits = [[Integer(f"visits{p}_{c}", 0, n_boats - 1, vpool=pool) for c in range(n_boats)]
              for p in range(n_periods)]
    engine = IntegerEngine(vars=[v for row in visits for v in row], vpool=pool)
    cnf = engine.clausify()
    on = lambda p, c, b: visits[p][c].equals(b)  # crew c is on boat b in period p

    # the crew of a host boat stays on its own boat
    for b in range(n_boats):
        for p in range(n_periods):
            cnf.append([-is_host[b], on(p, b, b)])
    # the people on a boat in one period never exceed its capacity
    for p in range(n_periods):
        for b in range(n_boats):
            cnf.extend(PBEnc.leq(lits=[on(p, c, b) for c in range(n_boats)], weights=crew_size,
                                 bound=capacity[b], vpool=pool).clauses)
    for b in range(n_boats):
        # a guest crew cannot visit the same boat twice
        for p, q in combinations(range(n_periods), 2):
            for v in range(n_boats):
                cnf.append([is_host[b], -on(p, b, v), -on(q, b, v)])
        # a boat that does not host cannot be visited
        for p in range(n_periods):
            for c in range(n_boats):
                cnf.append([is_host[b], -on(p, c, b)])
    # two crews are on the same boat in at most one period
    for c1, c2 in combinations(range(n_boats), 2):
        meet = []
        for p in range(n_periods):
            flag = pool.id(("meet", c1, c2, p))
            for b in range(n_boats):
                cnf.append([-on(p, c1, b), -on(p, c2, b), flag])
            meet.append(flag)
        cnf.extend(CardEnc.atmost(lits=meet, bound=1, vpool=pool, encoding=EncType.pairwise).clauses)

    return cnf, {"is_host": is_host, "visits": visits}, ("minimize", is_host)
