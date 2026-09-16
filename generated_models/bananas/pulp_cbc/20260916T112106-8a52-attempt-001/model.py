import pulp


def build(instance):
    """Bananas: buy exactly 100 fruits for exactly 100 dollars, taking as few
    bananas and apples as possible. Multiplying by 3*5*7*9 = 945 clears the
    divisions, which is what the reference does.
    """
    del instance

    problem = pulp.LpProblem("bananas", pulp.LpMinimize)
    bananas = pulp.LpVariable("bananas", 1, 100, cat="Integer")
    oranges = pulp.LpVariable("oranges", 1, 100, cat="Integer")
    mangoes = pulp.LpVariable("mangoes", 1, 100, cat="Integer")
    apples = pulp.LpVariable("apples", 1, 100, cat="Integer")

    problem += (3 * bananas * 189 + 5 * oranges * 135
                + 7 * mangoes * 105 + 9 * apples * 315 == 100 * 945)
    problem += bananas + oranges + mangoes + apples == 100
    problem += bananas + apples

    return problem, {
        "bananas": bananas, "oranges": oranges,
        "mangoes": mangoes, "apples": apples,
    }
