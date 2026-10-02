# Added corners: write the digits 1 to 8 in the eight circles (C) and squares (F) around a frame
#   C F C
#   F   F
#   C F C
# so that the number in each square equals the sum of the numbers in the two circles next to it.
from exact import Exact


def build(instance):
    # This problem has no instance data. The eight digits 1..8 belong to the problem statement.
    n = 8

    solver = Exact()

    # positions[0..7] = values read left to right, top to bottom: a b c / d e / f g h
    positions = [f"position_{i}" for i in range(n)]
    for name in positions:
        solver.addVariable(name, 1, n)
    a, b, c, d, e, f, g, h = positions

    # all different: each digit 1..n is used exactly once. Exact is linear, so every position has one
    # 0/1 variable per digit, and each digit is taken by exactly one position (n positions, n digits).
    is_digit = [[f"position_{i}_is_{v}" for v in range(1, n + 1)] for i in range(n)]
    for i in range(n):
        for name in is_digit[i]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in is_digit[i]], True, 1, True, 1)
        solver.addConstraint([(v, is_digit[i][v - 1]) for v in range(1, n + 1)]
                             + [(-1, positions[i])], True, 0, True, 0)
    for v in range(1, n + 1):
        solver.addConstraint([(1, is_digit[i][v - 1]) for i in range(n)], True, 1, True, 1)

    # each square is the sum of the two circles next to it
    solver.addConstraint([(1, b), (-1, a), (-1, c)], True, 0, True, 0)  # b = a + c
    solver.addConstraint([(1, d), (-1, a), (-1, f)], True, 0, True, 0)  # d = a + f
    solver.addConstraint([(1, e), (-1, c), (-1, h)], True, 0, True, 0)  # e = c + h
    solver.addConstraint([(1, g), (-1, f), (-1, h)], True, 0, True, 0)  # g = f + h

    return solver, {"positions": positions}
