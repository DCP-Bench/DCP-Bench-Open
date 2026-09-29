# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in total. The output is the total price in GBP thousands.
from ortools.sat.python import cp_model

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
    model = cp_model.CpModel()

    # buy[k][j] is true when player j of position k is bought
    buy = [[model.new_bool_var(f"buy_{k}_{j}") for j in range(len(prices))] for k, (_, prices) in enumerate(POSITIONS)]

    # the number of players bought at each position lies within its limits
    for k, ((lowest, highest), prices) in enumerate(POSITIONS):
        model.add(sum(buy[k]) >= lowest)
        model.add(sum(buy[k]) <= (highest if highest is not None else len(prices)))

    # at least eleven players in total
    model.add(sum(sum(row) for row in buy) >= MIN_PLAYERS)

    # z = total price paid, and it stays within the budget
    z = model.new_int_var(0, BUDGET, "z")
    model.add(z == sum(price * buy[k][j] for k, (_, prices) in enumerate(POSITIONS) for j, price in enumerate(prices)))

    # spend as much as possible
    model.maximize(z)

    return model, {"z": z}
