# Fancy dress: Mr Greenguest chooses what green clothes to buy (tie, hat,
# socks; he owns a shirt) or pays the entrance fee instead, so that the
# dress rules hold at the lowest total cost.
# The rules and prices are the puzzle itself; the instance carries no fields.
from pysat.formula import IDPool, WCNF


def build(instance):
    pool = IDPool()
    t = pool.id("tie")      # wears a green tie
    h = pool.id("hat")      # wears a green hat
    r = pool.id("shirt")    # wears a green shirt
    s = pool.id("socks")    # wears green socks
    n = pool.id("fee")      # pays the entrance fee

    formula = WCNF()
    # Rule 1: a green tie requires a green shirt, unless the fee is paid.
    formula.append([-t, r, n])
    # Rule 2: green socks or a green shirt require a green tie or a green
    # hat, unless the fee is paid.
    formula.append([-s, t, h, n])
    formula.append([-r, t, h, n])
    # Rule 3: a green shirt, a green hat, or no green socks requires a green
    # tie, unless the fee is paid.
    formula.append([-r, t, n])
    formula.append([-h, t, n])
    formula.append([s, t, n])

    # Minimise the cost 10 * tie + 2 * hat + 12 * socks + 11 * fee: each
    # item bought, and the fee, pays its price. The shirt is already owned.
    formula.append([-t], weight=10)
    formula.append([-h], weight=2)
    formula.append([-s], weight=12)
    formula.append([-n], weight=11)

    return formula, {"t": t, "h": h, "r": r, "s": s, "n": n}
