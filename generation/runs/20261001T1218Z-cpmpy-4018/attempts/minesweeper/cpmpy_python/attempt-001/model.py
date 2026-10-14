# Minesweeper: from the numbers on the opened cells, decide which unopened cells hold a mine.
# An opened cell shows how many of its (up to 8) neighbours are mines.
import cpmpy as cp


def build(instance):
    unopened = instance["X"]        # marker for a cell that has not been opened (-1)
    game = instance["game_data"]    # game[r][c] = number of mines around the cell, or the marker
    rows = len(game)
    cols = len(game[0])

    # mines[r, c] = True if the cell holds a mine
    mines = cp.boolvar(shape=(rows, cols), name="mines")

    model = cp.Model()

    for r in range(rows):
        for c in range(cols):
            if game[r][c] == unopened:
                continue

            # An opened cell is not a mine.
            model += ~mines[r, c]

            # The number shown is the count of mines among the neighbouring cells
            # (the eight surrounding cells, fewer at the border of the board).
            neighbours = [mines[r + a, c + b]
                          for a in (-1, 0, 1) for b in (-1, 0, 1)
                          if (a, b) != (0, 0) and 0 <= r + a < rows and 0 <= c + b < cols]
            model += cp.sum(neighbours) == game[r][c]

    return model, {"mines": mines}
