# Bananas: buy 100 fruits for 100 dollars at five bananas for $3, seven
# oranges for $5, nine mangoes for $7 and three apples for $9, buying at
# least one of each kind and as few bananas plus apples as possible.
# The prices and the 100/100 targets are the puzzle itself; the instance
# carries no fields.
from pysat.formula import IDPool, WCNF
from pysat.integer import Integer, IntegerEngine

FRUITS = 100     # fruits to buy
DOLLARS = 100    # dollars to spend


def build(instance):
    pool = IDPool()
    # Quantity of each fruit, 1..100 as in the reference. Coupled encoding:
    # value literals for the price table below and for the runner to block
    # a reported answer, thresholds for the count and the objective.
    bananas, oranges, mangoes, apples = (
        Integer(name, 1, FRUITS, encoding="coupled", vpool=pool)
        for name in ("bananas", "oranges", "mangoes", "apples"))
    engine = IntegerEngine(vars=[bananas, oranges, mangoes, apples], vpool=pool)

    # 100 fruits are bought.
    engine.add_linear(bananas + oranges + mangoes + apples == FRUITS)

    formula = WCNF()
    formula.extend(engine.clausify().clauses)

    # The fruits cost 100 dollars: 3/5 per banana, 5/7 per orange, 7/9 per
    # mango and 9/3 per apple. Multiplied through by 945 and divided by 3,
    # 189 b + 225 o + 245 m + 945 a = 31500. Substituting
    # o = 100 - b - m - a from the count above gives
    # 9 b = 5 m + 180 a - 2250, so mangoes and apples fix the bananas.
    # This is stated as a table: for each pair of values of apples and
    # mangoes, the one banana count that pays exactly, or the pair is
    # excluded. A pseudo-Boolean encoding of the price equation with these
    # coefficients ran out of time.
    scale = 945 // 3
    price = {"b": 3 * 189 // 3, "o": 5 * 135 // 3, "m": 7 * 105 // 3,
             "a": 9 * 315 // 3}
    budget = DOLLARS * scale
    for a in range(1, FRUITS + 1):
        for m in range(1, FRUITS + 1):
            # price_b * b + price_o * (FRUITS - b - m - a) + price_m * m
            #   + price_a * a = budget, solved for b.
            rest = (budget - price["o"] * (FRUITS - m - a)
                    - price["m"] * m - price["a"] * a)
            step = price["b"] - price["o"]
            pair = [-apples.equals(a), -mangoes.equals(m)]
            if rest % step == 0 and 1 <= rest // step <= FRUITS:
                formula.append(pair + [bananas.equals(rest // step)])
            else:
                formula.append(pair)

    # Minimise bananas + apples: each banana and each apple beyond the one
    # that must be bought pays 1 (a constant 2 below the true sum).
    for fruit in (bananas, apples):
        for v in range(2, FRUITS + 1):
            formula.append([-fruit.ge(v)], weight=1)

    return formula, {"bananas": bananas, "oranges": oranges,
                     "mangoes": mangoes, "apples": apples}
