"""Football: buy players for as close to GBP 30 million as possible without going over,
with exactly one goalkeeper, at least two defenders, three midfielders and two strikers,
and at least eleven players in all.

The model reports the total price z in GBP thousands.
"""
import pulp


def build(instance):
    del instance  # the problem has no instance data; its prices are below

    # Problem data, mirrored from the reference (prices in GBP thousands).
    budget = 30000
    costs = [
        [730, 1280, 3880],                                                # goalkeepers
        [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570],                  # defenders
        [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130],     # midfielders
        [4460, 6470, 7780, 8390, 9500],                                   # strikers
    ]
    # how many of each type to buy: [least, most]
    most = max(len(group) for group in costs)
    min_max = [[1, 1], [2, most], [3, most], [2, most]]
    min_players = 11

    problem = pulp.LpProblem("football", pulp.LpMaximize)

    # buy[k][j] = 1 if player j of type k is bought
    buy = [[pulp.LpVariable(f"buy_{k}_{j}", cat="Binary") for j in range(len(group))]
           for k, group in enumerate(costs)]

    # the number of each type bought lies within its limits
    for k, (least, upper) in enumerate(min_max):
        problem += pulp.lpSum(buy[k]) >= least
        problem += pulp.lpSum(buy[k]) <= upper

    # at least eleven players in total
    problem += pulp.lpSum(var for group in buy for var in group) >= min_players

    # z is the total price, which may not exceed the budget
    z = pulp.LpVariable("z", 0, budget, cat="Integer")
    problem += z == pulp.lpSum(costs[k][j] * buy[k][j]
                               for k in range(len(costs)) for j in range(len(costs[k])))

    # spend as much as possible
    problem += z

    return problem, {"z": z}
