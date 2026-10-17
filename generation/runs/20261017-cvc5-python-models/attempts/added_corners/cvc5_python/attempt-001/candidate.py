# added_corners: enter the digits 1 through 8 in the circles and squares of a
# 3x3 layout (centre empty, corners are circles, edge midpoints are squares) so that
# the number in each square equals the sum of the adjoining circles.
# Output: the eight values read left to right, top to bottom.
import cvc5.pythonic as cz


def build(instance):
    # Positions in reading order:
    #   0 1 2
    #   3 _ 4
    #   5 6 7
    # Circles: 0, 2, 5, 7. Squares: 1, 3, 4, 6.
    p = cz.Ints(" ".join(f"p{i}" for i in range(8)))

    # Digits: each position holds a digit from 1 to 8.
    # cvc5 integers are unbounded, so the bounds must be added.
    domain = [cz.And(v >= 1, v <= 8) for v in p]

    # Enter the digits 1 through 8, each used exactly once.
    all_different = [cz.Distinct(p)]

    # Each square holds the sum of the circles it adjoins.
    # Top square (1) adjoins the top-left and top-right circles.
    # Left square (3) adjoins the top-left and bottom-left circles.
    # Right square (4) adjoins the top-right and bottom-right circles.
    # Bottom square (6) adjoins the bottom-left and bottom-right circles.
    square_sums = [
        p[1] == p[0] + p[2],
        p[3] == p[0] + p[5],
        p[4] == p[2] + p[7],
        p[6] == p[5] + p[7],
    ]

    constraints = domain + all_different + square_sums
    return constraints, {"positions": [p[i] for i in range(8)]}
