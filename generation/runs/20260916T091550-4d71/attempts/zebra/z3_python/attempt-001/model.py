import z3


def build(instance):
    """The zebra puzzle: five houses, and five attributes per house.

    Every variable holds a house number 0..4, so two variables sharing a number
    means those two attributes belong to the same house.
    """
    del instance

    n_houses = 5
    colors = z3.Ints("yellow green red white blue")
    yellow, green, red, white, blue = colors
    nations = z3.Ints("italy spain japan england norway")
    italy, spain, japan, england, norway = nations
    jobs = z3.Ints("painter sculptor diplomat pianist doctor")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = z3.Ints("cat zebra bear snails horse")
    cat, zebra, bear, snails, horse = pets
    drinks = z3.Ints("milk water tea coffee juice")
    milk, water, tea, coffee, juice = drinks

    solver = z3.Solver()
    for group in (colors, nations, jobs, pets, drinks):
        for value in group:
            solver.add(value >= 0, value <= n_houses - 1)
        solver.add(z3.Distinct(group))

    solver.add(painter == horse)
    solver.add(diplomat == coffee)
    solver.add(white == milk)
    solver.add(spain == painter)
    solver.add(england == red)
    solver.add(snails == sculptor)
    # The green house is immediately left of the red one.
    solver.add(green + 1 == red)
    # The Norwegian is immediately right of the blue house.
    solver.add(blue + 1 == norway)
    solver.add(doctor == milk)
    solver.add(japan == diplomat)
    solver.add(norway == zebra)
    # The green house is next to the white one, either side.
    solver.add(z3.Abs(green - white) == 1)
    # The horse belongs to a neighbour of the diplomat.
    solver.add(z3.Or(horse == diplomat - 1, horse == diplomat + 1))
    # The Italian lives in the red, white or green house.
    solver.add(z3.Or(italy == red, italy == white, italy == green))

    return solver, {
        "colors": list(colors), "nations": list(nations), "jobs": list(jobs),
        "pets": list(pets), "drinks": list(drinks),
    }
