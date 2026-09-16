from pychoco.model import Model


def build(instance):
    """Allergy logic puzzle: match each friend to a surname and an allergy.

    Friends are numbered Debra 0, Janet 1, Hugh 2, Rick 3, as the declared
    outputs are read.
    """
    del instance

    n = 4
    debra, janet, hugh, rick = range(n)

    model = Model()
    # foods[i] is the friend allergic to the ith food.
    foods = [model.intvar(0, n - 1, name=f"food{i}") for i in range(n)]
    eggs, mold, nuts, ragweed = foods
    # surnames[i] is the friend carrying the ith surname.
    surnames = [model.intvar(0, n - 1, name=f"surname{i}") for i in range(n)]
    baxter, lemon, malone, fleet = surnames

    model.all_different(foods).post()
    model.all_different(surnames).post()

    model.arithm(mold, "!=", rick).post()
    model.arithm(eggs, "=", baxter).post()
    model.arithm(lemon, "!=", hugh).post()
    model.arithm(fleet, "!=", hugh).post()
    model.arithm(ragweed, "=", debra).post()
    model.arithm(lemon, "!=", janet).post()
    model.arithm(eggs, "!=", janet).post()
    model.arithm(mold, "!=", janet).post()

    return model, {
        "eggs": eggs, "mold": mold, "nuts": nuts, "ragweed": ragweed,
        "baxter": baxter, "lemon": lemon, "malone": malone, "fleet": fleet,
    }
