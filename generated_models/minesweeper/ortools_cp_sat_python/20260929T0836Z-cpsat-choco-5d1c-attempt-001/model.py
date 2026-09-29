# Minesweeper: from the revealed numbers of a board, decide which of the
# unopened cells hold a mine. An opened cell is safe and shows how many of its
# (up to eight) neighbours are mines.
from ortools.sat.python import cp_model


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]
    rows, cols = len(game), len(game[0])

    model = cp_model.CpModel()

    # mines[r][c] is true when cell (r, c) holds a mine
    mines = [[model.new_bool_var(f"mine_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                model.add(mines[r][c] == 0)
                # its number is the count of mines among its neighbours
                model.add(
                    sum(
                        mines[a][b]
                        for a in range(max(0, r - 1), min(rows, r + 2))
                        for b in range(max(0, c - 1), min(cols, c + 2))
                        if (a, b) != (r, c)
                    )
                    == game[r][c]
                )

    return model, {"mines": mines}
