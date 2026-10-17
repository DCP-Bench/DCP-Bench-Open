# N-queens (csplib 054): place n queens on an n x n board so that no two queens
# attack each other. queens[i] is the column (1..n) of the queen in row i+1.
# Pairwise encoding: each pair of queens gets a column, diagonal and anti-diagonal
# disequality, written as plain binary constraints instead of Distinct.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    q = [cz.Int(f"q_{i}") for i in range(n)]
    constraints = []

    # Each queen is placed on a column between 1 and n.
    for v in q:
        constraints.append(v >= 1)
        constraints.append(v <= n)

    # No two queens are on the same column, or on the same diagonal:
    # a queen at row i and column c covers the diagonals c + i and c - i.
    for i in range(n):
        for j in range(i + 1, n):
            constraints.append(q[i] != q[j])
            constraints.append(q[i] + i != q[j] + j)
            constraints.append(q[i] - i != q[j] - j)

    return constraints, {"queens": q}
