"""Bananas: five bananas cost $3, seven oranges $5, nine mangoes $7 and three apples $9. Buy 100
fruits for $100, at least one of every kind, with as few bananas and apples together as possible.

The model reports how many of each fruit to buy. The puzzle has no instance data; its prices and
totals are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    total_fruits = 100   # fruits to buy (puzzle constant)
    total_dollars = 100  # money to spend (puzzle constant)

    model = Model("bananas")

    # Every kind of fruit is bought, 1..100 of each (the reference's domain).
    bananas = model.integer_var(1, 100, name="bananas")
    oranges = model.integer_var(1, 100, name="oranges")
    mangoes = model.integer_var(1, 100, name="mangoes")
    apples = model.integer_var(1, 100, name="apples")

    # The fruits cost $100: 3/5 per banana, 5/7 per orange, 7/9 per mango, 9/3 per apple;
    # both sides are multiplied by 3 * 5 * 7 * 9 = 945 to keep the coefficients integral.
    model.add_constraint(3 * 189 * bananas + 5 * 135 * oranges + 7 * 105 * mangoes + 9 * 315 * apples
                         == total_dollars * 945)

    # 100 fruits are bought.
    model.add_constraint(bananas + oranges + mangoes + apples == total_fruits)

    # Minimize the number of bananas and apples together.
    model.minimize(bananas + apples)

    return model, {"bananas": bananas, "oranges": oranges, "mangoes": mangoes, "apples": apples}
