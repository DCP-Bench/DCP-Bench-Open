# Circling the squares (Dudeney): put a different number in each of ten squares
# around a circle so that the sum of squares of any two adjacent numbers equals
# the sum of squares of the two numbers diametrically opposite them.
import z3


def build(instance):
    del instance  # the puzzle states its own given numbers

    # Ten squares in circular order A B C D E F G H I K.
    A, B, C, D, E, F, G, H, I, K = squares = z3.Ints("A B C D E F G H I K")

    solver = z3.Solver()

    # The solution needs no number with more than two figures, so 1..99
    # (bound stated in the puzzle text).
    for v in squares:
        solver.add(v >= 1, v <= 99)

    # A different number in each square.
    solver.add(z3.Distinct(squares))

    # The four numbers given as examples must stand as they are.
    solver.add(A == 16, B == 2, F == 8, G == 14)

    def same_square_sum(x1, x2, y1, y2):
        return x1 * x1 + x2 * x2 == y1 * y1 + y2 * y2

    # Each adjacent pair has the same sum of squares as the pair opposite it.
    solver.add(same_square_sum(A, B, F, G))
    solver.add(same_square_sum(B, C, G, H))
    solver.add(same_square_sum(C, D, H, I))
    solver.add(same_square_sum(D, E, I, K))
    solver.add(same_square_sum(E, F, K, A))

    return solver, {"A": A, "B": B, "C": C, "D": D, "E": E,
                    "F": F, "G": G, "H": H, "I": I, "K": K}
