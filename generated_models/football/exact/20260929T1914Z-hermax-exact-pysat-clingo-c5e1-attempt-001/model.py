# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in total. The output is the total price in GBP thousands.
from exact import Exact

BUDGET = 30000  # GBP thousands
# The players on offer are fixed by the problem, so their prices (in GBP
# thousands) are mirrored here, one list per position, with the fewest and most
# players that must be bought at that position.
POSITIONS = [
    # goalkeepers: exactly 1
    ((1, 1), [730, 1280, 3880]),
    # defenders: 2 or more
    ((2, None), [920, 1310, 1620, 2410, 2790, 3280, 3910, 4570]),
    # midfielders: 3 or more
    ((3, None), [1800, 2630, 3170, 3769, 4140, 4750, 5380, 5930, 6780, 7130]),
    # strikers: 2 or more
    ((2, None), [4460, 6470, 7780, 8390, 9500]),
]
MIN_PLAYERS = 11  # at least this many players in all


def build(instance):
    solver = Exact()
    # buy[k][j] is 1 when player j of position k is bought
    buy = [[f"buy_{k}_{j}" for j in range(len(prices))] for k, (_, prices) in enumerate(POSITIONS)]
    for row in buy:
        for name in row:
            solver.addVariable(name, 0, 1)

    # the number of players bought at each position lies within its limits
    for k, ((lowest, highest), prices) in enumerate(POSITIONS):
        solver.addConstraint([(1, name) for name in buy[k]], True, lowest,
                             True, highest if highest is not None else len(prices))

    # at least eleven players in total
    solver.addConstraint([(1, name) for row in buy for name in row], True, MIN_PLAYERS)

    # z = total price paid, and it stays within the budget
    priced = [(price, buy[k][j]) for k, (_, prices) in enumerate(POSITIONS) for j, price in enumerate(prices)]
    solver.addVariable("z", 0, BUDGET)
    solver.addConstraint(priced + [(-1, "z")], True, 0, True, 0)

    # spend as much as possible
    return solver, {"z": "z"}, ("maximize", [(1, "z")])
