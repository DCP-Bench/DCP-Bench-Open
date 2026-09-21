# Digits 1..8 around a square, each side cell the sum of its two corners.
# The layout is the puzzle, so the instance carries no fields.
from dcp_sat import Sat


def build(instance):
    n = 8
    sat = Sat()
    p = sat.ints(n, 1, n)
    sat.all_different(p)

    # reading order: a b c / d e / f g h
    a, b, c, d, e, f, g, h = p
    for target, left, right in ((b, a, c), (d, a, f), (e, c, h), (g, f, h)):
        sat.linear_eq([(1, target), (-1, left), (-1, right)], 0)
    return sat, {"positions": p}
