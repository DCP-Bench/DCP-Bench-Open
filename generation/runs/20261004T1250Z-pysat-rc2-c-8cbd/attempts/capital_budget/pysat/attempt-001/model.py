# Capital budgeting (Winston): choose which investments to make so that their
# cash outflow stays within the budget and their total net present value
# (NPV) is as large as possible.
from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer
from pysat.pb import EncType, PBEnc


def build(instance):
    budget = instance["budget"]
    npv = instance["npv"]
    cash_flow = instance["cash_flow"]
    n = len(npv)

    pool = IDPool()
    formula = WCNF()

    # x[i] is true when investment i is chosen.
    x = [pool.id(("x", i)) for i in range(n)]

    # The cash outflow of the chosen investments must not exceed the budget.
    formula.extend(PBEnc.leq(lits=x, weights=cash_flow, bound=budget,
                             vpool=pool).clauses)

    # z, the total NPV, is a declared output, so it is an Integer tied to the
    # NPV of the chosen investments. Its range 0..sum(npv) is the reference's.
    # Every total is a multiple of the common divisor of the NPVs, so the sum
    # is stated over "units" of that divisor: units = sum of npv[i]/unit over
    # the chosen investments, a narrow integer (a few hundred values on the
    # instances here) where a sum over the raw values would need hundreds of
    # thousands of literals.
    unit = 0
    for v in npv:
        unit = gcd(unit, v)
    unit = unit or 1
    steps = [v // unit for v in npv]
    top = sum(steps)
    units = Integer("npv_units", 0, max(top, 1), encoding="coupled", vpool=pool)
    formula.extend(units.domain_clauses())
    # units equals the chosen investments' NPV in units: on its order literals
    # units = sum over k of [units >= k], so the equation is pseudo-Boolean.
    order = [units.ge(k) for k in range(1, max(top, 1) + 1)]
    formula.extend(PBEnc.equals(lits=x + order,
                                weights=steps + [-1] * len(order), bound=0,
                                vpool=pool, encoding=EncType.bdd).clauses)

    # z takes the value unit * units. Its value literals are channelled to
    # those of units, and a value that is not a multiple of the unit is
    # impossible; together these leave exactly one value true, so z needs no
    # exactly-one constraint of its own.
    z = Integer("z", 0, unit * max(top, 1), vpool=pool)
    for v in range(0, unit * max(top, 1) + 1):
        if v % unit == 0:
            formula.append([-z.equals(v), units.equals(v // unit)])
            formula.append([z.equals(v), -units.equals(v // unit)])
        else:
            formula.append([-z.equals(v)])

    # Maximise the NPV: leaving investment i out pays npv[i], so RC2 minimises
    # the shortfall from the NPV of choosing every investment.
    for i in range(n):
        if npv[i] > 0:
            formula.append([x[i]], weight=npv[i])

    return formula, {"x": x, "z": z}
