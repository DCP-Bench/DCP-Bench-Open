# Costas array problem (CSPLib 076): n marks on an n x n grid, one per row and column,
# with all difference vectors between the marks distinct. Model with cvc5 (pythonic API).
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

    # each line of the difference triangle must not contain any value twice:
    # for each length l, the differences X[i] - X[i+l] are all different
    for l in range(1, n):
        diffs = [X[i] - X[i + l] for i in range(n - l)]
        if len(diffs) >= 2:
            constraints.append(cz.Distinct(diffs))

    return constraints, {"costas": list(X)}
