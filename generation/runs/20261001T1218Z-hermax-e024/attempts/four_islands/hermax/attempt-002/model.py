# Four islands: four islands on a 2x2 map joined by bridges each have a name, an export and
# a tourist attraction. Place each name, export and attraction on the map from six clues.
import functools
import operator

from hermax.model import Model

# Map positions, fixed by the problem: A is north-west, B north-east, C south-west,
# D south-east; bridges join A-B and C-D (east-west) and A-C and B-D (north-south).
A, B, C, D = range(4)


def one_of(m, x, y, placements):
    """Post: (x, y) sits at one of the (position of x, position of y) pairs."""
    options = []
    for px, py in placements:
        option = m.bool()
        m &= (~option | (x == px))
        m &= (~option | (y == py))
        options.append(option)
    m &= functools.reduce(operator.or_, options)


def build(instance):
    # The clues are fixed by the problem; the instance carries no data.
    n = 4

    m = Model()
    # map position of each island name: Pwana, Quero, Rayou, Skern
    island = m.int_vector("island", n, 0, n - 1)
    pwana, quero, rayou, skern = (island[k] for k in range(n))
    # map position of each export: alabaster, bananas, coconuts, durian fruit
    export = m.int_vector("export", n, 0, n - 1)
    alabaster, bananas, coconuts, durian_fruit = (export[k] for k in range(n))
    # map position of each attraction: resort hotel, ice skating rink, jai alai stadium,
    # koala preserve
    attraction = m.int_vector("attraction", n, 0, n - 1)
    resort_hotel, ice_skating_rink, jai_alai_stadium, koala_preserve = (attraction[k] for k in range(n))

    # each island has a different name, export and attraction
    m &= island.all_different()
    m &= export.all_different()
    m &= attraction.all_different()

    # 1. The island with the koala preserve is due south of Pwana.
    one_of(m, pwana, koala_preserve, [(A, C), (B, D)])
    # 2. The island with the alabaster quarry is due west of Quero.
    one_of(m, alabaster, quero, [(A, B), (C, D)])
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    one_of(m, durian_fruit, resort_hotel, [(A, B), (C, D)])
    # 4. Skern and the island with the jai alai stadium are joined by a north-south bridge.
    one_of(m, skern, jai_alai_stadium, [(A, C), (C, A), (B, D), (D, B)])
    # 5. Rayou and the island that exports bananas are joined by an east-west bridge.
    one_of(m, rayou, bananas, [(A, B), (B, A), (C, D), (D, C)])
    # 6. The islands with the ice skating rink and the jai alai stadium are not joined by a
    #    bridge, so they are diagonally opposite.
    one_of(m, ice_skating_rink, jai_alai_stadium, [(A, D), (D, A), (B, C), (C, B)])

    return m, {"island": island, "export": export, "attraction": attraction}
