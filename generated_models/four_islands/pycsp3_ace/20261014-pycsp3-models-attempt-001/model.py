from pycsp3 import *

# four islands on a 2 by 2 map: A=0 (north west), B=1 (north east), C=2 (south west), D=3 (south east)
# islands are connected by bridges between neighbours in the same row or column
POS = range(4)


def row(p):
    return p // 2


def col(p):
    return p % 2


def pairs(relation):
    # the (p, q) map positions for which the relation holds
    return [(p, q) for p in POS for q in POS if relation(p, q)]


# island[i] is the map position of the island named i: Pwana=0, Quero=1, Rayou=2, Skern=3
island = VarArray(size=4, dom=POS)
# export[j] is the map position of the island with export j: alabaster=0, bananas=1, coconuts=2, durian fruit=3
export = VarArray(size=4, dom=POS)
# attraction[k] is the map position of the island with attraction k: resort hotel=0, ice skating rink=1,
# jai alai stadium=2, koala preserve=3
attraction = VarArray(size=4, dom=POS)

satisfy(
    # each island has a different name, export and attraction
    AllDifferent(island),
    AllDifferent(export),
    AllDifferent(attraction),
    # the island with the koala preserve is due south of Pwana
    Table(scope=[attraction[3], island[0]],
          supports=pairs(lambda p, q: col(p) == col(q) and row(p) > row(q))),
    # the island with the largest alabaster quarry is due west of Quero
    Table(scope=[export[0], island[1]],
          supports=pairs(lambda p, q: row(p) == row(q) and col(p) < col(q))),
    # the island with the resort hotel is due east of the one that exports durian fruit
    Table(scope=[attraction[0], export[3]],
          supports=pairs(lambda p, q: row(p) == row(q) and col(p) > col(q))),
    # Skern and the island with the jai alai stadium are connected by a north-south bridge
    Table(scope=[island[3], attraction[2]],
          supports=pairs(lambda p, q: col(p) == col(q) and abs(row(p) - row(q)) == 1)),
    # Rayou and the island that exports bananas are connected by an east-west bridge
    Table(scope=[island[2], export[1]],
          supports=pairs(lambda p, q: row(p) == row(q) and abs(col(p) - col(q)) == 1)),
    # the islands with the ice skating rink and the jai alai stadium are not connected by a bridge
    Table(scope=[attraction[1], attraction[2]],
          supports=pairs(lambda p, q: not (abs(row(p) - row(q)) + abs(col(p) - col(q)) == 1))),
)
