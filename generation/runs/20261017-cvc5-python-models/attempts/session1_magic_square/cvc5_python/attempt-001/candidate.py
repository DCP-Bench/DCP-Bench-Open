# Session 1 magic square: an n x n grid where each cell holds a different integer
# from 1 to n^2, and the sum of the integers in each row, column and diagonal is
# equal to n(n^2 + 1)/2. The output is the grid as a list of lists.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    cells = [[cz.Int(f"s_{i}_{j}") for j in range(n)] for i in range(n)]
    flat = [c for row in cells for c in row]
    target = n * (n * n + 1) // 2

    constraints = []

    # each cell contains an integer from 1 to n^2
    for c in flat:
        constraints.append(c >= 1)
        constraints.append(c <= n * n)

    # each cell contains a different integer
    if len(flat) >= 2:
        constraints.append(cz.Distinct(flat))

    # the sum of the integers in each row is n(n^2 + 1)/2
    for row in cells:
        constraints.append(sum(row) == target)

    # the sum of the integers in each column is n(n^2 + 1)/2
    for j in range(n):
        constraints.append(sum(cells[i][j] for i in range(n)) == target)

    # the sum of the integers in each diagonal is n(n^2 + 1)/2
    constraints.append(sum(cells[i][i] for i in range(n)) == target)
    constraints.append(sum(cells[i][n - 1 - i] for i in range(n)) == target)

    return constraints, {"square": cells}
