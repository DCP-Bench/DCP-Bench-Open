# Match four friends to their allergy and surname.
# The clues are the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    n = 4
    debra, janet, hugh, rick = 0, 1, 2, 3

    sat = Sat()
    foods = sat.ints(n, 0, n - 1)
    surnames = sat.ints(n, 0, n - 1)
    sat.all_different(foods)
    sat.all_different(surnames)

    eggs, mold, nuts, ragweed = foods
    baxter, lemon, malone, fleet = surnames

    sat.clause([-mold.literal(rick)])
    sat.same(eggs, baxter)
    sat.clause([-lemon.literal(hugh)])
    sat.clause([-fleet.literal(hugh)])
    sat.clause([ragweed.literal(debra)])
    sat.clause([-lemon.literal(janet)])
    sat.clause([-eggs.literal(janet)])
    sat.clause([-mold.literal(janet)])

    return sat, {"eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
                 "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet}
