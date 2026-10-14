# Minesweeper: from the revealed numbers of a board, decide which of the
# unopened cells hold a mine. An opened cell is safe and shows how many of its
# (up to eight) neighbours are mines.
import z3


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]
    rows, cols = len(game), len(game[0])

    solver = z3.Solver()

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[z3.Bool(f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                solver.add(z3.Not(mines[r][c]))
                # its number is the count of mines among its neighbours
                neighbours = [
                    mines[a][b]
                    for a in range(max(0, r - 1), min(rows, r + 2))
                    for b in range(max(0, c - 1), min(cols, c + 2))
                    if (a, b) != (r, c)
                ]
                solver.add(z3.PbEq([(m, 1) for m in neighbours], game[r][c]))

    return solver, {"mines": mines}
