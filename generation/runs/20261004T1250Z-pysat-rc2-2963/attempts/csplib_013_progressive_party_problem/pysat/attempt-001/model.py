# Progressive party problem (CSPLib 13): choose host boats and a visit
# schedule so that guest crews tour the hosts without overfilling any boat,
# revisiting a host or meeting another crew twice, using as few hosts as
# possible.
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n_boats = instance["n_boats"]
    n_periods = instance["n_periods"]
    capacity = instance["capacity"]
    crew_size = instance["crew_size"]
    boats = range(n_boats)
    periods = range(n_periods)

    pool = IDPool()
    # visits[p][b] is the boat whose deck boat b's crew is on in period p;
    # the domain is the boat indices. Direct encoding: every constraint below
    # talks about "crew b is on boat v", which is one literal of it.
    visits = [[Integer(f"visits_{p}_{b}", 0, n_boats - 1, vpool=pool)
               for b in boats] for p in periods]
    is_host = [pool.id(("is_host", b)) for b in boats]
    engine = IntegerEngine(vars=[x for row in visits for x in row], vpool=pool)

    def on(p, b, v):
        return visits[p][b].equals(v)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The crew of a host boat stays on board in every period.
    for b in boats:
        for p in periods:
            formula.append([-is_host[b], on(p, b, b)])

    # A boat that is not a host cannot be visited, not even by its own crew.
    for v in boats:
        for p in periods:
            for b in boats:
                formula.append([is_host[v], -on(p, b, v)])

    # The people aboard a boat in a period (host crew and guest crews) must
    # not exceed its capacity.
    for p in periods:
        for v in boats:
            formula.extend(PBEnc.leq(lits=[on(p, b, v) for b in boats],
                                     weights=crew_size, bound=capacity[v],
                                     vpool=pool).clauses)

    # A guest crew cannot visit the same host twice.
    for b in boats:
        for v in boats:
            for p in periods:
                for q in periods:
                    if p < q:
                        formula.append([is_host[b], -on(p, b, v), -on(q, b, v)])

    # Two crews cannot meet more than once: meet[p] is forced true whenever
    # both crews are on the same boat in period p, and at most one may be.
    for c1 in boats:
        for c2 in boats:
            if c1 >= c2:
                continue
            meet = [pool.id(("meet", p, c1, c2)) for p in periods]
            for p in periods:
                for v in boats:
                    formula.append([-on(p, c1, v), -on(p, c2, v), meet[p]])
            formula.extend(CardEnc.atmost(lits=meet, bound=1, vpool=pool,
                                          encoding=EncType.seqcounter).clauses)

    # Implied: every crew is aboard some host in each period, so the hosts'
    # capacities must together hold all crews. This follows from the
    # capacity constraint and helps RC2 refute too few hosts.
    formula.extend(PBEnc.geq(lits=is_host, weights=capacity,
                             bound=sum(crew_size), vpool=pool).clauses)

    # Minimise the number of host boats: each host pays 1.
    for b in boats:
        formula.append([-is_host[b]], weight=1)

    return formula, {"visits": visits, "is_host": is_host}
