# Flow Free: connect the two cells of each colour with a pipe so that the pipes
# cover the whole board and do not cross or overlap. The board is printed as a
# list of lists of colours 1..K.
import cvc5.pythonic as cz


def build(instance):
    board = instance["board"]
    R = len(board)
    C = len(board[0])
    N = R * C
    K = max(max(row) for row in board)

    col = [[cz.Int(f"col_{r}_{c}") for c in range(C)] for r in range(R)]
    # rank orders the cells of one pipe away from its source clue (rank 0).
    rank = [[cz.Int(f"rank_{r}_{c}") for c in range(C)] for r in range(R)]

    def neighbours(r, c):
        out = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < R and 0 <= nc < C:
                out.append((nr, nc))
        return out

    cons = []

    # Every cell takes one colour from 1 to K; a clue cell keeps its given colour.
    for r in range(R):
        for c in range(C):
            cons.append(col[r][c] >= 1)
            cons.append(col[r][c] <= K)
            if board[r][c] != 0:
                cons.append(col[r][c] == board[r][c])

    # Each colour is one pipe: its two clue cells are the ends, with exactly one
    # neighbour of the same colour. Every other cell of that colour has exactly
    # two such neighbours, so the pipe passes through it.
    for r in range(R):
        for c in range(C):
            clue = board[r][c] != 0
            same = [cz.If(col[qr][qc] == col[r][c], 1, 0) for qr, qc in neighbours(r, c)]
            cons.append(cz.Sum(same) == (1 if clue else 2))

    # The pipe must be one connected path with no loop. The source clue of a
    # colour has rank 0, every other cell has rank >= 1 and a neighbour of its
    # colour with rank one lower. Ranks strictly fall toward the source, so no
    # cycle can close.
    for r in range(R):
        for c in range(C):
            clue = board[r][c] != 0
            cons.append(rank[r][c] >= 0)
            cons.append(rank[r][c] <= N - 1)
            if not clue:
                cons.append(rank[r][c] >= 1)
            pred = [
                cz.And(col[qr][qc] == col[r][c], rank[qr][qc] == rank[r][c] - 1)
                for qr, qc in neighbours(r, c)
            ]
            cons.append(cz.Implies(rank[r][c] > 0, cz.Or(pred)))

    outputs = {"B": [[col[r][c] for c in range(C)] for r in range(R)]}
    return cons, outputs
