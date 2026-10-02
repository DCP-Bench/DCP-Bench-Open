# Zebra puzzle: five houses in a row, each with a different colour, and an inhabitant of a
# different nationality, job, pet and drink. Fifteen clues say who lives next to whom; find the
# house of every colour, nationality, job, pet and drink.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n_houses = 5  # the houses are numbered 0..4 from left to right

    pool = IDPool()

    def houses(name):
        # entry i = the house (0..4) of the i-th member of the category
        return [Integer(f"{name}{i}", 0, n_houses - 1, vpool=pool) for i in range(n_houses)]

    colors = houses("color")
    yellow, green, red, white, blue = colors
    nations = houses("nation")
    italy, spain, japan, england, norway = nations
    jobs = houses("job")
    painter, sculptor, diplomat, pianist, doctor = jobs
    pets = houses("pet")
    cat, zebra, bear, snails, horse = pets
    drinks = houses("drink")
    milk, water, tea, coffee, juice = drinks

    engine = IntegerEngine(vars=colors + nations + jobs + pets + drinks, vpool=pool)

    # within a category every member lives in a different house
    for category in (colors, nations, jobs, pets, drinks):
        engine.add_alldifferent(category)

    # "x is the same house as y"
    same_house = [
        (painter, horse),    # the painter owns the horse
        (diplomat, coffee),  # the diplomat drinks coffee
        (white, milk),       # the one who drinks milk lives in the white house
        (spain, painter),    # the Spaniard is a painter
        (england, red),      # the Englishman lives in the red house
        (snails, sculptor),  # the snails are owned by the sculptor
        (doctor, milk),      # the doctor drinks milk
        (japan, diplomat),   # the diplomat is Japanese
        (norway, zebra),     # the Norwegian owns the zebra
    ]
    for x, y in same_house:
        engine.add_equal(x, y)

    cnf = engine.clausify()

    def require(x, y, holds):
        """The houses (x, y) have to satisfy holds(x, y): every other pair is ruled out."""
        for p in range(n_houses):
            for q in range(n_houses):
                if not holds(p, q):
                    cnf.append([-x.equals(p), -y.equals(q)])

    # the green house is immediately on the left of the red one
    require(green, red, lambda g, r: g + 1 == r)
    # the Norwegian lives immediately on the right of the blue house
    require(blue, norway, lambda b, o: b + 1 == o)
    # the green house is next to the white one
    require(green, white, lambda g, w: abs(g - w) == 1)
    # the horse is owned by the neighbour of the diplomat
    require(diplomat, horse, lambda d, h: abs(d - h) == 1)
    # the Italian lives in the red, white or green house: in whichever house he lives, one of
    # those three colours is that house
    for house in range(n_houses):
        cnf.append([-italy.equals(house), red.equals(house), white.equals(house),
                    green.equals(house)])

    return cnf, {"colors": colors, "nations": nations, "jobs": jobs, "pets": pets,
                 "drinks": drinks}
