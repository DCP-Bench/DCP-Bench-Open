# Minesweeper: from the revealed numbers of a board, decide which of the
# unopened cells hold a mine. An opened cell is safe and shows how many of its
# (up to eight) neighbours are mines.
from exact import Exact


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]
    rows, cols = len(game), len(game[0])

    solver = Exact()
    # mines[r][c] is 1 when cell (r, c) holds a mine, 0 otherwise
    mines = [[f"mine_{r}_{c}" for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            solver.addVariable(mines[r][c], 0, 1)

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                solver.addConstraint([(1, mines[r][c])], True, 0, True, 0)
                # its number is the count of mines among its neighbours
                around = [(1, mines[a][b])
                          for a in range(max(0, r - 1), min(rows, r + 2))
                          for b in range(max(0, c - 1), min(cols, c + 2))
                          if (a, b) != (r, c)]
                solver.addConstraint(around, True, game[r][c], True, game[r][c])

    return solver, {"mines": mines}
