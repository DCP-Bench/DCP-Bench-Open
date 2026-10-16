# Added corners: put the digits 1 to 8 in the 8 positions of a figure (four circles at
# the corners, four squares at the edge midpoints) so that each square holds the sum
# of the two circles next to it. Positions are read left to right, top to bottom.
from pyscipopt import Model, quicksum


def build(instance):
    # The figure is fixed by the problem: 8 positions, digits 1 through 8.
    n = 8
    digits = range(1, n + 1)
    m = Model()

    # value of each position, 0 = top left, 7 = bottom right in reading order
    pos = [m.addVar(name=f"p{i}", vtype="I", lb=1, ub=n) for i in range(n)]

    # one-hot choice: position i holds digit v when b[i, v] = 1
    b = {(i, v): m.addVar(name=f"b{i}_{v}", vtype="B") for i in range(n) for v in digits}
    # each position holds exactly one digit
    for i in range(n):
        m.addCons(quicksum(b[i, v] for v in digits) == 1)
        m.addCons(pos[i] == quicksum(v * b[i, v] for v in digits))

    # the digits 1 through 8 are each used once
    for v in digits:
        m.addCons(quicksum(b[i, v] for i in range(n)) == 1)

    # circles are at the corners: positions 0, 2, 5, 7
    # squares are at the edge midpoints: positions 1, 3, 4, 6
    # the top square (1) is the sum of the circles next to it (0 and 2)
    m.addCons(pos[1] == pos[0] + pos[2])
    # the left square (3) is the sum of the circles above and below it (0 and 5)
    m.addCons(pos[3] == pos[0] + pos[5])
    # the right square (4) is the sum of the circles above and below it (2 and 7)
    m.addCons(pos[4] == pos[2] + pos[7])
    # the bottom square (6) is the sum of the circles next to it (5 and 7)
    m.addCons(pos[6] == pos[5] + pos[7])

    return m, {"positions": pos}
