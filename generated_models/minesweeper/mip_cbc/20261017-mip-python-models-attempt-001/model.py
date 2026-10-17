# Minesweeper: a grid of cells. A cell is either unopened (its value equals the
# instance field X) or a clue (a number). A clue is the number of mines among the
# eight cells around it. Decide which unopened cells hold a mine.
# Output mines[r][c] is True for a mine and False otherwise.
import mip


def build(instance):
    grid = instance["game_data"]
    unknown = instance["X"]
    rows = len(grid)
    cols = len(grid[0])
    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    # Only unopened cells can hold a mine; clue cells are open and hold none.
    mine = {}
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == unknown:
                mine[r, c] = model.add_var(f"mine_{r}_{c}", var_type=mip.BINARY)

    # The number on a clue cell is the number of mines among its adjacent cells.
    for r in range(rows):
        for c in range(cols):
            clue = grid[r][c]
            if clue == unknown:
                continue
            neighbours = [
                mine[nr, nc]
                for nr in range(r - 1, r + 2)
                for nc in range(c - 1, c + 2)
                if (nr, nc) != (r, c) and (nr, nc) in mine
            ]
            if neighbours:
                model.add_constr(mip.xsum(neighbours) == clue)

    outputs = {
        "mines": [
            [mine[r, c] if (r, c) in mine else False for c in range(cols)]
            for r in range(rows)
        ]
    }
    return model, outputs
