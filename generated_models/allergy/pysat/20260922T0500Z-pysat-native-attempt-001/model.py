# Match four friends to their allergy and surname.
# The clues are the puzzle, so the instance carries no fields.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = 4
    debra, janet, hugh, rick = 0, 1, 2, 3

    pool = IDPool()
    foods = [Integer(f"food{i}", 0, n - 1, vpool=pool) for i in range(n)]
    surnames = [Integer(f"surname{i}", 0, n - 1, vpool=pool) for i in range(n)]
    engine = IntegerEngine(vars=foods + surnames, vpool=pool)
    engine.add_alldifferent(foods)
    engine.add_alldifferent(surnames)

    eggs, mold, nuts, ragweed = foods
    baxter, lemon, malone, fleet = surnames

    engine.add_equal(eggs, baxter)
    cnf = engine.clausify()
    # The remaining clues fix or forbid single values, which is one unit clause
    # each over the direct encoding's value literals.
    for variable, person in ((mold, rick), (lemon, hugh), (fleet, hugh),
                             (lemon, janet), (eggs, janet), (mold, janet)):
        cnf.append([-variable.equals(person)])
    cnf.append([ragweed.equals(debra)])

    return cnf, {"eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
                 "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet}
