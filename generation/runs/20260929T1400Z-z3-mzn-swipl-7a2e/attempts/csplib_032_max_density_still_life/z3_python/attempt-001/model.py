# Maximum density still life: on an n x m active area of Conway's Game of Life,
# find the pattern with the most live cells that is stable (unchanged in the
# next generation). Cells outside the area are dead but still obey the rules.
import z3


def build(instance):
    n, m = instance["n"], instance["m"]  # rows and columns of the active area

    solver = z3.Solver()

    # grid[i][j] is true when the cell is alive
    grid = [[z3.Bool(f"grid_{i}_{j}") for j in range(m)] for i in range(n)]

    def live_neighbours(i, j):
        """The number of live cells around (i, j), limited to the active area."""
        return z3.Sum([
            z3.If(grid[a][b], 1, 0)
            for a in range(max(0, i - 1), min(n, i + 2))
            for b in range(max(0, j - 1), min(m, j + 2))
            if (a, b) != (i, j)
        ])

    # cells inside the area stay as they are
    for i in range(n):
        for j in range(m):
            count = live_neighbours(i, j)
            # a live cell survives only with 2 or 3 live neighbours
            solver.add(z3.Implies(grid[i][j], z3.And(count >= 2, count <= 3)))
            # a dead cell must not have exactly 3 live neighbours, or it would be born
            solver.add(z3.Implies(z3.Not(grid[i][j]), count != 3))

    # dead cells just outside the area must not be born either. The cells that
    # touch the area along its top and bottom edges see three cells of the
    # first / last row, those along the left and right edges three cells of the
    # first / last column; the four outer corners see one cell and never reach 3.
    def total(cells):
        return z3.Sum([z3.If(c, 1, 0) for c in cells])

    for j in range(m):
        solver.add(total([grid[0][a] for a in range(max(0, j - 1), min(m, j + 2))]) != 3)
        solver.add(total([grid[n - 1][a] for a in range(max(0, j - 1), min(m, j + 2))]) != 3)
    for i in range(n):
        solver.add(total([grid[a][0] for a in range(max(0, i - 1), min(n, i + 2))]) != 3)
        solver.add(total([grid[a][m - 1] for a in range(max(0, i - 1), min(n, i + 2))]) != 3)

    # maximise the number of live cells
    return solver, {"grid": grid}, ("maximize", total([grid[i][j] for i in range(n) for j in range(m)]))
