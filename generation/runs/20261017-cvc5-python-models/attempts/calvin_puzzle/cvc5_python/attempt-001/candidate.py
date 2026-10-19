# Calvin puzzle: fill an n by n grid with the numbers 1..n^2 so that each number
# is placed relative to the previous one by one of two movement types.
# Model: cvc5 (pythonic). Values are 0-based internally, outputs are 1-based.

from cvc5.pythonic import Distinct, Ints, Or, And


def build(instance):
    n = instance["n"]
    N = n * n

    # P[v]: cell index (row * n + col) holding the number v+1.
    # X[c]: number (minus 1) written in cell c.
    P = Ints(" ".join(f"P{v}" for v in range(N)))
    X = Ints(" ".join(f"X{c}" for c in range(N)))
    # R[v], C[v]: row and column of the number v+1.
    R = Ints(" ".join(f"R{v}" for v in range(N)))
    C = Ints(" ".join(f"C{v}" for v in range(N)))

    constraints = []

    # Domains: the grid holds each of the numbers 1..n^2 exactly once.
    for v in range(N):
        constraints += [P[v] >= 0, P[v] <= N - 1, X[v] >= 0, X[v] <= N - 1]
        constraints += [R[v] >= 0, R[v] <= n - 1, C[v] >= 0, C[v] <= n - 1]
        constraints.append(P[v] == R[v] * n + C[v])

    # Every cell receives exactly one number.
    constraints.append(Distinct([P[v] for v in range(N)]))

    # Link the two views of the grid: number v+1 sits in cell c iff X[c] == v.
    for c in range(N):
        for v in range(N):
            constraints.append((P[v] == c) == (X[c] == v))

    # Movement between consecutive numbers v+1 and v+2.
    # Type I: horizontal or vertical, exactly three squares away (two-square gap).
    # Type II: diagonal, exactly two squares away (one-square gap).
    for v in range(N - 1):
        dr = R[v + 1] - R[v]
        dc = C[v + 1] - C[v]
        orthogonal = Or(
            And(dr == 0, Or(dc == 3, dc == -3)),
            And(dc == 0, Or(dr == 3, dr == -3)),
        )
        diagonal = And(Or(dr == 2, dr == -2), Or(dc == 2, dc == -2))
        constraints.append(Or(orthogonal, diagonal))

    x = [[X[i * n + j] + 1 for j in range(n)] for i in range(n)]
    return constraints, {"x": x}
