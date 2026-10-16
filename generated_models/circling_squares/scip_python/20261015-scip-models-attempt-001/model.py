# Circling the squares: place a different whole number (0..99) in each of ten
# squares arranged in a circle (A B C D E F G H I K), so that for any two
# adjacent squares the sum of their squares equals the sum of the squares of the
# two diametrically opposite squares.
from pyscipopt import Model, quicksum

# The four numbers given in the puzzle statement (A=16, B=2, F=8, G=14) are part
# of the problem, not of an instance, so they are fixed here.
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}

# Circle order: positions 0..9. Position i is diametrically opposite position i+5.
NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]

# The statement says no number needs more than two figures and fractions are
# not allowed, so the squares take whole values 0..99.
MAX_VALUE = 99


def build(instance):
    m = Model()
    values = range(MAX_VALUE + 1)

    # one-hot binaries: b[p, v] = 1 if square p holds the number v
    b = {(p, v): m.addVar(name=f"b_{NAMES[p]}_{v}", vtype="B") for p in range(10) for v in values}
    x = {}
    sq = {}
    for p in range(10):
        # each square holds exactly one number
        m.addCons(quicksum(b[p, v] for v in values) == 1, name=f"one_value_{NAMES[p]}")
        x[p] = m.addVar(name=NAMES[p], vtype="I", lb=0, ub=MAX_VALUE)
        sq[p] = m.addVar(name=f"sq_{NAMES[p]}", vtype="I", lb=0, ub=MAX_VALUE * MAX_VALUE)
        # the number and its square, read off the one-hot choice
        m.addCons(x[p] == quicksum(v * b[p, v] for v in values), name=f"value_{NAMES[p]}")
        m.addCons(sq[p] == quicksum(v * v * b[p, v] for v in values), name=f"square_{NAMES[p]}")

    # a different number in each square: each value is used at most once
    # (the statement asks for a different number in each of the ten squares)
    for v in values:
        m.addCons(quicksum(b[p, v] for p in range(10)) <= 1, name=f"all_different_{v}")

    # the four numbers placed as examples must stand as they are
    for name, val in GIVEN.items():
        m.addCons(x[NAMES.index(name)] == val, name=f"given_{name}")

    # for every pair of adjacent squares, the sum of their squares equals the sum
    # of the squares of the two squares diametrically opposite to them
    for p in range(10):
        q = (p + 1) % 10
        o1 = (p + 5) % 10
        o2 = (q + 5) % 10
        m.addCons(sq[p] + sq[q] == sq[o1] + sq[o2],
                  name=f"adjacent_pair_{NAMES[p]}{NAMES[q]}")

    outputs = {NAMES[p]: x[p] for p in range(10)}
    return m, outputs
