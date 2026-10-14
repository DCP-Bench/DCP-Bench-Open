# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in total. The output is the total price in GBP thousands.
import z3

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
    solver = z3.Solver()

    # buy[k][j] is true when player j of position k is bought
    buy = [[z3.Bool(f"buy_{k}_{j}") for j in range(len(prices))] for k, (_, prices) in enumerate(POSITIONS)]

    # the number of players bought at each position lies within its limits
    for k, ((lowest, highest), prices) in enumerate(POSITIONS):
        solver.add(z3.AtLeast(*buy[k], lowest))
        solver.add(z3.AtMost(*buy[k], highest if highest is not None else len(prices)))

    # at least eleven players in total
    everyone = [b for row in buy for b in row]
    solver.add(z3.AtLeast(*everyone, MIN_PLAYERS))

    # z = total price paid, and it stays within the budget
    z = z3.Int("z")
    solver.add(z >= 0, z <= BUDGET)
    solver.add(z == z3.Sum([z3.If(b, price, 0) for b, price in zip(everyone, [p for _, ps in POSITIONS for p in ps])]))

    # spend as much as possible
    return solver, {"z": z}, ("maximize", z)
