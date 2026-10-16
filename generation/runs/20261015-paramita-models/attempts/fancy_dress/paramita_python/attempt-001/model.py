# Fancy dress: Mr Greenguest owns a green shirt and chooses which of tie (t), hat (h),
# shirt (r), socks (s) to wear, or pays the entrance fee (n), so that the total cost is minimal.
# The prices come from the problem statement and are fixed for this problem (not instance data).
from paramita.modelling import Bool, If, Iff


def build(instance):
    t = Bool("t")  # green tie, buyable for $10
    h = Bool("h")  # green hat (used), buyable for $2
    r = Bool("r")  # green shirt, already owned, so it costs nothing
    s = Bool("s")  # green socks, buyable for $12
    n = Bool("n")  # pays the $11 entrance fee

    # rule 1: if someone wears a green tie he has to wear a green shirt
    rule1 = If(t, r)

    # rule 2: green socks and a green shirt only if a green tie or a green hat is worn
    rule2 = If(s & r, t | h)

    # rule 3: a green shirt or a green hat or no green socks requires a green tie
    rule3 = If(r | h | ~s, t)

    cons = []
    # rule 4: the fee is paid exactly when the guest is not dressed according to rules 1-3
    cons.append(Iff(n, ~(rule1 & rule2 & rule3)))

    # the cheapest choice: tie $10, hat $2, socks $12, entrance fee $11
    total = 10 * t + 2 * h + 12 * s + 11 * n

    outputs = {"t": t, "h": h, "r": r, "s": s, "n": n}
    return cons, outputs, ("minimize", total)
