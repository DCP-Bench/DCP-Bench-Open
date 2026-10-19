# Bananas puzzle: buy 100 fruits (bananas, oranges, mangoes, apples) for exactly
# 100 dollars, every fruit type at least once, minimise bananas and apples.
# Prices: 5 bananas for 3, 7 oranges for 5, 9 mangoes for 7, 3 apples for 9.
import cvc5.pythonic as cz


def build(instance):
    bananas, oranges, mangoes, apples = cz.Ints("bananas oranges mangoes apples")

    # Every fruit type is bought at least once.
    # Each count is non-negative and bounded by the 100 fruits.
    # The description says all types need to be purchased.
    bounds = [
        bananas >= 1, oranges >= 1, mangoes >= 1, apples >= 1,
        bananas <= 100, oranges <= 100, mangoes <= 100, apples <= 100,
    ]

    # Buy 100 fruits in total.
    # I need to purchase 100 fruits in 100 dollars.
    count = [bananas + oranges + mangoes + apples == 100]

    # Spend exactly 100 dollars. Costs are scaled by 315 (the lcm of 5, 7, 9, 3)
    # so every price is an integer: banana 3/5 = 189, orange 5/7 = 225,
    # mango 7/9 = 245, apple 9/3 = 945, budget 100 = 31500.
    # 100 dollars in 100 dollars.
    budget = [
        189 * bananas + 225 * oranges + 245 * mangoes + 945 * apples == 31500,
    ]

    # Bananas and apples should be of minimum quantity.
    objective = bananas + apples

    return (
        bounds + count + budget,
        {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples},
        ("minimize", objective),
    )
