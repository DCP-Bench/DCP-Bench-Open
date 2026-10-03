"""Added corners: place the digits 1..8 in the four corner circles and four side squares of a
3-by-3 frame so that every square holds the sum of the two circles next to it.

    a b c        corners (circles): a, c, f, h
    d   e        sides (squares):   b, d, e, g
    f g h

The model reports the eight values read left to right, top to bottom. The puzzle has no instance
data; the layout is the puzzle's own.
"""
from docplex.mp.model import Model


def build(instance):
    n = 8  # the digits 1..8, one per position (puzzle constant)
    digits = range(1, n + 1)
    places = range(n)

    model = Model("added_corners")

    # put[k, v] = 1 when position k holds digit v. Every position holds one digit and every
    # digit is used once (all different).
    put = {(k, v): model.binary_var(name=f"put_{k}_{v}") for k in places for v in digits}
    for k in places:
        model.add_constraint(model.sum(put[k, v] for v in digits) == 1)
    for v in digits:
        model.add_constraint(model.sum(put[k, v] for k in places) == 1)

    def value(k):
        return model.sum(v * put[k, v] for v in digits)

    a, b, c, d, e, f, g, h = places

    # Each square equals the sum of its two adjoining corner circles.
    model.add_constraint(value(b) == value(a) + value(c))  # top side
    model.add_constraint(value(d) == value(a) + value(f))  # left side
    model.add_constraint(value(e) == value(c) + value(h))  # right side
    model.add_constraint(value(g) == value(f) + value(h))  # bottom side

    return model, {"positions": [value(k) for k in places]}
