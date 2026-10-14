# Birthday coins: Tommy got 15 coins (half-crowns, shillings and sixpences) worth 1 pound 5
# shillings 6 pence. How many half-crowns did he get?
from pychoco.model import Model

# The puzzle has no instance data; coin values and totals are its statement, in pence
# (a shilling is 12 pence, a pound 240 pence, a half-crown 2 shillings and sixpence).
VALUES = [30, 12, 6]  # half-crown, shilling, sixpence
TOTAL_VALUE = 240 + 5 * 12 + 6  # 1 pound 5 shillings 6 pence
TOTAL_COINS = 15


def build(instance):
    del instance  # the puzzle carries no instance data

    model = Model()

    # coins[k] = number of coins of type k; there are 15 coins in all, which bounds each count
    coins = [model.intvar(0, TOTAL_COINS, name=f"coins_{k}") for k in range(len(VALUES))]

    # The coins add up to 1 pound 5 shillings 6 pence.
    model.scalar(coins, VALUES, "=", TOTAL_VALUE).post()

    # There are 15 coins.
    model.sum(coins, "=", TOTAL_COINS).post()

    return model, {"half_crowns": coins[0]}
