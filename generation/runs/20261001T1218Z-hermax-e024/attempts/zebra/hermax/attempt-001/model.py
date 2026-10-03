# Zebra (Einstein's puzzle): five houses in a row, each with a colour, an inhabitant's
# nationality, pet, drink and job, all different. Place everything from the clues.
import functools
import operator

from hermax.model import Model


def offset_options(m, x, y, offsets, n):
    """Post: x == y + d for one of the offsets d, all values in 0..n-1."""
    options = []
    for d in offsets:
        option = m.bool()
        for v in range(n):
            if 0 <= v + d < n:
                m &= (~option | ~(y == v) | (x == v + d))
            else:
                m &= (~option | ~(y == v))
        options.append(option)
    m &= functools.reduce(operator.or_, options)


def build(instance):
    # The clues are fixed by the problem; the instance carries no data.
    n = 5  # houses 0..4, left to right

    m = Model()
    # each vector gives the house of each item
    colors = m.int_vector("colors", n, 0, n - 1)    # yellow, green, red, white, blue
    nations = m.int_vector("nations", n, 0, n - 1)  # italy, spain, japan, england, norway
    jobs = m.int_vector("jobs", n, 0, n - 1)        # painter, sculptor, diplomat, pianist, doctor
    pets = m.int_vector("pets", n, 0, n - 1)        # cat, zebra, bear, snails, horse
    drinks = m.int_vector("drinks", n, 0, n - 1)    # milk, water, tea, coffee, juice
    yellow, green, red, white, blue = (colors[k] for k in range(n))
    italy, spain, japan, england, norway = (nations[k] for k in range(n))
    painter, sculptor, diplomat, pianist, doctor = (jobs[k] for k in range(n))
    cat, zebra, bear, snails, horse = (pets[k] for k in range(n))
    milk, water, tea, coffee, juice = (drinks[k] for k in range(n))

    # each house has a different colour, nationality, job, pet and drink
    for vector in (colors, nations, jobs, pets, drinks):
        m &= vector.all_different()

    m &= (painter == horse)     # the painter owns the horse
    m &= (diplomat == coffee)   # the diplomat drinks coffee
    m &= (white == milk)        # the one who drinks milk lives in the white house
    m &= (spain == painter)     # the Spaniard is a painter
    m &= (england == red)       # the Englishman lives in the red house
    m &= (snails == sculptor)   # the snails are owned by the sculptor
    m &= (green + 1 == red)     # the green house is immediately left of the red one
    m &= (blue + 1 == norway)   # the Norwegian lives immediately right of the blue house
    m &= (doctor == milk)       # the doctor drinks milk
    m &= (japan == diplomat)    # the diplomat is Japanese
    m &= (norway == zebra)      # the Norwegian owns the zebra
    # the green house is next to the white one
    offset_options(m, green, white, (-1, 1), n)
    # the horse is owned by the neighbour of the diplomat
    offset_options(m, horse, diplomat, (-1, 1), n)
    # the Italian lives in the red, white or green house
    options = []
    for house in (red, white, green):
        option = m.bool()
        for v in range(n):
            m &= (~option | ~(house == v) | (italy == v))
        options.append(option)
    m &= functools.reduce(operator.or_, options)

    return m, {"colors": colors, "nations": nations, "jobs": jobs, "pets": pets, "drinks": drinks}
