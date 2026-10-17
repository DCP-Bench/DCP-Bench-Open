# Fancy dress party: Mr Greenguest chooses a tie (t), hat (h), shirt (r), socks (s)
# and pays an entrance fee (n). Minimise the total cost.
import cvc5.pythonic as cz


def build(instance):
    t = cz.Bool("t")
    h = cz.Bool("h")
    r = cz.Bool("r")
    s = cz.Bool("s")
    n = cz.Bool("n")

    # Rule 1: If someone wears a green tie he has to wear a green shirt.
    rule1 = cz.Implies(t, r)

    # Rule 2: A guest may only wear green socks and a green shirt if he wears
    # a green tie or a green hat.
    rule2 = cz.Implies(cz.And(s, r), cz.Or(t, h))

    # Rule 3: A guest wearing a green shirt or a green hat or who does not wear
    # green socks must wear a green tie.
    rule3 = cz.Implies(cz.Or(r, h, cz.Not(s)), t)

    # Rule 4: A guest who is not dressed according to rules 1-3 must pay the
    # entrance fee.
    constraints = [
        n == cz.Not(cz.And(rule1, rule2, rule3)),
    ]

    # The guest owns a green shirt, so wearing one costs nothing. Items bought:
    # tie $10, hat $2, socks $12, entrance fee $11.
    cost = (
        cz.If(t, 10, 0)
        + cz.If(h, 2, 0)
        + cz.If(s, 12, 0)
        + cz.If(n, 11, 0)
    )

    return constraints, {"t": t, "h": h, "r": r, "s": s, "n": n}, ("minimize", cost)
