# Minesweeper: decide which unopened cells contain a mine, given the numbers on the opened cells.
from pyscipopt import Model, quicksum


def build(instance):
    board = instance["game_data"]
    rows = len(board)
    cols = len(board[0])
    m = Model()

    # mines[r][c] = 1 if cell (r, c) contains a mine
    mines = [[m.addVar(name=f"mine_{r}_{c}", vtype="B") for c in range(cols)] for r in range(rows)]

    def neighbours(r, c):
        return [(r + dr, c + dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0) and 0 <= r + dr < rows and 0 <= c + dc < cols]

    # an opened cell (a number in game_data; -1 marks an unopened cell) is safe, so it holds no mine
    for r in range(rows):
        for c in range(cols):
            if board[r][c] >= 0:
                m.addCons(mines[r][c] == 0)

    # the number on an opened cell is the count of mines among its adjacent cells
    for r in range(rows):
        for c in range(cols):
            if board[r][c] >= 0:
                m.addCons(quicksum(mines[nr][nc] for nr, nc in neighbours(r, c)) == board[r][c])

    # the output is the mine map, one row per board row
    return m, {"mines": [[mines[r][c] for c in range(cols)] for r in range(rows)]}
