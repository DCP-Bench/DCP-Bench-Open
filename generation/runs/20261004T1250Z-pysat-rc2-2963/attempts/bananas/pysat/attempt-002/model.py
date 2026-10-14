# Bananas: buy 100 fruits for 100 dollars at five bananas for $3, seven
# oranges for $5, nine mangoes for $7 and three apples for $9, buying at
# least one of each kind and as few bananas plus apples as possible.
# The prices and the 100/100 targets are the puzzle itself; the instance
# carries no fields.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine
from pysat.pb import PBEnc


def build(instance):
    pool = IDPool()
    # Quantity of each fruit, 1..100 as in the reference. Coupled encoding:
    # thresholds for the sums and the objective, value literals for the
    # runner to block a reported answer.
    bananas, oranges, mangoes, apples = (
        Integer(name, 1, 100, encoding="coupled", vpool=pool)
        for name in ("bananas", "oranges", "mangoes", "apples"))
    engine = IntegerEngine(vars=[bananas, oranges, mangoes, apples], vpool=pool)

    # 100 fruits are bought.
    engine.add_linear(bananas + oranges + mangoes + apples == 100)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The fruits cost 100 dollars: 3/5 per banana, 5/7 per orange, 7/9 per
    # mango and 9/3 per apple. Multiplied through by 945 and divided by 3,
    # 189 b + 225 o + 245 m + 945 a = 31500. With o = 100 - b - m - a from
    # the count above this is -36 b + 20 m + 720 a = 9000, or
    # -9 b + 5 m + 180 a = 2250, the same constraint with small
    # coefficients: the original ones (bound 94500) made the pseudo-Boolean
    # encoding too large to build within the time limit.
    # Each quantity is 1 + (number of thresholds 2..100 it reaches). The
    # -9 b term is written as 9 per threshold of b NOT reached, minus
    # 9 * 100, which keeps PBEnc's bound non-negative:
    # 5 * (1 + M) + 180 * (1 + A) + 9 * (notB) - 900 = 2250.
    lits, weights = [], []
    for v in range(2, 101):
        lits.append(mangoes.ge(v))
        weights.append(5)
        lits.append(apples.ge(v))
        weights.append(180)
        lits.append(-bananas.ge(v))
        weights.append(9)
    formula.extend(PBEnc.equals(lits=lits, weights=weights,
                                bound=2250 + 900 - 5 - 180, vpool=pool).clauses)

    # Minimise bananas + apples: each banana and each apple beyond the one
    # that must be bought pays 1 (a constant 2 below the true sum).
    for fruit in (bananas, apples):
        for v in range(2, 101):
            formula.append([-fruit.ge(v)], weight=1)

    return formula, {"bananas": bananas, "oranges": oranges,
                     "mangoes": mangoes, "apples": apples}
