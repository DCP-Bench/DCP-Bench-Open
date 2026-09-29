# Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpences)
# worth 1 pound 5 shillings 6 pence. How many half-crowns did he get?
from hermax.model import Model


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    values = [30, 12, 6]  # pence in a half-crown, a shilling and a sixpence
    total_value = 240 + 5 * 12 + 6  # 1 pound 5 shillings 6 pence, in pence
    total_coins = 15
    m = Model()
    # coins[t] = how many coins of type t he was given: half-crowns, shillings, sixpences
    coins = m.int_vector("coins", len(values), 0, total_coins)

    # the coins are worth the total value
    m &= (sum(values[t] * coins[t] for t in range(len(values))) == total_value)
    # he was given 15 coins
    m &= (sum(coins[t] for t in range(len(values))) == total_coins)

    return m, {"half_crowns": coins[0]}
