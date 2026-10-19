# Circling the squares: place a different integer in each of ten squares
# A B C D E F G H I K arranged in a circle, in this order (K next to A).
# The four numbers A=16, B=2, F=8, G=14 are given and stand as they are.
# Fractions are not allowed, and no number needs more than two figures,
# so every square holds an integer from 0 to 99.

import cvc5.pythonic as cz

NAMES = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]
LOW, HIGH = 0, 99
GIVEN = {"A": 16, "B": 2, "F": 8, "G": 14}


def build(instance):
    n = len(NAMES)
    values = list(range(LOW, HIGH + 1))

    # Each square holds exactly one value. A Boolean per (square, value)
    # keeps the squares linear: the square of a value is a constant.
    hold = [[cz.Bool(f"h_{i}_{v}") for v in values] for i in range(n)]
    x = [cz.Int(f"x_{i}") for i in range(n)]
    sq = [cz.Int(f"sq_{i}") for i in range(n)]

    constraints = []

    # The number in each square is one of the allowed integers.
    for i in range(n):
        constraints.append(cz.Sum([cz.If(hold[i][k], 1, 0) for k in range(len(values))]) == 1)
        constraints.append(x[i] == cz.Sum([cz.If(hold[i][k], v, 0) for k, v in enumerate(values)]))
        constraints.append(sq[i] == cz.Sum([cz.If(hold[i][k], v * v, 0) for k, v in enumerate(values)]))

    # Place a different number in each of the ten squares.
    constraints.append(cz.Distinct(x))

    # The four numbers given in the description.
    for name, value in GIVEN.items():
        constraints.append(x[NAMES.index(name)] == value)

    # The sum of the squares of any two adjacent numbers equals the sum of the
    # squares of the two numbers diametrically opposite to them on the circle.
    for i in range(n):
        constraints.append(sq[i] + sq[(i + 1) % n] == sq[(i + 5) % n] + sq[(i + 6) % n])

    outputs = {name: x[i] for i, name in enumerate(NAMES)}
    return constraints, outputs
