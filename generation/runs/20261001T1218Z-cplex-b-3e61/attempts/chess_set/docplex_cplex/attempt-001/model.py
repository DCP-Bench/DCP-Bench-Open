"""Chess sets: a joinery makes small and large chess sets, limited by 160 lathe-hours and 200 kg of
boxwood per week; choose how many of each to make to maximize profit.

The model reports the numbers of small and large sets and the profit. The puzzle has no instance
data; its figures are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    model = Model("chess_set")

    # Sets made per week, 0..100 each (the reference's domain).
    small_set = model.integer_var(0, 100, name="small_set")
    large_set = model.integer_var(0, 100, name="large_set")
    max_profit = model.integer_var(0, 10000, name="max_profit")

    # Boxwood: 1 kg per small set, 3 kg per large set, 200 kg available.
    model.add_constraint(small_set + 3 * large_set <= 200)

    # Lathe time: 3 hours per small set, 2 per large set, 160 lathe-hours available.
    model.add_constraint(3 * small_set + 2 * large_set <= 160)

    # Profit: $5 per small set, $20 per large set.
    model.add_constraint(max_profit == 5 * small_set + 20 * large_set)

    # Maximize the profit.
    model.maximize(max_profit)

    return model, {"small_set": small_set, "large_set": large_set, "max_profit": max_profit}
