# Divisible by 1 through 9: find a ten-digit number using each digit 0-9 exactly
# once such that the number formed by its first n digits is divisible by n, for
# n = 1 to 10.
import z3


def build(instance):
    del instance  # the puzzle states its own length

    n = 10  # number of digits

    # x[i] = the digit at position i, read from left to right.
    x = z3.IntVector("x", n)
    # prefix[i] = the number formed by the first i + 1 digits.
    prefix = z3.IntVector("prefix", n)

    solver = z3.Solver()

    for d in x:
        solver.add(d >= 0, d <= 9)
    for p in prefix:
        solver.add(p >= 0, p <= 10 ** n)

    # Every digit from 0 to 9 is used exactly once.
    solver.add(z3.Distinct(x))

    for i in range(n):
        # The first i+1 digits read as a decimal number.
        solver.add(prefix[i] == z3.Sum([x[j] * 10 ** (i - j) for j in range(i + 1)]))
        # That number is divisible by its length i+1.
        solver.add(prefix[i] % (i + 1) == 0)

    # The whole ten-digit number is the prefix made of all the digits.
    return solver, {"number": prefix[n - 1]}
