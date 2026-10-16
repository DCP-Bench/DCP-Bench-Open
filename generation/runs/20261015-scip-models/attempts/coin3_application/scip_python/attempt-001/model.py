# Coin problem: choose the fewest coins, from a given set of denominations, such that
# every amount smaller than a given maximum amount can be paid exactly with them.
from pyscipopt import Model, quicksum


def build(instance):
    denoms = instance["denominations"]
    max_amount = instance["max_amount_to_pay"]
    amounts = range(1, max_amount)  # every amount smaller than the maximum
    k = len(denoms)

    m = Model()

    # x[i] = number of coins of denomination i that are bought.
    # Paying an amount below max_amount never needs more than (max_amount - 1) // d coins of
    # denomination d, so that is the upper bound on x[i].
    x = [m.addVar(name=f"x[{i}]", vtype="I", lb=0, ub=(max_amount - 1) // denoms[i])
         for i in range(k)]

    # pay[v, i] = number of coins of denomination i used to pay the amount v.
    # Each pay[v, i] is at most the number of coins bought, so it is bounded by x[i].
    pay = {}
    for v in amounts:
        for i in range(k):
            pay[v, i] = m.addVar(name=f"pay[{v},{i}]", vtype="I", lb=0,
                                 ub=min(v // denoms[i], (max_amount - 1) // denoms[i]))

    # the coins used to pay an amount must add up to exactly that amount
    for v in amounts:
        # the amount v is paid exactly with the coins used for it
        m.addCons(quicksum(denoms[i] * pay[v, i] for i in range(k)) == v)

    # no more coins are used for an amount than were bought
    for v in amounts:
        for i in range(k):
            # coins of denomination i used for amount v are among the coins bought
            m.addCons(pay[v, i] <= x[i])

    # minimise the total number of coins bought
    m.setObjective(quicksum(x), "minimize")

    return m, {"x": x}
