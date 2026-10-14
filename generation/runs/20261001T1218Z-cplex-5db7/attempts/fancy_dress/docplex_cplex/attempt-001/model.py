"""Fancy dress: Mr Greenguest owns a green shirt and can buy a green tie ($10), hat ($2) and
socks ($12), or pay an $11 entrance fee if not dressed by the rules. Find his cheapest way in.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data; the rules and prices are from the statement.
    model = Model("fancy_dress")

    t = model.binary_var(name="t")  # wears a green tie
    h = model.binary_var(name="h")  # wears a green hat
    r = model.binary_var(name="r")  # wears a green shirt
    s = model.binary_var(name="s")  # wears green socks
    n = model.binary_var(name="n")  # pays the entrance fee

    # Each rule may be broken only by paying the fee (rule 4). The rules are clauses over
    # the 0/1 choices, written as "at least one literal holds".
    # 1. A green tie requires a green shirt: not t, or r, or the fee.
    model.add_constraint((1 - t) + r + n >= 1)
    # 2. Green socks or a green shirt only with a green tie or a green hat:
    #    (s or r) -> (t or h), or the fee; one clause for s and one for r.
    model.add_constraint((1 - s) + t + h + n >= 1)
    model.add_constraint((1 - r) + t + h + n >= 1)
    # 3. A green shirt, or a green hat, or no green socks requires a green tie:
    #    (r or h or not s) -> t, or the fee; one clause for each of the three cases.
    model.add_constraint((1 - r) + t + n >= 1)
    model.add_constraint((1 - h) + t + n >= 1)
    model.add_constraint(s + t + n >= 1)

    # Minimise what he pays: tie $10, hat $2, socks $12, fee $11 (he already owns the shirt).
    model.minimize(10 * t + 2 * h + 12 * s + 11 * n)

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}
