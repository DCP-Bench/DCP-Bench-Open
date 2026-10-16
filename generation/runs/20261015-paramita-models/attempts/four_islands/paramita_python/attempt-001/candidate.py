# Four islands: Pwana, Quero, Rayou and Skern each have a different export and a
# different tourist attraction, placed on the 2x2 map A B / C D.
# Positions are encoded A=0, B=1, C=2, D=3, so row = p // 2 and column = p % 2.
# Every island, export and attraction gets a one-hot position over the four map positions.
from paramita.modelling import Bool

ISLANDS = ["Pwana", "Quero", "Rayou", "Skern"]
EXPORTS = ["alabaster", "bananas", "coconuts", "durian_fruit"]
ATTRACTIONS = ["resort_hotel", "ice_skating_rink", "jai_alai_stadium", "koala_preserve"]
POS = range(4)


def row(p):
    return p // 2


def col(p):
    return p % 2


def build(instance):
    cons = []

    # each island is on a different map position
    isl = [[Bool(f"isl_{k}_{p}") for p in POS] for k in range(4)]
    cons += [sum(isl[k]) == 1 for k in range(4)]
    cons += [sum(isl[k][p] for k in range(4)) == 1 for p in POS]

    # each export is on a different map position
    exp = [[Bool(f"exp_{j}_{p}") for p in POS] for j in range(4)]
    cons += [sum(exp[j]) == 1 for j in range(4)]
    cons += [sum(exp[j][p] for j in range(4)) == 1 for p in POS]

    # each tourist attraction is on a different map position
    att = [[Bool(f"att_{j}_{p}") for p in POS] for j in range(4)]
    cons += [sum(att[j]) == 1 for j in range(4)]
    cons += [sum(att[j][p] for j in range(4)) == 1 for p in POS]

    def require(x, y, ok):
        # a thing at position p and a thing at position q must satisfy ok(p, q)
        for p in POS:
            for q in POS:
                if not ok(p, q):
                    cons.append(~(x[p] & y[q]))

    # the island noted for its koala preserve is due south of Pwana
    require(isl[0], att[3], lambda p, q: col(p) == col(q) and row(q) == row(p) + 1)

    # the island with the largest alabaster quarry is due west of Quero
    require(exp[0], isl[1], lambda p, q: row(p) == row(q) and col(p) < col(q))

    # the island with the resort hotel is due east of the one that exports durian fruit
    require(att[0], exp[3], lambda p, q: row(p) == row(q) and col(p) > col(q))

    # Skern and the island with the jai alai stadium are connected by a north-south bridge
    require(isl[3], att[2], lambda p, q: col(p) == col(q) and row(p) != row(q))

    # Rayou and the island that exports bananas are connected by an east-west bridge
    require(isl[2], exp[1], lambda p, q: row(p) == row(q) and col(p) != col(q))

    # the ice skating rink and the jai alai stadium are not connected by a bridge
    require(att[1], att[2], lambda p, q: row(p) != row(q) and col(p) != col(q))

    def value(group):
        return [sum(p * group[k][p] for p in POS) for k in range(len(group))]

    return cons, {
        "island": value(isl),
        "export": value(exp),
        "attraction": value(att),
    }
