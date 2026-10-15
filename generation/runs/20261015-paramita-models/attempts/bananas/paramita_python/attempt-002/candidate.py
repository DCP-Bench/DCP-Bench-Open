# Fruit shopping: buy 100 fruits for exactly 100 dollars, every type at least once,
# minimising the number of bananas and apples.
# Prices are problem data from the statement, scaled to integers: 1 unit = 1/315 dollar,
# since 315 = lcm(5, 7, 9, 3) makes every per-fruit price whole.
# The two equations (100 fruits, 100 dollars) are solved into a table of allowed
# (oranges, apples) combinations; each combination fixes mangoes and bananas.
from paramita.modelling import Bool

TOTAL = 100  # fruits to purchase
PRICE_BANANA, PRICE_ORANGE, PRICE_MANGO, PRICE_APPLE = 189, 225, 245, 945  # 1/315 dollar each
BUDGET = 100 * 315  # 100 dollars
# with bananas = 100 - o - m - a, the spend gives 36 o + 56 m + 756 a = 12600, i.e.
# 9 o + 14 m + 189 a = 3150, and oranges are a multiple of 7: o = 7 k gives 9 k + 2 m + 27 a = 450


def allowed_combinations():
    combos = []
    for k in range(1, 15):  # oranges 7, 14, ..., 98
        for a in range(1, 17):  # apples: 189 a <= 3150 - 9 - 14
            twice_m = 450 - 9 * k - 27 * a
            if twice_m <= 0 or twice_m % 2:
                continue
            m = twice_m // 2
            b = TOTAL - 7 * k - m - a
            if m >= 1 and b >= 1:  # every type is bought at least once
                combos.append((7 * k, m, b, a))
    return combos


def build(instance):
    combos = allowed_combinations()
    pick = {c: Bool(f"combo_o{c[0]}_m{c[1]}_b{c[2]}_a{c[3]}") for c in combos}
    cons = [sum(pick.values()) == 1]  # exactly one allowed combination

    oranges = sum(c[0] * v for c, v in pick.items())
    mangoes = sum(c[1] * v for c, v in pick.items())
    bananas = sum(c[2] * v for c, v in pick.items())
    apples = sum(c[3] * v for c, v in pick.items())

    outputs = {"apples": apples, "bananas": bananas, "mangoes": mangoes, "oranges": oranges}

    # minimise the quantity of bananas and apples
    objective = sum((c[2] + c[3]) * v for c, v in pick.items())
    return cons, outputs, ("minimize", objective)
