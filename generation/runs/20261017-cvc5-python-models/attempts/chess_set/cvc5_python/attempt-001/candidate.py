# Chess set production (joinery): decide how many small and large boxwood chess
# sets to make each week to maximise profit.
# Small set: 3 lathe-hours, 1 kg boxwood, profit 5. Large set: 2 lathe-hours,
# 3 kg boxwood, profit 20. Lathe capacity: 4 lathes x 40 h = 160 h. Boxwood: 200 kg.

import cvc5.pythonic as cz


def build(instance):
    small, large = cz.Ints("small_set large_set")

    constraints = [
        # Sets made are non-negative whole numbers.
        small >= 0,
        large >= 0,
        # Lathe-hours per week: the small set needs 3 hours, the large set 2 hours,
        # and there are 160 lathe-hours per week (four lathes, 40 hours each).
        3 * small + 2 * large <= 160,
        # Boxwood per week: the small set needs 1 kg, the large set 3 kg, and only
        # 200 kg per week can be obtained.
        small + 3 * large <= 200,
    ]

    # Profit: $5 per small set and $20 per large set.
    profit = 5 * small + 20 * large

    outputs = {
        "small_set": small,
        "large_set": large,
        "max_profit": profit,
    }
    return constraints, outputs, ("maximize", profit)
