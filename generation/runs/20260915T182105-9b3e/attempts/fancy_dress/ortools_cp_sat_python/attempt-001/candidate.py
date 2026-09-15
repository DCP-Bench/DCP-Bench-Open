from ortools.sat.python import cp_model


def build(instance):
    """Fancy dress: the cheapest way for Mr Greenguest to attend, either by
    dressing to the rules or by paying the entrance fee.

    The puzzle states its own rules and prices, so `instance` is unused.  He
    already owns the shirt, so only the tie, hat, socks and fee cost anything.
    """
    del instance

    model = cp_model.CpModel()
    tie = model.new_bool_var("t")
    hat = model.new_bool_var("h")
    shirt = model.new_bool_var("r")
    socks = model.new_bool_var("s")
    fee = model.new_bool_var("n")
    cost = model.new_int_var(0, 100, "cost")

    # 1. A green tie needs a green shirt, unless the fee is paid.
    #    (tie -> shirt) or fee  is  (not tie) or shirt or fee.
    model.add_bool_or([~tie, shirt, fee])

    # 2. Green socks or a green shirt need a green tie or a green hat, unless
    #    the fee is paid.  The antecedent is a disjunction, so it is posted once
    #    per disjunct.
    model.add_bool_or([~socks, tie, hat, fee])
    model.add_bool_or([~shirt, tie, hat, fee])

    # 3. A green shirt, a green hat, or no green socks needs a green tie or the
    #    fee.  Again one clause per disjunct of the antecedent.
    model.add_bool_or([~shirt, tie, fee])
    model.add_bool_or([~hat, tie, fee])
    model.add_bool_or([socks, tie, fee])

    model.add(cost == 10 * tie + 2 * hat + 12 * socks + 11 * fee)
    model.minimize(cost)

    return model, {"t": tie, "h": hat, "r": shirt, "s": socks, "n": fee}
