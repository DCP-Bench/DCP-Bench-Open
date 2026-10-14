"""Fancy dress: Mr Greenguest must follow Mr Greenfan's rules on green tie, shirt, hat and
socks, or pay an $11 entrance fee. He owns a green shirt and can buy a tie ($10), a used
hat ($2) and socks ($12). Find his cheapest way to participate.

The model reports 0/1 for tie (t), hat (h), shirt (r), socks (s) and entrance fee (n).
"""
import pulp


def build(instance):
    del instance  # the puzzle has no instance data; its prices are below

    problem = pulp.LpProblem("fancy_dress", pulp.LpMinimize)

    t = pulp.LpVariable("t", cat="Binary")  # wears a green tie
    h = pulp.LpVariable("h", cat="Binary")  # wears a green hat
    r = pulp.LpVariable("r", cat="Binary")  # wears a green shirt
    s = pulp.LpVariable("s", cat="Binary")  # wears green socks
    n = pulp.LpVariable("n", cat="Binary")  # pays the entrance fee

    # 1. whoever wears a green tie has to wear a green shirt, or pays the fee
    problem += t <= r + n
    # 2. green socks or a green shirt only with a green tie or a green hat, or pay the fee
    problem += s <= t + h + n
    problem += r <= t + h + n
    # 3. whoever wears a green shirt or a green hat, or no green socks, must wear a green
    #    tie, or pays the fee
    problem += r <= t + n
    problem += h <= t + n
    problem += 1 - s <= t + n

    # the cost: tie $10, hat $2, socks $12, entrance fee $11 (0..100 as in the reference)
    cost = pulp.LpVariable("cost", 0, 100, cat="Integer")
    problem += cost == 10 * t + 2 * h + 12 * s + 11 * n

    # minimize the cost
    problem += cost

    return problem, {"t": t, "h": h, "r": r, "s": s, "n": n}
