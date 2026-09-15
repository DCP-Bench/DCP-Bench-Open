from ortools.sat.python import cp_model


def build(instance):
    """Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
    bananas and apples as possible.

    The puzzle states its own prices, so `instance` is unused.  Five bananas
    cost three dollars, seven oranges five, nine mangoes seven and three apples
    nine; multiplying through by 3*5*7*9 = 945 clears the divisions, which is
    what the reference does.
    """
    del instance

    model = cp_model.CpModel()
    bananas = model.new_int_var(1, 100, "bananas")
    oranges = model.new_int_var(1, 100, "oranges")
    mangoes = model.new_int_var(1, 100, "mangoes")
    apples = model.new_int_var(1, 100, "apples")
    the_sum = model.new_int_var(1, 2000, "the_sum")

    model.add(the_sum == bananas + apples)
    model.add(
        3 * bananas * 189
        + 5 * oranges * 135
        + 7 * mangoes * 105
        + 9 * apples * 315
        == 100 * 945
    )
    model.add(bananas + oranges + mangoes + apples == 100)
    model.minimize(the_sum)

    return model, {
        "bananas": bananas,
        "oranges": oranges,
        "mangoes": mangoes,
        "apples": apples,
    }
