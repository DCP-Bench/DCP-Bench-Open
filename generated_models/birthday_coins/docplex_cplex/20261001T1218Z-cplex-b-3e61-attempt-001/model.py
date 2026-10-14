"""Birthday coins: Tommy got 15 coins, half-crowns, shillings and sixpences, worth 1 pound 5
shillings 6 pence in all. How many half-crowns did he get?

The model reports the number of half-crowns. The puzzle has no instance data; the coin values and
totals are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    values = [30, 12, 6]              # pence per half-crown, shilling, sixpence (puzzle constant)
    total_value = 240 + 5 * 12 + 6    # 1 pound 5 shillings 6 pence, in pence (puzzle constant)
    total_coins = 15                  # coins given (puzzle constant)

    model = Model("birthday_coins")

    # coins[i]: how many coins of kind i (half-crowns, shillings, sixpences), 0..15.
    coins = [model.integer_var(0, total_coins, name=f"coins_{i}") for i in range(len(values))]

    # The coins add up to 1 pound 5 shillings 6 pence.
    model.add_constraint(model.dot(coins, values) == total_value)

    # There are 15 coins.
    model.add_constraint(model.sum(coins) == total_coins)

    return model, {"half_crowns": coins[0]}
