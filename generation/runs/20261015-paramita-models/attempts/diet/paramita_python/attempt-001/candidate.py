"""Diet: choose units of four foods that meet the nutrition minimums at the lowest cost.

Each food j has an integer number of units. Units are encoded in unary: the
Bool x[j][v] means the food j is bought at least v+1 times, and the number of
units is the sum of its Bools. Each unary chain is ordered (x[j][v] implies
x[j][v-1]).
"""

from paramita.modelling import Bool, If

# The nutrition table of the problem (fixed by the problem statement, not by the instance).
# Rows are nutrients in the order calories, chocolate (ounces), sugar (ounces), fat (ounces).
# Columns are foods in the order chocolate cake, chocolate ice cream, cola, pineapple cheesecake.
NUTRIENTS = [
    [400, 200, 150, 500],  # calories
    [3, 2, 0, 0],          # chocolate (ounces)
    [2, 2, 4, 4],          # sugar (ounces)
    [2, 4, 1, 5],          # fat (ounces)
]


def build(instance):
    n = instance["n"]
    price = instance["price"]
    limits = instance["limits"]
    assert len(price) == n and len(NUTRIENTS[0]) == n

    # upper bound on the units of each food: beyond ub[j] units, removing one unit
    # keeps every requirement satisfied and does not raise the cost, so an optimal
    # diet with at most ub[j] units of food j always exists (also when a price is 0)
    ub = []
    for j in range(n):
        bounds = [-(-limits[k] // NUTRIENTS[k][j]) for k in range(len(limits)) if NUTRIENTS[k][j] > 0]
        ub.append(max(bounds, default=0))

    # unary units: units[j][v] is true when food j is bought at least v+1 times
    units = [[Bool(f"units_{j}_ge_{v + 1}") for v in range(ub[j])] for j in range(n)]

    cons = []
    # the unary chain is ordered: at least v+2 units implies at least v+1 units
    for j in range(n):
        for v in range(1, ub[j]):
            cons.append(If(units[j][v], units[j][v - 1]))

    # total units of food j is the number of true Bools in its chain
    # every nutrient requirement is met: total nutrient of each type is at least the minimum
    for k in range(len(limits)):
        total = sum(NUTRIENTS[k][j] * b for j in range(n) for b in units[j])
        if isinstance(total, int):
            # no food contains this nutrient or no units are allowed: the minimum must be 0
            assert limits[k] <= 0
            continue
        cons.append(total >= limits[k])

    # cost of the products: price times units, summed over the foods
    cost = sum(price[j] * b for j in range(n) for b in units[j])
    return cons, {"cost": cost}, ("minimize", cost)
