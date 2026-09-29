# Maximum density still life: on an n x m active area of Conway's Game of Life,
# find the pattern with the most live cells that is stable (unchanged in the
# next generation). Cells outside the area are dead but still obey the rules.
from ortools.sat.python import cp_model


def build(instance):
    n, m = instance["n"], instance["m"]  # rows and columns of the active area

    model = cp_model.CpModel()

    # grid[i][j] is true when the cell is alive
    grid = [[model.new_bool_var(f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    def neighbours(i, j):
        """The live-cell indicators around (i, j), limited to the active area."""
        return [
            grid[a][b]
            for a in range(max(0, i - 1), min(n, i + 2))
            for b in range(max(0, j - 1), min(m, j + 2))
            if (a, b) != (i, j)
        ]

    # cells inside the area stay as they are
    for i in range(n):
        for j in range(m):
            count = sum(neighbours(i, j))
            # a live cell survives only with 2 or 3 live neighbours
            model.add(count >= 2).only_enforce_if(grid[i][j])
            model.add(count <= 3).only_enforce_if(grid[i][j])
            # a dead cell must not have exactly 3 live neighbours, or it would be born
            model.add(count != 3).only_enforce_if(grid[i][j].negated())

    # dead cells just outside the area must not be born either. The cells that
    # touch the area along its top and bottom edges see three cells of the
    # first / last row, those along the left and right edges three cells of the
    # first / last column; the four outer corners see one cell and never reach 3.
    for j in range(m):
        model.add(sum(grid[0][a] for a in range(max(0, j - 1), min(m, j + 2))) != 3)
        model.add(sum(grid[n - 1][a] for a in range(max(0, j - 1), min(m, j + 2))) != 3)
    for i in range(n):
        model.add(sum(grid[a][0] for a in range(max(0, i - 1), min(n, i + 2))) != 3)
        model.add(sum(grid[a][m - 1] for a in range(max(0, i - 1), min(n, i + 2))) != 3)

    # maximise the number of live cells
    model.maximize(sum(grid[i][j] for i in range(n) for j in range(m)))

    return model, {"grid": grid}
