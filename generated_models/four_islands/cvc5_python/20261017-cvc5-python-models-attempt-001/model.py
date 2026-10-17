# four_islands: A tiny nation in the South Pacific contains four islands connected by bridges.
# Each island (Pwana, Quero, Rayou, Skern) has a different primary export (alabaster,
# bananas, coconuts, durian fruit) and a different tourist attraction (hotel, ice skating
# rink, jai alai stadium, koala preserve). Find the name, export and attraction of each island.
#
# Map positions: A=0, B=1, C=2, D=3 on a 2x2 grid:
#   (A) -- (B)
#    |      |
#   (C) -- (D)
# Bridges: A-B, A-C, B-D, C-D. A is north of C, C is west of D, and so on.
import cvc5.pythonic as cz

# (x, y) pairs of map positions, with the relation named in each comment.
SOUTH = [(0, 2), (1, 3)]  # y is due south of x
WEST = [(0, 1), (2, 3)]  # x is due west of y
EAST = [(1, 0), (3, 2)]  # x is due east of y
NS_BRIDGE = [(0, 2), (2, 0), (1, 3), (3, 1)]  # north-south bridge, either direction
EW_BRIDGE = [(0, 1), (1, 0), (2, 3), (3, 2)]  # east-west bridge, either direction
DIAGONAL = [(0, 3), (3, 0), (1, 2), (2, 1)]  # no bridge between the two


def pair_in(x, y, allowed):
    return cz.Or([cz.And(x == a, y == b) for a, b in allowed])


def build(instance):
    # island[i]: map position of the island named i (0 Pwana, 1 Quero, 2 Rayou, 3 Skern).
    island = cz.Ints(["island_pwana", "island_quero", "island_rayou", "island_skern"])
    # export[j]: map position of the island whose export is j
    # (0 alabaster, 1 bananas, 2 coconuts, 3 durian fruit).
    export = cz.Ints(["export_alabaster", "export_bananas", "export_coconuts", "export_durian"])
    # attraction[k]: map position of the island with attraction k
    # (0 resort hotel, 1 ice skating rink, 2 jai alai stadium, 3 koala preserve).
    attraction = cz.Ints(["attr_hotel", "attr_rink", "attr_jai_alai", "attr_koala"])

    constraints = []

    # Each island, export and attraction is a permutation of the four map positions.
    for group in (island, export, attraction):
        constraints += [v >= 0 for v in group]
        constraints += [v <= 3 for v in group]
        constraints.append(cz.Distinct(group))

    # The island noted for its koala preserve is due south of Pwana.
    constraints.append(pair_in(island[0], attraction[3], SOUTH))

    # The island with the largest alabaster quarry is due west of Quero.
    constraints.append(pair_in(export[0], island[1], WEST))

    # The island with the resort hotel is due east of the one that exports durian fruit.
    constraints.append(pair_in(attraction[0], export[3], EAST))

    # Skern and the island with the jai alai stadium are connected by a north-south bridge.
    constraints.append(pair_in(island[3], attraction[2], NS_BRIDGE))

    # Rayou and the island that exports bananas are connected by an east-west bridge.
    constraints.append(pair_in(island[2], export[1], EW_BRIDGE))

    # The islands noted for the ice skating rink and for the jai alai stadium are not
    # connected by a bridge.
    constraints.append(pair_in(attraction[1], attraction[2], DIAGONAL))

    outputs = {
        "island": island,
        "export": export,
        "attraction": attraction,
    }
    return constraints, outputs
