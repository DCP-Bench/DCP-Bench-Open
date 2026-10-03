"""Circling the squares (Dudeney): place a different number in each of ten squares around a circle
so that for any two adjacent squares the sum of the squares of their numbers equals that of the
two diametrically opposite squares. A = 16, B = 2, F = 8 and G = 14 are given.

The model reports the ten numbers A..K. The puzzle has no instance data; the givens and the
range 1..99 ("no number need contain more than two figures") are the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    names = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "K"]  # around the circle
    given = {"A": 16, "B": 2, "F": 8, "G": 14}                   # puzzle givens
    numbers = range(1, 100)

    model = Model("circling_squares")

    # Squares of numbers are not linear, so each open square picks its number one-hot:
    # pick[x, v] = 1 when square x holds v. The four given squares are constants.
    open_squares = [x for x in names if x not in given]
    pick = {(x, v): model.binary_var(name=f"pick_{x}_{v}") for x in open_squares for v in numbers}
    for x in open_squares:
        model.add_constraint(model.sum(pick[x, v] for v in numbers) == 1)

    # All numbers are different: an open square cannot take a given number, and no number is
    # used by two open squares.
    for v in numbers:
        if v in given.values():
            model.add_constraint(model.sum(pick[x, v] for x in open_squares) == 0)
        else:
            model.add_constraint(model.sum(pick[x, v] for x in open_squares) <= 1)

    def value(x):
        if x in given:
            return given[x]
        return model.sum(v * pick[x, v] for v in numbers)

    def square(x):
        if x in given:
            return model.linear_expr(constant=given[x] ** 2)
        return model.sum(v * v * pick[x, v] for v in numbers)

    # For two adjacent squares, the sum of the squares equals that of the opposite pair:
    # A,B ~ F,G; B,C ~ G,H; C,D ~ H,I; D,E ~ I,K; E,F ~ K,A.
    for x1, x2, y1, y2 in [("A", "B", "F", "G"), ("B", "C", "G", "H"), ("C", "D", "H", "I"),
                           ("D", "E", "I", "K"), ("E", "F", "K", "A")]:
        model.add_constraint(square(x1) + square(x2) == square(y1) + square(y2))

    return model, {x: value(x) for x in names}
