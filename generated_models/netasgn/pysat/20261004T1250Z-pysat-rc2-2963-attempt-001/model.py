# Project assignment (netasgn): decide how many hours each person works on
# each project, using up every person's supply and meeting every project's
# demand within per-pair limits, at minimum total cost.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    supply = instance["supply"]
    demand = instance["demand"]
    cost = instance["cost"]
    limit = instance["limit"]
    people = range(len(supply))
    projects = range(len(demand))

    pool = IDPool()
    # assign[i][j] is the hours person i works on project j. The reference
    # gives it the domain 0..10 and requires assign <= limit, so the upper
    # bound is the smaller of 10 and the limit. Coupled encoding: thresholds
    # for the sums and the cost, value literals for the runner to block a
    # reported answer.
    top = [[min(10, limit[i][j]) for j in projects] for i in people]
    infeasible = any(top[i][j] < 0 for i in people for j in projects)
    assign = [[Integer(f"assign_{i}_{j}", 0, max(top[i][j], 0),
                       encoding="coupled", vpool=pool)
               for j in projects] for i in people]
    cells = [(i, j) for i in people for j in projects]

    # total_cost ranges over every cell at 0 or at its upper bound.
    low = sum(min(cost[i][j] * max(top[i][j], 0), 0) for i, j in cells)
    high = sum(max(cost[i][j] * max(top[i][j], 0), 0) for i, j in cells)
    total_cost = Integer("total_cost", low, high, vpool=pool)
    engine = IntegerEngine(vars=[assign[i][j] for i, j in cells] + [total_cost],
                           vpool=pool)

    # The hours assigned from each person equal that person's supply.
    for i in people:
        engine.add_linear(sum(assign[i][j] for j in projects) == supply[i])
    # The hours assigned to each project equal its demand.
    for j in projects:
        engine.add_linear(sum(assign[i][j] for i in people) == demand[j])

    formula = WCNF()
    formula.extend(engine.clausify().clauses)
    if infeasible:
        # A negative limit leaves no admissible number of hours.
        formula.append([])

    # total_cost = sum(cost * assign). Its value above `low` is written in
    # binary digits, so the equation is one pseudo-Boolean constraint over
    # the hour thresholds and a few weighted bits, rather than over every
    # one of the many threshold literals total_cost would have. A negative
    # cost c is written as |c| on the negated threshold, which moves `low`
    # to the other side and keeps the bound at 0, as PBEnc requires.
    lits, weights = [], []
    for i, j in cells:
        c = cost[i][j]
        for v in range(1, max(top[i][j], 0) + 1):
            if c > 0:
                lits.append(assign[i][j].ge(v))
                weights.append(c)
            elif c < 0:
                lits.append(-assign[i][j].ge(v))
                weights.append(-c)
    width = max(high - low, 0).bit_length()
    bits = [pool.id(("total_bit", b)) for b in range(width)]
    if lits or bits:
        formula.extend(PBEnc.equals(lits=lits + bits,
                                    weights=weights + [-(1 << b) for b in range(width)],
                                    bound=0, vpool=pool).clauses)
    # Each value of total_cost fixes its binary digits.
    for value in range(low, high + 1):
        for b in range(width):
            on = (value - low) >> b & 1
            formula.append([-total_cost.equals(value), bits[b] if on else -bits[b]])

    # Minimise the total cost: every hour person i works on project j pays
    # cost[i][j] (a negative cost pays its magnitude for every hour not
    # worked, a constant shift).
    for i, j in cells:
        c = cost[i][j]
        for v in range(1, max(top[i][j], 0) + 1):
            if c > 0:
                formula.append([-assign[i][j].ge(v)], weight=c)
            elif c < 0:
                formula.append([assign[i][j].ge(v)], weight=-c)

    return formula, {"assign": assign, "total_cost": total_cost}
