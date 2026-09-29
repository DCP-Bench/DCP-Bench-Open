# Football squad: buy players for as close to GBP 30 million as possible without
# going over, taking the required number from each position and at least eleven
# players in total. The output is the total price in GBP thousands.
from hermax.model import Model

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
    m = Model()
    # buy[k][j] is true when player j of position k is bought
    buy = [m.bool_vector(f"buy_{k}", len(prices)) for k, (_, prices) in enumerate(POSITIONS)]

    # the number of players bought at each position lies within its limits
    for k, ((lowest, highest), prices) in enumerate(POSITIONS):
        m &= (sum(1 * buy[k][j] for j in range(len(prices))) >= lowest)
        m &= (sum(1 * buy[k][j] for j in range(len(prices))) <= (highest if highest is not None else len(prices)))

    # at least eleven players in total
    m &= (sum(1 * buy[k][j] for k, (_, prices) in enumerate(POSITIONS) for j in range(len(prices))) >= MIN_PLAYERS)

    # z = total price paid, and it stays within the budget. z is a declared output, so it
    # is an integer tied to the sum of the prices of the bought players; its upper bound is
    # the budget, which keeps the encoding of the equality small.
    price_of = [(price, buy[k][j]) for k, (_, prices) in enumerate(POSITIONS) for j, price in enumerate(prices)]
    z = m.int("z", 0, BUDGET)
    m &= (sum(price * bought for price, bought in price_of) == z)

    # Spend as much as possible: a player who is not bought forgoes his price, so the
    # soft clause is the literal itself.
    for price, bought in price_of:
        m.obj[price] += bought

    return m, {"z": z}
