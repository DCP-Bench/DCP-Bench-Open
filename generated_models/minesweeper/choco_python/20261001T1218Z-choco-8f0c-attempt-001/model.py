# Minesweeper: from the numbers shown on the opened cells of a board, decide which of the
# unopened cells hide a mine. An opened cell shows how many of its neighbours are mines.
from pychoco.model import Model


def build(instance):
    unopened = instance["X"]  # the value that marks a cell that is not opened
    game = instance["game_data"]  # shown number of an opened cell, `unopened` otherwise
    rows, cols = len(game), len(game[0])

    model = Model()

    # mines[r][c] = 1 if the cell in row r, column c holds a mine
    mines = [[model.boolvar(name=f"mines_{r}_{c}") for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            if game[r][c] != unopened:
                # an opened cell is not a mine
                model.arithm(mines[r][c], "=", 0).post()
                # its number is the count of mines among its (up to eight) neighbours
                neighbours = [mines[r + a][c + b]
                              for a in (-1, 0, 1) for b in (-1, 0, 1)
                              if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols]
                model.sum(neighbours, "=", game[r][c]).post()

    return model, {"mines": mines}
