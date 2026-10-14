"""Maximum density still life: in Conway's Game of Life, find the most densely populated stable
pattern (a still life) on an n x m active grid. Cells outside the grid are dead. A live cell
stays alive only with 2 or 3 live neighbours; a dead cell, also one just outside the grid, must
not have exactly 3 live neighbours (it would come alive). Maximise the number of live cells in
the grid.

The model reports the grid, with 1 for a live cell and 0 for a dead one.
"""
import pulp


def build(instance):
    n = instance["n"]  # rows of the active grid
    m = instance["m"]  # columns of the active grid

    problem = pulp.LpProblem("still_life", pulp.LpMaximize)

    # grid[i][j] = 1 if the cell in row i, column j is alive
    grid = [[pulp.LpVariable(f"grid_{i}_{j}", cat="Binary") for j in range(m)] for i in range(n)]

    for i in range(n):
        for j in range(m):
            # live neighbours of the cell, among the (up to eight) cells around it
            around = pulp.lpSum(grid[i + di][j + dj]
                                for di in (-1, 0, 1) for dj in (-1, 0, 1)
                                if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m)

            # A live cell has 2 or 3 live neighbours. Off (slack) when the cell is dead; at most
            # eight neighbours exist, so the slack for "at most 3" is 5.
            problem += around >= 2 * grid[i][j]
            problem += around <= 3 + 5 * (1 - grid[i][j])

            # A dead cell does not have exactly 3 live neighbours: it has at most 2 or at least 4.
            # more[i][j] = 1 chooses "at least 4". Off (slack) when the cell is alive; at most 8
            # neighbours exist.
            more = pulp.LpVariable(f"more_{i}_{j}", cat="Binary")
            problem += around <= 2 + 6 * more + 6 * grid[i][j]
            problem += around >= 4 * more - 4 * grid[i][j]

    # Dead cells just outside the grid do not come alive. Such a cell touches at most three
    # cells of the grid, those along the edge next to it; it must not touch three live cells.
    for j in range(m):
        for edge_row in (0, n - 1):
            window = [grid[edge_row][jj] for jj in range(max(0, j - 1), min(m, j + 2))]
            problem += pulp.lpSum(window) <= 2
    for i in range(n):
        for edge_col in (0, m - 1):
            window = [grid[ii][edge_col] for ii in range(max(0, i - 1), min(n, i + 2))]
            problem += pulp.lpSum(window) <= 2

    # maximise the number of live cells
    problem += pulp.lpSum(grid[i][j] for i in range(n) for j in range(m))

    return problem, {"grid": grid}
