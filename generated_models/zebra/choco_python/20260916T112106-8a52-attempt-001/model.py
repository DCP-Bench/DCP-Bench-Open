from pychoco.model import Model


def build(instance):
    """The zebra puzzle: five houses, and five attributes per house.

    Every variable holds a house number 0..4, so two variables sharing a number
    means those two attributes belong to the same house.
    """
    del instance

    n = 5
    model = Model()

    def block(prefix):
        return [model.intvar(0, n - 1, name=f"{prefix}{i}") for i in range(n)]

    colors = block("colour")
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
        model.all_different(group).post()

    for left, right in ((painter, horse), (diplomat, coffee), (white, milk),
                        (spain, painter), (england, red), (snails, sculptor),
                        (doctor, milk), (japan, diplomat), (norway, zebra)):
        model.arithm(left, "=", right).post()

    # The green house is immediately left of the red one.
    model.scalar([green, red], [1, -1], "=", -1).post()
    # The Norwegian is immediately right of the blue house.
    model.scalar([blue, norway], [1, -1], "=", -1).post()
    # The green house is next to the white one, either side.
    model.distance(green, white, "=", 1).post()
    # The horse belongs to a neighbour of the diplomat.
    model.distance(horse, diplomat, "=", 1).post()
    # The Italian lives in the red, white or green house.
    model.or_([
        model.arithm(italy, "=", red),
        model.arithm(italy, "=", white),
        model.arithm(italy, "=", green),
    ]).post()

    return model, {
        "colors": colors, "nations": nations, "jobs": jobs,
        "pets": pets, "drinks": drinks,
    }
