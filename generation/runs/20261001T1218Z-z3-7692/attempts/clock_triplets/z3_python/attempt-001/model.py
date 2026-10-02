# Clock triplets: arrange the numbers 1 to 12 around a clock face so that no three
# adjacent numbers sum to more than 21 (the smallest value the largest triplet
# sum can take).
import z3


def build(instance):
    del instance  # the puzzle states its own clock and limit

    n = 12          # numbers on the clock face
    max_triplet = 21  # largest allowed sum of three adjacent numbers

    # x[i] = the number at position i of the clock, between 1 and 12.
    x = z3.IntVector("x", n)

    solver = z3.Solver()
    for v in x:
        solver.add(v >= 1, v <= n)

    # Each number from 1 to 12 appears once on the face.
    solver.add(z3.Distinct(x))

    # Every triplet of adjacent numbers (the clock is circular) sums to at most 21.
    for i in range(n):
        solver.add(x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= max_triplet)

    return solver, {"x": list(x)}
