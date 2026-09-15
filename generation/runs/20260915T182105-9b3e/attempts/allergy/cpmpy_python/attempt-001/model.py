import cpmpy as cp


def build(instance):
    """Allergy logic puzzle: match each friend to a surname and an allergy.

    The puzzle states its own four friends and clues, so `instance` is unused.
    Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3, as the reference
    declares and as the declared outputs are read.
    """
    del instance

    n = 4
    debra, janet, hugh, rick = range(n)

    # foods[i] is the friend allergic to the ith food.
    foods = cp.intvar(0, n - 1, shape=n, name="foods")
    eggs, mold, nuts, ragweed = foods
    # surnames[i] is the friend carrying the ith surname.
    surnames = cp.intvar(0, n - 1, shape=n, name="surnames")
    baxter, lemon, malone, fleet = surnames

    model = cp.Model(
        cp.AllDifferent(foods),
        cp.AllDifferent(surnames),
        mold != rick,
        eggs == baxter,
        lemon != hugh,
        fleet != hugh,
        ragweed == debra,
        lemon != janet,
        eggs != janet,
        mold != janet,
    )

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
