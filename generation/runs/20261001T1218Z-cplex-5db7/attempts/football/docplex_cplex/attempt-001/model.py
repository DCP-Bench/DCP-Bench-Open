"""Football squad: buy players of four kinds, within the numbers required of each kind and at
least eleven in all, spending as close to the GBP 30 million limit as possible without going
over.
"""
from docplex.mp.model import Model


def build(instance):
    # The problem has no instance data. Prices (GBP thousands), the budget and the required
    # numbers come from the statement and are mirrored from the reference; a price of 0 means
    # there is no such player.
    budget = 30000
    num_players = [3, 8, 10, 5]  # goalkeepers, defenders, midfielders, strikers
    max_num_players = max(num_players)
    min_max = [[1, 1],                  # exactly one goalkeeper
               [2, max_num_players],    # two or more defenders
               [3, max_num_players],    # three or more midfielders
               [2, max_num_players]]    # two or more strikers
    costs = [[730, 1280, 3880, 0, 0, 0, 0, 0, 0, 0],
             [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570, 0, 0],
             [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],
             [4460, 6470, 7780, 8390, 9500, 0, 0, 0, 0, 0]]
    min_total = 11
    kinds = range(len(num_players))

    model = Model("football")

    # buy[i, j] is 1 when player j of kind i is bought; only real players (price > 0).
    buy = {(i, j): model.binary_var(name=f"buy_{i}_{j}")
           for i in kinds for j in range(max_num_players) if costs[i][j] > 0}

    # The number bought of each kind is within its required range.
    for i in kinds:
        bought = model.sum(buy[i, j] for j in range(max_num_players) if (i, j) in buy)
        model.add_range(min_max[i][0], bought, min_max[i][1])

    # At least eleven players in total.
    model.add_constraint(model.sum(buy.values()) >= min_total)

    # z is the total price, which stays within the budget and is maximised.
    z = model.integer_var(0, budget, name="z")
    model.add_constraint(z == model.sum(costs[i][j] * b for (i, j), b in buy.items()))
    model.maximize(z)

    return model, {"z": z}
