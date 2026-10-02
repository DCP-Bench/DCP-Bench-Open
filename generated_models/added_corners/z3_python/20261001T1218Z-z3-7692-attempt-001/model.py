# Added corners: enter the digits 1 to 8 in the circles and squares of a grid so that the
# number in each square is the sum of the numbers in the two circles next to it:
#   C F C
#   F   F
#   C F C
import z3


def build(instance):
    # Constants of the problem (the instance has no data): eight different digits 1..8, one
    # per position in reading order (left to right, top to bottom).
    n = 8
    positions = [z3.Int(f"positions_{i}") for i in range(n)]
    a, b, c, d, e, f, g, h = positions
    # a, c, f, h are the corner circles, b, d, e, g are the squares in between.

    solver = z3.Solver()

    for p in positions:
        solver.add(p >= 1, p <= n)

    # All the digits are different.
    solver.add(z3.Distinct(positions))

    # Each square is the sum of the two circles next to it: top (b) is between the top corners
    # a and c, left (d) between a and f, right (e) between c and h, bottom (g) between f and h.
    solver.add(b == a + c, d == a + f, e == c + h, g == f + h)

    return solver, {"positions": positions}
