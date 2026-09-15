from ortools.sat.python import cp_model


def build(instance):
    """Allergy logic puzzle: match each friend to a surname and an allergy.

    The puzzle states its own four friends and clues, so `instance` is unused.
    Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3, as the reference
    declares and as the declared outputs are read.
    """
    del instance

    n = 4
    debra, janet, hugh, rick = range(n)

    model = cp_model.CpModel()
    # foods[i] is the friend allergic to the ith food.
    foods = [model.new_int_var(0, n - 1, f"food{i}") for i in range(n)]
    eggs, mold, nuts, ragweed = foods
    # surnames[i] is the friend carrying the ith surname.
    surnames = [model.new_int_var(0, n - 1, f"surname{i}") for i in range(n)]
    baxter, lemon, malone, fleet = surnames

    model.add_all_different(foods)
    model.add_all_different(surnames)
    model.add(mold != rick)
    model.add(eggs == baxter)
    model.add(lemon != hugh)
    model.add(fleet != hugh)
    model.add(ragweed == debra)
    model.add(lemon != janet)
    model.add(eggs != janet)
    model.add(mold != janet)

    return model, {
        "eggs": eggs,
        "mold": mold,
        "nuts": nuts,
        "ragweed": ragweed,
        "baxter": baxter,
        "lemon": lemon,
        "malone": malone,
        "fleet": fleet,
    }
