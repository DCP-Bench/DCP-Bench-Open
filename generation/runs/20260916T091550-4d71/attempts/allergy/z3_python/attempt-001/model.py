import z3


def build(instance):
    """Allergy logic puzzle: match each friend to a surname and an allergy.

    The puzzle states its own four friends and clues, so it carries no instance
    data.  Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3, as the
    declared outputs are read.
    """
    del instance

    n = 4
    debra, janet, hugh, rick = range(n)

    # foods[i] is the friend allergic to the ith food.
    eggs, mold, nuts, ragweed = foods = z3.Ints("eggs mold nuts ragweed")
    # surnames[i] is the friend carrying the ith surname.
    baxter, lemon, malone, fleet = surnames = z3.Ints("baxter lemon malone fleet")

    solver = z3.Solver()
    for value in list(foods) + list(surnames):
        solver.add(value >= 0, value <= n - 1)
    solver.add(z3.Distinct(foods))
    solver.add(z3.Distinct(surnames))

    solver.add(mold != rick)
    solver.add(eggs == baxter)
    solver.add(lemon != hugh)
    solver.add(fleet != hugh)
    solver.add(ragweed == debra)
    solver.add(lemon != janet)
    solver.add(eggs != janet)
    solver.add(mold != janet)

    return solver, {
        "eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
        "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet,
    }
