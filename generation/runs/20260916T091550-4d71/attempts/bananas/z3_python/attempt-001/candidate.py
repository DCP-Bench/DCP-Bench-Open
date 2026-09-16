import z3


def build(instance):
    """Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
    bananas and apples as possible.

    The puzzle states its own prices, so it carries no instance data.  Five
    bananas cost three dollars, seven oranges five, nine mangoes seven and
    three apples nine; multiplying through by 3*5*7*9 = 945 clears the
    divisions, which is what the reference does.
    """
    del instance

    bananas, oranges, mangoes, apples = z3.Ints("bananas oranges mangoes apples")
    the_sum = z3.Int("the_sum")

    solver = z3.Solver()
    for value in (bananas, oranges, mangoes, apples):
        solver.add(value >= 1, value <= 100)
    solver.add(the_sum >= 1, the_sum <= 2000)

    solver.add(the_sum == bananas + apples)
    solver.add(3 * bananas * 189 + 5 * oranges * 135
               + 7 * mangoes * 105 + 9 * apples * 315 == 100 * 945)
    solver.add(bananas + oranges + mangoes + apples == 100)

    return solver, {
        "bananas": bananas, "oranges": oranges,
        "mangoes": mangoes, "apples": apples,
    }, ("minimize", the_sum)
