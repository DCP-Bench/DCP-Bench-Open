from ortools.sat.python import cp_model


def build(instance):
    """The zebra puzzle: five houses, and five attributes per house.

    The puzzle states its own houses and clues, so `instance` is unused.
    Every variable holds a house number 0..4, so two variables sharing a
    number means those two attributes belong to the same house.
    """
    del instance

    n_houses = 5
    model = cp_model.CpModel()

    def block(prefix):
        return [model.new_int_var(0, n_houses - 1, f"{prefix}{i}")
                for i in range(n_houses)]

    colors = block("color")
    yellow, green, red, white, blue = colors
    nations = block("nation")
    italy, spain, japan, england, norway = nations
    jobs = block("job")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = block("pet")
    cat, zebra, bear, snails, horse = pets
    drinks = block("drink")
    milk, water, tea, coffee, juice = drinks

    for group in (colors, nations, jobs, pets, drinks):
        model.add_all_different(group)

    model.add(painter == horse)
    model.add(diplomat == coffee)
    model.add(white == milk)
    model.add(spain == painter)
    model.add(england == red)
    model.add(snails == sculptor)
    # The green house is immediately left of the red one.
    model.add(green + 1 == red)
    # The Norwegian is immediately right of the blue house.
    model.add(blue + 1 == norway)
    model.add(doctor == milk)
    model.add(japan == diplomat)
    model.add(norway == zebra)

    # The green house is next to the white one, either side.
    gap = model.new_int_var(0, n_houses - 1, "green_white_gap")
    model.add_abs_equality(gap, green - white)
    model.add(gap == 1)

    def equals(variable, expression, name):
        """A Boolean that is true exactly when the two agree."""
        same = model.new_bool_var(name)
        model.add(variable == expression).only_enforce_if(same)
        model.add(variable != expression).only_enforce_if(~same)
        return same

    # The horse belongs to a neighbour of the diplomat.
    model.add_bool_or([
        equals(horse, diplomat - 1, "horse_left"),
        equals(horse, diplomat + 1, "horse_right"),
    ])
    # The Italian lives in the red, white or green house.
    model.add_bool_or([
        equals(italy, red, "italy_red"),
        equals(italy, white, "italy_white"),
        equals(italy, green, "italy_green"),
    ])

    return model, {
        "colors": colors, "nations": nations, "jobs": jobs,
        "pets": pets, "drinks": drinks,
    }
