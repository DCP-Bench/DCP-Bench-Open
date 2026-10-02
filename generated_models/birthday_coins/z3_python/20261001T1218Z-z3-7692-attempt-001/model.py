# Birthday coins: Tommy has 15 coins, half-crowns, shillings and sixpences, worth
# 1 pound 5 shillings 6 pence in total; find how many are half-crowns.
import z3


def build(instance):
    del instance  # the puzzle states its own coins and totals

    # Problem data: coin values in pence for half-crowns, shillings, sixpences.
    values = [30, 12, 6]
    total_value = 240 + 5 * 12 + 6  # 1 pound (240 pence) + 5 shillings + 6 pence
    total_coins = 15

    # coins[i] = how many coins of type i Tommy has, at most all of them.
    coins = z3.IntVector("coins", len(values))

    solver = z3.Solver()
    for c in coins:
        solver.add(c >= 0, c <= total_coins)

    # The coins add up to the pounds, shillings and pence he counted.
    solver.add(z3.Sum([v * c for v, c in zip(values, coins)]) == total_value)

    # He was given 15 coins in all.
    solver.add(z3.Sum(coins) == total_coins)

    return solver, {"half_crowns": coins[0]}
