# N-queens (csplib 054): place n queens on an n x n board so that no two queens
# attack each other. queens[i] is the column (1..n) of the queen in row i+1.
# Re-submitted after the run profile was corrected (full instance set).
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    q = [cz.Int(f"q_{i}") for i in range(n)]
    constraints = []

    # Each queen is placed on a column between 1 and n.
    for v in q:
        constraints.append(v >= 1)
        constraints.append(v <= n)

    # No two queens are on the same column.
    constraints.append(cz.Distinct(q))

    # No two queens are on the same diagonal: a queen at row i and column c
    # covers the diagonals c + i and c - i, so these must all be different.
    constraints.append(cz.Distinct([q[i] + i for i in range(n)]))
    constraints.append(cz.Distinct([q[i] - i for i in range(n)]))

    return constraints, {"queens": q}
