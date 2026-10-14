# Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpences)
# worth 1 pound 5 shillings 6 pence. How many half-crowns did he get?
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    values = [30, 12, 6]  # pence in a half-crown, a shilling and a sixpence
    total_value = 240 + 5 * 12 + 6  # 1 pound 5 shillings 6 pence, in pence
    total_coins = 15
    pool = IDPool()
    # coins[t] = how many coins of type t he was given: half-crowns, shillings, sixpences
    coins = [Integer(f"coins_{t}", 0, total_coins, vpool=pool) for t in range(len(values))]
    engine = IntegerEngine(vars=coins, vpool=pool)

    # the coins are worth the total value
    engine.add_linear(sum(values[t] * coins[t] for t in range(len(values))) == total_value)
    # he was given 15 coins
    engine.add_linear(sum(coins) == total_coins)

    return engine.clausify(), {"half_crowns": coins[0]}
