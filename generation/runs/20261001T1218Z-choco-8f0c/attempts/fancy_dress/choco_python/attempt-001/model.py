# Fancy dress: Mr Greenguest owns a green shirt and can buy a green tie ($10), hat ($2) or socks
# ($12); a guest breaking the dress rules pays an $11 entrance fee. Find the cheapest choice.
from pychoco.model import Model

# The puzzle has no instance data; the prices and rules are its statement.
PRICE_TIE, PRICE_HAT, PRICE_SOCKS, FEE = 10, 2, 12, 11


def clause(model, positive, negative):
    """At least one of the positive literals is true or one of the negative ones is false."""
    model.scalar(positive + negative, [1] * len(positive) + [-1] * len(negative),
                 ">=", 1 - len(negative)).post()


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    t = model.boolvar(name="t")  # wears a green tie
    h = model.boolvar(name="h")  # wears a green hat
    r = model.boolvar(name="r")  # wears a green shirt (already owned)
    s = model.boolvar(name="s")  # wears green socks
    n = model.boolvar(name="n")  # pays the entrance fee

    # Each rule may be broken only by paying the fee (rule 4).
    # 1. A green tie needs a green shirt: not t, or r, or n.
    clause(model, [r, n], [t])
    # 2. Green socks or a green shirt only with a green tie or a green hat:
    #    (s or r) implies (t or h), or n.
    clause(model, [t, h, n], [s])
    clause(model, [t, h, n], [r])
    # 3. A green shirt, a green hat or no green socks needs a green tie:
    #    (r or h or not s) implies (t or n).
    clause(model, [t, n], [r])
    clause(model, [t, n], [h])
    clause(model, [s, t, n], [])

    # Minimise the cost of the purchases and the fee.
    cost = model.intvar(0, PRICE_TIE + PRICE_HAT + PRICE_SOCKS + FEE, name="cost")
    model.scalar([t, h, s, n], [PRICE_TIE, PRICE_HAT, PRICE_SOCKS, FEE], "=", cost).post()

    return model, {"t": t, "h": h, "r": r, "s": s, "n": n}, ("minimize", cost)
