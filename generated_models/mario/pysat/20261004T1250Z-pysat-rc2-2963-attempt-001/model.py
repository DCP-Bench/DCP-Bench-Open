# Mario: plan a route from Mario's house to Luigi's house, visiting houses
# to collect as much gold as possible, without the fuel spent on the route
# exceeding the fuel limit.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    n = instance["nHouses"]
    mario = instance["marioHouse"]
    luigi = instance["luigiHouse"]
    fuel_limit = instance["fuelLimit"]
    arc_fuel = instance["arc_fuel"]
    gold = instance["goldInHouse"]
    houses = range(n)

    pool = IDPool()
    # s[i] is the house succeeding house i (s[i] = i when i is not on the
    # route), 0..n-1. Direct encoding: each value is one arc.
    s = [Integer(f"s_{i}", 0, n - 1, vpool=pool) for i in houses]
    # order[i] is the rank of house i in the tour, 1..n. Direct encoding:
    # ranks are compared one value at a time.
    order = [Integer(f"order_{i}", 1, n, vpool=pool) for i in houses]
    engine = IntegerEngine(vars=s + order, vpool=pool)

    # All houses are assigned distinct successors.
    engine.add_alldifferent(s)
    # All ranks are distinct.
    engine.add_alldifferent(order)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    def arc(i, j):
        return s[i].equals(j)

    # The tour starts at Mario's house, which has rank 1.
    formula.append([order[mario].equals(1)])

    # The path ends at Luigi's house, which loops back to Mario's house.
    formula.append([arc(luigi, mario)])

    for i in houses:
        # A house on the tour, other than the arc back to Mario's house, is
        # followed by a house of rank exactly one higher.
        for j in houses:
            if j == i or j == mario:
                continue
            for r in range(1, n):
                formula.append([-arc(i, j), -order[i].equals(r),
                                order[j].equals(r + 1)])
            formula.append([-arc(i, j), -order[i].equals(n)])
        # A house is either on the tour, or ranked after Luigi's house, so
        # houses off the tour cannot form ranked subtours of their own.
        for r in range(1, n + 1):
            for q in range(1, r + 1):
                formula.append([-arc(i, i), -order[luigi].equals(r),
                                -order[i].equals(q)])

    # The fuel spent on the arcs taken stays within the fuel limit.
    lits, weights = [], []
    for i in houses:
        for j in houses:
            if arc_fuel[i][j] != 0:
                lits.append(arc(i, j))
                weights.append(arc_fuel[i][j])
    if lits:
        formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=fuel_limit,
                                 vpool=pool).clauses)
    elif fuel_limit < 0:
        formula.append([])

    # Maximise the gold collected at the houses on the route: a house left
    # off the route (s[i] = i) pays its gold, so the cost is the shortfall
    # from the gold of all houses.
    for i in houses:
        if gold[i] > 0:
            formula.append([-arc(i, i)], weight=gold[i])
        elif gold[i] < 0:
            formula.append([arc(i, i)], weight=-gold[i])

    return formula, {"s": s}
