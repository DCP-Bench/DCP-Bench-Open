import cpmpy as cp


def build(instance):
    """Fancy dress: the cheapest way for Mr Greenguest to attend, either by
    dressing to the rules or by paying the entrance fee.

    The puzzle states its own rules and prices, so `instance` is unused.  He
    already owns the shirt, so only the tie, hat, socks and fee cost anything.
    """
    del instance

    tie = cp.boolvar(name="t")
    hat = cp.boolvar(name="h")
    shirt = cp.boolvar(name="r")
    socks = cp.boolvar(name="s")
    fee = cp.boolvar(name="n")
    cost = cp.intvar(0, 100, name="cost")

    model = cp.Model(
        # 1. A green tie needs a green shirt.
        tie.implies(shirt) | fee,
        # 2. Green socks or a green shirt need a green tie or a green hat.
        ((socks | shirt).implies(tie | hat)) | fee,
        # 3. A green shirt, a green hat, or no green socks needs a green tie.
        (shirt | hat | ~socks).implies(tie | fee),
        cost == 10 * tie + 2 * hat + 12 * socks + 11 * fee,
    )
    model.minimize(cost)

    return model, {"t": tie, "h": hat, "r": shirt, "s": socks, "n": fee}
