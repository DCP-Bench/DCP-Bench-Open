# Diet problem (hakank, diet1): buy whole units of four foods so that the
# diet meets the minimum calories, chocolate, sugar and fat requirements at
# the least total price, and report that price.
from math import gcd

from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


# Nutrient content of one unit of each food (chocolate cake, chocolate ice
# cream, cola, pineapple cheesecake). The reference fixes this table as part
# of the problem, not the instance, so it is mirrored here.
CALORIES = [400, 200, 150, 500]
CHOCOLATE = [3, 2, 0, 0]
SUGAR = [2, 2, 4, 4]
FAT = [2, 4, 1, 5]

# The reference declares cost in 0..1000, so a diet above 1000 is not allowed.
MAX_COST = 1000


def build(instance):
    n = instance["n"]
    price = instance["price"]
    limits = instance["limits"]
    contents = [CALORIES, CHOCOLATE, SUGAR, FAT]

    pool = IDPool()

    # x[i] is the number of units of food i. The reference allows up to
    # 10000; an optimal diet never buys more of a food than it would take to
    # meet, on its own, every requirement it contributes to (one unit less
    # would still meet them all, for less), so that bounds the domain. Order
    # encoding: the domains are a dozen values and the constraints are sums.
    x = []
    for i in range(n):
        enough = [-(-limits[j] // contents[j][i]) for j in range(len(contents))
                  if contents[j][i] > 0]
        top = max(enough + [1])
        x.append(Integer(f"x_{i}", 0, top, encoding="order", vpool=pool))

    # cost is the declared output. Every price total is a multiple of the
    # common divisor of the prices, so the sum is stated over units of it
    # (100 values instead of 1000 on the example), then scaled back below.
    unit = 0
    for p in price:
        unit = gcd(unit, p)
    unit = unit or 1
    units = Integer("cost_units", 0, max(MAX_COST // unit, 1),
                    encoding="coupled", vpool=pool)

    engine = IntegerEngine(vars=x + [units], vpool=pool)

    # Each nutrient requirement is met (at least the limit).
    for j, content in enumerate(contents):
        engine.add_linear(sum(content[i] * x[i] for i in range(n)) >= limits[j])

    # units is the total price of the diet in units.
    engine.add_linear(sum((price[i] // unit) * x[i] for i in range(n)) - units == 0)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # cost = unit * units, within the reference's 0..MAX_COST: cost >= v
    # exactly when units >= ceil(v / unit). The direct literals of the coupled
    # encoding are what the runner reads the value from.
    cost = Integer("cost", 0, MAX_COST, encoding="coupled", vpool=pool)
    formula.extend(cost.domain_clauses())
    for v in range(1, MAX_COST + 1):
        k = -(-v // unit)
        if k <= units.ub:
            formula.append([-cost.ge(v), units.ge(k)])
            formula.append([cost.ge(v), -units.ge(k)])
        else:
            formula.append([-cost.ge(v)])
    if MAX_COST // unit + 1 <= units.ub:
        formula.append([-units.ge(MAX_COST // unit + 1)])

    # Minimise the price: every unit of food i bought pays price[i].
    for i in range(n):
        if price[i] > 0:
            for v in range(1, x[i].ub + 1):
                formula.append([-x[i].ge(v)], weight=price[i])

    return formula, {"cost": cost}
