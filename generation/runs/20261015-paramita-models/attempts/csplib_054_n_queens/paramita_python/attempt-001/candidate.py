# N-queens (csplib 054): place n queens on an n x n chessboard so that no two
# queens share a row, a column or a diagonal.
from paramita.modelling import Bool


def build(instance):
    n = instance["n"]

    # q[i][c] = 1 if the queen of row i stands in column c (0-based inside the model)
    q = [[Bool(f"q_{i}_{c}") for c in range(n)] for i in range(n)]

    cons = []
    # one queen in every row (no two queens on the same row)
    cons += [sum(q[i]) == 1 for i in range(n)]
    # one queen in every column (no two queens on the same column)
    cons += [sum(q[i][c] for i in range(n)) == 1 for c in range(n)]
    # no two queens on the same anti-diagonal: cells with equal i + c
    for s in range(2 * n - 1):
        cells = [q[i][c] for i in range(n) for c in range(n) if i + c == s]
        if len(cells) > 1:
            cons.append(sum(cells) <= 1)
    # no two queens on the same diagonal: cells with equal i - c
    for dd in range(-(n - 1), n):
        cells = [q[i][c] for i in range(n) for c in range(n) if i - c == dd]
        if len(cells) > 1:
            cons.append(sum(cells) <= 1)

    # output: the column of the queen in each row, 1-based
    queens = [sum((c + 1) * q[i][c] for c in range(n)) for i in range(n)]
    return cons, {"queens": queens}
