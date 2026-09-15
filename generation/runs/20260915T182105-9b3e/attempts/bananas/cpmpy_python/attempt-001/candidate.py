import cpmpy as cp


def build(instance):
    """Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
    bananas and apples as possible.

    The puzzle states its own prices, so `instance` is unused.  Five bananas
    cost three dollars, seven oranges five, nine mangoes seven and three apples
    nine; multiplying through by 3*5*7*9 = 945 clears the divisions, which is
    what the reference does.
    """
    del instance

    x = cp.intvar(1, 100, shape=4, name="x")
    bananas, oranges, mangoes, apples = x
    the_sum = cp.intvar(1, 2000, name="the_sum")

    model = cp.Model(
        the_sum == bananas + apples,
        3 * bananas * 189
        + 5 * oranges * 135
        + 7 * mangoes * 105
        + 9 * apples * 315
        == 100 * 945,
        cp.sum(x) == 100,
    )
    model.minimize(the_sum)

    return model, {
        "bananas": bananas,
        "oranges": oranges,
        "mangoes": mangoes,
        "apples": apples,
    }
