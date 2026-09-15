import cpmpy as cp


def build(instance):
    """The zebra puzzle: five houses, and five attributes per house.

    The puzzle states its own houses and clues, so `instance` is unused.
    Every variable holds a house number 0..4, so two variables sharing a
    number means those two attributes belong to the same house.
    """
    del instance

    n_houses = 5
    colors = cp.intvar(0, n_houses - 1, shape=n_houses, name="colors")
    yellow, green, red, white, blue = colors
    nations = cp.intvar(0, n_houses - 1, shape=n_houses, name="nations")
    italy, spain, japan, england, norway = nations
    jobs = cp.intvar(0, n_houses - 1, shape=n_houses, name="jobs")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = cp.intvar(0, n_houses - 1, shape=n_houses, name="pets")
    cat, zebra, bear, snails, horse = pets
    drinks = cp.intvar(0, n_houses - 1, shape=n_houses, name="drinks")
    milk, water, tea, coffee, juice = drinks

    model = cp.Model(
        cp.AllDifferent(colors),
        cp.AllDifferent(nations),
        cp.AllDifferent(jobs),
        cp.AllDifferent(pets),
        cp.AllDifferent(drinks),
        painter == horse,
        diplomat == coffee,
        white == milk,
        spain == painter,
        england == red,
        snails == sculptor,
        # The green house is immediately left of the red one.
        green + 1 == red,
        # The Norwegian is immediately right of the blue house.
        blue + 1 == norway,
        doctor == milk,
        japan == diplomat,
        norway == zebra,
        # The green house is next to the white one, either side.
        cp.abs(green - white) == 1,
        # The horse belongs to a neighbour of the diplomat.
        (horse == diplomat - 1) | (horse == diplomat + 1),
        (italy == red) | (italy == white) | (italy == green),
    )

    return model, {
        "colors": colors, "nations": nations, "jobs": jobs,
        "pets": pets, "drinks": drinks,
    }
