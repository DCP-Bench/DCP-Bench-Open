# Bananas: buy 100 fruits for 100 dollars at five bananas for $3, seven
# oranges for $5, nine mangoes for $7 and three apples for $9, buying at
# least one of each kind and as few bananas plus apples as possible.
# The prices and the 100/100 targets are the puzzle itself; the instance
# carries no fields.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine


def build(instance):
    pool = IDPool()
    # Quantity of each fruit, 1..100: every kind must be bought, and no more
    # than 100 fruits are bought in all. Coupled encoding: thresholds for the
    # objective, value literals for the runner to block a reported answer.
    bananas, oranges, mangoes, apples = (
        Integer(name, 1, 100, encoding="coupled", vpool=pool)
        for name in ("bananas", "oranges", "mangoes", "apples"))
    engine = IntegerEngine(vars=[bananas, oranges, mangoes, apples], vpool=pool)

    # The fruits cost 100 dollars: 3/5 per banana, 5/7 per orange, 7/9 per
    # mango and 9/3 per apple, multiplied through by 945 = 3 * 5 * 7 * 9 to
    # keep the coefficients whole, as the reference does.
    engine.add_linear(3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes
                      + 9 * 315 * apples == 100 * 945)
    # 100 fruits are bought.
    engine.add_linear(bananas + oranges + mangoes + apples == 100)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # Minimise bananas + apples: each banana and each apple beyond the one
    # that must be bought pays 1 (a constant 2 below the true sum).
    for fruit in (bananas, apples):
        for v in range(2, 101):
            formula.append([-fruit.ge(v)], weight=1)

    return formula, {"bananas": bananas, "oranges": oranges,
                     "mangoes": mangoes, "apples": apples}
