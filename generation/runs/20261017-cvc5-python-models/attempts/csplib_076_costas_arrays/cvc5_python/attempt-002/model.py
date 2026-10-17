# Costas array problem (CSPLib 076): n marks on an n x n grid, one per row and column,
# with all difference vectors between the marks distinct. Model with cvc5 (pythonic API).
# Attempt 2: the difference triangle is made explicit with bounded integer variables, so
# each all-different line works over small domains; the first attempt let the differences
# be unbounded expressions and timed out for n >= 11.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]

    # X[i] is the column of the mark in row i (values 1..n, a permutation).
    X = cz.Ints(" ".join(f"X{i}" for i in range(n)))
    constraints = []

    # the marks are one per row and one per column: X is a permutation of 1..n
    for x in X:
        constraints.append(x >= 1)
        constraints.append(x <= n)
    constraints.append(cz.Distinct(X))

    # the difference triangle: line l holds the differences X[i] - X[i+l] for
    # i = 1..n-l. Each difference lies in -(n-1)..(n-1) (both marks are in 1..n),
    # and is non-zero because the marks are distinct columns.
    for l in range(1, n):
        line = cz.Ints(" ".join(f"D{l}_{i}" for i in range(n - l)))
        for i, d in enumerate(line):
            constraints.append(d == X[i] - X[i + l])
            constraints.append(d >= -(n - 1))
            constraints.append(d <= n - 1)
            constraints.append(d != 0)
        # each line of the difference triangle must not contain any value twice
        if len(line) >= 2:
            constraints.append(cz.Distinct(line))

    return constraints, {"costas": list(X)}
