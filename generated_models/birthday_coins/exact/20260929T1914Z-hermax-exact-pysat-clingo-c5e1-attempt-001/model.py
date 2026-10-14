# Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpences)
# worth 1 pound 5 shillings 6 pence. How many half-crowns did he get?
from exact import Exact


def build(instance):
    # The puzzle is fixed by the problem; the instance carries no data.
    values = [30, 12, 6]  # pence in a half-crown, a shilling and a sixpence
    total_value = 240 + 5 * 12 + 6  # 1 pound 5 shillings 6 pence, in pence
    total_coins = 15
    solver = Exact()
    # coins[t] = how many coins of type t he was given: half-crowns, shillings, sixpences
    coins = [f"coins_{t}" for t in range(len(values))]
    for name in coins:
        solver.addVariable(name, 0, total_coins)

    # the coins are worth the total value
    solver.addConstraint([(values[t], coins[t]) for t in range(len(values))], True, total_value, True, total_value)
    # he was given 15 coins
    solver.addConstraint([(1, name) for name in coins], True, total_coins, True, total_coins)

    return solver, {"half_crowns": coins[0]}
