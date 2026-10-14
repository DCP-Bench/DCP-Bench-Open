# Coins: choose how many coins of each denomination to carry, as few coins as
# possible in all, so that every amount from 1 up to one less than the maximum
# amount to pay can be paid exactly with some of those coins.
from hermax.model import Model


def build(instance):
    denominations = instance["denominations"]  # value of each kind of coin
    limit = instance["max_amount_to_pay"]  # amounts 1 .. limit-1 must be payable
    n = len(denominations)

    m = Model()
    # x[i] = number of coins carried of denomination i. Paying an amount below
    # `limit` never needs more than (limit - 1) // value coins of one kind, and
    # carrying more only costs more, so this is the largest number worth
    # considering; it bounds the domain.
    x = [m.int(f"x_{i}", 0, max(1, (limit - 1) // denominations[i])) for i in range(n)]

    # Every amount from 1 to limit-1 can be paid exactly with coins from those
    # carried. reach[i][v] is true only if the amount v can be made from the
    # first i denominations, using no more of each than carried. Only the
    # "true implies it can really be made" direction is posted, which is enough
    # because the payable amounts below only demand that entries are true.
    reach = [m.bool_vector(f"reach_{i}", limit) for i in range(n + 1)]
    # with no denominations, only the amount 0 can be made
    m &= reach[0][0]
    for v in range(1, limit):
        m &= ~reach[0][v]

    for i in range(n):
        value = denominations[i]
        for v in range(limit):
            # reach[i+1][v] needs a reason: no coin of denomination i is used, or
            # k >= 1 of them are used, are carried, and the rest of v can be made
            reasons = [reach[i][v]]
            for k in range(1, v // value + 1):
                used = m.bool(f"used_{i}_{v}_{k}")
                m &= (~used | (x[i] >= k))
                m &= (~used | reach[i][v - k * value])
                reasons.append(used)
            clause = ~reach[i + 1][v]
            for reason in reasons:
                clause = clause | reason
            m &= clause

    for amount in range(1, limit):
        m &= reach[n][amount]

    # Minimise the number of coins carried: each coin of a kind, counted by
    # x[i] >= k, pays one. A soft clause pays when its literal is false, so the
    # literal is the negation of "at least k coins of this kind".
    for i in range(n):
        for k in range(1, x[i].ub + 1):
            m.obj[1] += ~(x[i] >= k)

    return m, {"x": x}
