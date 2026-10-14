# Hanging weights: thirteen weights A-M hang from a system of bars, each weight
# an integer from 1 to 13. Find the weights for which every bar balances.
import z3


def build(instance):
    del instance  # the puzzle states its own diagram

    N = 13
    a, b, c, d, e, f, g, h, i, j, k, l, m = weights = z3.Ints("a b c d e f g h i j k l m")

    solver = z3.Solver()

    # Each weight has an integer value between 1 and 13, and all weights differ.
    for w in weights:
        solver.add(w >= 1, w <= N)
    solver.add(z3.Distinct(weights))

    # Bottom bars: on each, the weights on both sides of the pivot balance when
    # multiplied by their distance from it.
    solver.add(4 * a == b)
    solver.add(5 * c == d)
    solver.add(3 * e == 2 * f)

    # A bar hanging beneath another counts as one weight equal to its total, so
    # the bars above use the sums of the weights hanging below them.
    # Bar of G, with the bar (C, D) hanging below it:
    solver.add(3 * g == 2 * (c + d))
    # Bar of J and K, with the bars (A, B) and (G, C, D) hanging below it:
    solver.add(3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    # Bar of H and I, with the bar (E, F) hanging below it:
    solver.add(3 * h == 2 * (e + f) + 3 * i)
    # Bar of L and M, with the system (H, I, E, F) hanging from it:
    solver.add((h + i + e + f) == l + 4 * m)
    # Top bar: everything hanging on one side balances everything on the other.
    solver.add(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))

    return solver, {"a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
                    "h": h, "i": i, "j": j, "k": k, "l": l, "m": m}
