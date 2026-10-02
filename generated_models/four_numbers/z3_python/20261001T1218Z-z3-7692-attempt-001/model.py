# Four numbers: given up to four distinct integers, find three integers between 1 and 10
# such that each given number is the sum of some subset of the three.
import z3


def build(instance):
    numbers = instance["numbers"]  # the numbers that have to be generated
    m = len(numbers)
    n = 3                          # how many numbers to find (fixed by the problem)

    # x[j] is the j-th number found, between 1 and 10 (bounds from the problem statement).
    x = [z3.Int(f"x_{j}") for j in range(n)]
    # use[i][j] is true if x[j] is part of the subset that sums to numbers[i].
    use = [[z3.Bool(f"use_{i}_{j}") for j in range(n)] for i in range(m)]

    solver = z3.Solver()

    for j in range(n):
        solver.add(x[j] >= 1, x[j] <= 10)

    # Each given number equals the sum of the chosen subset of x.
    for i in range(m):
        solver.add(z3.Sum([z3.If(use[i][j], x[j], 0) for j in range(n)]) == numbers[i])

    return solver, {"x": x}
