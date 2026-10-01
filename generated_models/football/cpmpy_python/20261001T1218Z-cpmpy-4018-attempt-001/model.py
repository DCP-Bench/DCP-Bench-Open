# Football squad: buy players from four groups (goalkeepers, defenders, midfielders, strikers) so
# that the total price is as close as possible to the 30 million GBP limit without going over,
# while meeting the minimum numbers per group and at least eleven players in total.
import cpmpy as cp


def build(instance):
    # The price list and the purchase rules are the problem statement itself (the instance has no
    # fields), so they are mirrored here. Prices are in thousands of GBP, so that they are integers.
    budget = 30000
    prices = [
        [730, 1280, 3880],                                              # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],   # midfielders
        [4460, 6470, 7780, 8390, 9500],                                 # strikers
    ]
    # Number of players to buy in each group: goalkeepers exactly 1, defenders at least 2,
    # midfielders at least 3, strikers at least 2 (no group has an upper limit besides its size).
    min_buy = [1, 2, 3, 2]
    max_buy = [1] + [len(group) for group in prices[1:]]
    min_total = 11  # at least eleven players in total

    # buy[g][p] = 1 if player p of group g is bought
    buy = [cp.boolvar(shape=(len(group),), name=f"buy{g}") for g, group in enumerate(prices)]

    model = cp.Model()

    # Each group supplies between its minimum and its maximum number of players.
    for g in range(len(prices)):
        model += cp.sum(buy[g]) >= min_buy[g]
        model += cp.sum(buy[g]) <= max_buy[g]

    # At least eleven players are bought in total.
    model += cp.sum([cp.sum(group) for group in buy]) >= min_total

    # z = total price of the players bought, in thousands of GBP; it may not exceed the budget.
    z = cp.intvar(0, budget, name="z")
    model += z == cp.sum([prices[g][p] * buy[g][p]
                          for g in range(len(prices)) for p in range(len(prices[g]))])

    # Spend as much as possible: the total price should be as close to the budget as it can get.
    model.maximize(z)

    return model, {"z": z}
