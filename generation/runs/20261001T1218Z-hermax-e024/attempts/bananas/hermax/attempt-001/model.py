# Bananas: buy 100 fruits for 100 dollars, where five bananas cost 3 dollars, seven
# oranges 5 dollars, nine mangoes 7 dollars and three apples 9 dollars. Every kind
# must be bought, and as few bananas and apples as possible.
from hermax.model import Model


def build(instance):
    # The prices and totals are fixed by the problem; the instance carries no data.
    fruits = 100
    dollars = 100

    m = Model()
    # how many of each fruit to buy: at least one of every kind, at most all 100
    bananas = m.int("bananas", 1, fruits)
    oranges = m.int("oranges", 1, fruits)
    mangoes = m.int("mangoes", 1, fruits)
    apples = m.int("apples", 1, fruits)

    # 100 fruits in all
    m &= (bananas + oranges + mangoes + apples == fruits)

    # they cost 100 dollars: 3/5 per banana, 5/7 per orange, 7/9 per mango, 9/3 per apple.
    # Multiplied through by 3 * 5 * 7 * 9 = 945 to clear the fractions, then divided by
    # the common factor 3 of all coefficients.
    m &= (189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples == dollars * 315)

    # Minimise bananas + apples. A soft clause pays 1 when its literal is false, so the
    # literal "bananas <= v - 1" pays 1 for every v from 2 to 100 that bananas reaches:
    # bananas - 1 in all, and likewise for apples. The constant 2 does not move the optimum.
    for v in range(2, fruits + 1):
        m.obj[1] += (bananas <= v - 1)
        m.obj[1] += (apples <= v - 1)

    return m, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}
