# SEND + MORE = MONEY: each letter stands for a different digit, the first letter
# of each word is not zero, and the sum must hold.
import z3


def build(instance):
    del instance  # the puzzle states its own words

    s, e, n, d, m, o, r, y = letters = z3.Ints("s e n d m o r y")

    solver = z3.Solver()

    # Each letter is a digit from 0 to 9, and different letters are different digits.
    for v in letters:
        solver.add(v >= 0, v <= 9)
    solver.add(z3.Distinct(letters))

    # The first letter of each word cannot be zero.
    solver.add(s > 0, m > 0)

    # SEND + MORE = MONEY, with each word read as a decimal number.
    solver.add(
        1000 * s + 100 * e + 10 * n + d
        + 1000 * m + 100 * o + 10 * r + e
        == 10000 * m + 1000 * o + 100 * n + 10 * e + y
    )

    return solver, {"s": s, "e": e, "n": n, "d": d, "m": m, "o": o, "r": r, "y": y}
