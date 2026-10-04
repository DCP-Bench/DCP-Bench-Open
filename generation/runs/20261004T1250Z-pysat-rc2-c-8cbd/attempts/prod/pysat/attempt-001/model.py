# Production planning (ComplexOR "prod"): choose an integer quantity of each
# product, at most u[j], so that the time used, sum of X[j] / a[j], stays
# within b, maximising the profit sum of c[j] * X[j].
import math

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def build(instance):
    a = instance["a"]
    c = instance["c"]
    u = instance["u"]
    b = instance["b"]
    n = len(a)

    pool = IDPool()
    formula = WCNF()

    # x[j] is the quantity of product j, in the reference's domain 0..max(u).
    # Coupled encoding: the value literals are the output, the order
    # literals x[j] >= v state the sums below.
    top = max(max(u), 1)
    x = [Integer(f"x_{j}", 0, top, encoding="coupled", vpool=pool) for j in range(n)]
    for var in x:
        formula.extend(var.domain_clauses())

    # Each quantity is at most its upper bound u[j].
    for j in range(n):
        if u[j] < top:
            formula.append([-x[j].ge(max(u[j], 0) + 1)])

    # Time limit: sum of X[j] / a[j] <= b, multiplied through by the least
    # common multiple of the a[j] (as the reference does) to keep integer
    # weights. Each order literal x[j] >= v adds one unit of product j.
    lcm_a = math.lcm(*a)
    lits, weights = [], []
    for j in range(n):
        for v in range(1, top + 1):
            lits.append(x[j].ge(v))
            weights.append(lcm_a // a[j])
    formula.extend(PBEnc.leq(lits=lits, weights=weights, bound=b * lcm_a,
                             vpool=pool).clauses)

    # total_profit is a declared output: an Integer equal to sum c[j] * X[j].
    # Its domain runs over every profit the bounds u allow. On its order
    # literals total_profit = low + sum over k of [total_profit >= k], so the
    # equation is pseudo-Boolean.
    low = sum(min(0, c[j] * max(u[j], 0)) for j in range(n))
    high = sum(max(0, c[j] * max(u[j], 0)) for j in range(n))
    if high == low:
        high = low + 1
    total_profit = Integer("total_profit", low, high, encoding="coupled", vpool=pool)
    formula.extend(total_profit.domain_clauses())
    profit_lits = [x[j].ge(v) for j in range(n) for v in range(1, top + 1)]
    profit_weights = [c[j] for j in range(n) for v in range(1, top + 1)]
    order = [total_profit.ge(k) for k in range(low + 1, high + 1)]
    formula.extend(PBEnc.equals(lits=profit_lits + order,
                                weights=profit_weights + [-1] * len(order),
                                bound=low, vpool=pool,
                                encoding=EncType.bdd).clauses)

    # Maximise the profit: each unit of product j not made pays c[j], so RC2
    # minimises the shortfall from making every product at the domain top.
    # A product with a negative profit pays for each unit made instead.
    for j in range(n):
        for v in range(1, top + 1):
            if c[j] > 0:
                formula.append([x[j].ge(v)], weight=c[j])
            elif c[j] < 0:
                formula.append([-x[j].ge(v)], weight=-c[j])

    return formula, {"x": x, "total_profit": total_profit}
