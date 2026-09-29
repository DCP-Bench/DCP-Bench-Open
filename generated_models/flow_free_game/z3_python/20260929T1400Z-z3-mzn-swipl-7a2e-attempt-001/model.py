# Flow Free: colour every cell of the board so that each colour forms one pipe
# joining its two given end cells, the pipes do not cross or overlap, and the
# whole board is covered. A pipe is a chain of orthogonally adjacent cells of
# one colour.
import z3


def build(instance):
    board = instance["board"]  # colour of each end cell, 0 for a cell to fill
    rows, cols = len(board), len(board[0])
    n_colors = max(max(row) for row in board)  # colours are numbered 1..n_colors

    solver = z3.Solver()

    # B[i][j] = colour of cell (i, j)
    B = [[z3.Int(f"B_{i}_{j}") for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            solver.add(B[i][j] >= 1, B[i][j] <= n_colors)

    for i in range(rows):
        for j in range(cols):
            neighbours = [(a, b) for a, b in ((i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1))
                          if 0 <= a < rows and 0 <= b < cols]
            same_neighbours = z3.Sum([z3.If(B[i][j] == B[a][b], 1, 0) for a, b in neighbours])
            if board[i][j] != 0:
                # an end cell has its given colour and joins exactly one neighbour of that colour
                solver.add(B[i][j] == board[i][j])
                solver.add(same_neighbours == 1)
            else:
                # a cell in the middle of a pipe joins exactly two neighbours of its colour
                solver.add(same_neighbours == 2)

    return solver, {"B": B}
