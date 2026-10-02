# De Bruijn sequence: a cyclic sequence over an alphabet of `base` symbols in
# which every string of length n occurs exactly once as a window.
import z3


def build(instance):
    base = instance["base"]  # size of the alphabet (digits 0..base-1)
    n = instance["n"]        # order: length of the strings
    m = base ** n            # length of the sequence = number of distinct strings

    # x[i] is the number (in base `base`) read by the window of n symbols starting at
    # position i; all m numbers 0..m-1 appear once.
    x = [z3.Int(f"x_{i}") for i in range(m)]
    # binary[i][j] is the j-th digit of that window (despite the name, a digit in 0..base-1).
    binary = [[z3.Int(f"binary_{i}_{j}") for j in range(n)] for i in range(m)]
    # de_bruijn[i] is the symbol at position i of the sequence.
    de_bruijn = [z3.Int(f"de_bruijn_{i}") for i in range(m)]

    solver = z3.Solver()

    for i in range(m):
        solver.add(x[i] >= 0, x[i] <= m - 1)
        solver.add(de_bruijn[i] >= 0, de_bruijn[i] <= base - 1)
        for j in range(n):
            solver.add(binary[i][j] >= 0, binary[i][j] <= base - 1)

    # All windows are different, so every string of length n occurs exactly once.
    solver.add(z3.Distinct(x))

    # Each window number x[i] is the number written by its digits, most significant first.
    for i in range(m):
        solver.add(x[i] == z3.Sum([binary[i][j] * (base ** (n - j - 1)) for j in range(n)]))

    # Consecutive windows overlap: the window at i shifted by one position is the
    # window at i - 1 without its first digit.
    for j in range(1, n):
        for i in range(1, m):
            solver.add(binary[i - 1][j] == binary[i][j - 1])

    # ... and the same holds around the corner, from the last window to the first.
    for j in range(1, n):
        solver.add(binary[m - 1][j] == binary[0][j - 1])

    # The sequence is the first digit of each window.
    for i in range(m):
        solver.add(de_bruijn[i] == binary[i][0])

    return solver, {"de_bruijn": de_bruijn}
