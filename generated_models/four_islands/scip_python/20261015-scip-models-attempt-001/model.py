# Four islands: match each island (Pwana, Quero, Rayou, Skern) with its export and tourist attraction.
# The four islands A, B, C, D form a 2x2 map: A north-west, B north-east, C south-west, D south-east.
from pyscipopt import Model, quicksum

ISLANDS = ["Pwana", "Quero", "Rayou", "Skern"]
EXPORTS = ["alabaster", "bananas", "coconuts", "durian_fruit"]
ATTRACTIONS = ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"]
CATEGORIES = {"island": ISLANDS, "export": EXPORTS, "attraction": ATTRACTIONS}

# map positions 0..3 = A, B, C, D; ROW 0 is north, 1 is south; COL 0 is west, 1 is east
ROW = [0, 0, 1, 1]
COL = [0, 1, 0, 1]


def bridge(p, q):
    # two islands are joined by a bridge when they are neighbours on the map
    return abs(ROW[p] - ROW[q]) + abs(COL[p] - COL[q]) == 1


def due_south(p, q):
    # p is due south of q: same column, p lower on the map
    return COL[p] == COL[q] and ROW[p] > ROW[q]


def due_west(p, q):
    # p is due west of q: same row, p further left
    return ROW[p] == ROW[q] and COL[p] < COL[q]


def due_east(p, q):
    return due_west(q, p)


def north_south_bridge(p, q):
    return COL[p] == COL[q] and bridge(p, q)


def east_west_bridge(p, q):
    return ROW[p] == ROW[q] and bridge(p, q)


def build(instance):
    m = Model()

    # b[c, i, p] = 1 if item i of category c is on map position p
    b = {
        (c, i, p): m.addVar(name=f"{c}_{i}_{p}", vtype="B")
        for c, items in CATEGORIES.items()
        for i in range(len(items))
        for p in range(4)
    }

    # each category places its four items on the four islands, one item per island
    for c, items in CATEGORIES.items():
        # each item is on exactly one island
        for i in range(len(items)):
            m.addCons(quicksum(b[c, i, p] for p in range(4)) == 1)
        # each island carries exactly one item of this category
        for p in range(4):
            m.addCons(quicksum(b[c, i, p] for i in range(len(items))) == 1)

    def link(cat_x, x, cat_y, y, holds):
        # item x of cat_x and item y of cat_y must stand in the relation holds(pos_x, pos_y);
        # forbid every pair of positions that breaks it
        for p in range(4):
            for q in range(4):
                if not holds(p, q):
                    m.addCons(b[cat_x, x, p] + b[cat_y, y, q] <= 1)

    # 1. The island noted for its koala preserve is due south of Pwana.
    link("attraction", 3, "island", 0, due_south)
    # 2. The island with the largest alabaster quarry is due west of Quero.
    link("export", 0, "island", 1, due_west)
    # 3. The island with the resort hotel is due east of the one that exports durian fruit.
    link("attraction", 0, "export", 3, due_east)
    # 4. Skern and the island with the jai alai stadium are connected by a north-south bridge.
    link("island", 3, "attraction", 2, north_south_bridge)
    # 5. Rayou and the island that exports bananas are connected by an east-west bridge.
    link("island", 2, "export", 1, east_west_bridge)
    # 6. The islands with the ice skating rink and the jai alai stadium are not connected by a bridge.
    link("attraction", 1, "attraction", 2, lambda p, q: not bridge(p, q))

    def position(c, i):
        # map position (0=A .. 3=D) of item i of category c
        return quicksum(p * b[c, i, p] for p in range(4))

    outputs = {
        "island": [position("island", i) for i in range(4)],
        "export": [position("export", i) for i in range(4)],
        "attraction": [position("attraction", i) for i in range(4)],
    }
    return m, outputs
