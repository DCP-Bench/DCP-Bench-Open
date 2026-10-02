# Even Fibonacci numbers (Project Euler 2): add up the even-valued terms of the
# Fibonacci sequence (1, 2, 3, 5, 8, ...) that do not exceed four million.
import z3


def build(instance):
    del instance  # the puzzle states its own limit

    limit = 4000000  # terms must not exceed four million
    n = 35           # terms f[1..35] are generated; f[35] = 9227465 already
                     # exceeds the limit, so no later term can count
    max_term = 10000000  # upper bound on f[0..n]: f[35] < 10**7

    # f[i] = the i-th Fibonacci term; x[i] = 1 when term i counts in the sum.
    f = z3.IntVector("f", n + 1)
    x = z3.BoolVector("x", n + 1)
    res = z3.Int("res")

    solver = z3.Solver()
    for term in f:
        solver.add(term >= 0, term <= max_term)
    solver.add(res >= 0, res <= 100000000)

    # Each term is the sum of the previous two. The sequence 1, 1, 2, 3, 5, ...
    # differs from the puzzle's 1, 2, 3, 5, ... only by an extra odd 1, which is
    # never counted.
    solver.add(f[0] == 0, f[1] == 1, f[2] == 1)
    for i in range(3, n + 1):
        solver.add(f[i] == f[i - 1] + f[i - 2])

    # Term 0 is not a term of the sequence.
    solver.add(z3.Not(x[0]))

    # A term counts exactly when it is even and below four million (4,000,000 is
    # not a Fibonacci number, so "below" and "not exceeding" agree).
    for i in range(1, n + 1):
        solver.add(x[i] == z3.And(f[i] % 2 == 0, f[i] < limit))

    # The answer is the sum of the counted terms.
    solver.add(res == z3.Sum([z3.If(x[i], f[i], 0) for i in range(1, n + 1)]))

    return solver, {"res": res}
