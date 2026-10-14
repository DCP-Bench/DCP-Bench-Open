# Maximum density still life: in Conway's Game of Life, find the most densely populated
# stable pattern (a "still life") on an n by m active grid. A live cell needs exactly 2
# or 3 live neighbours to stay alive; a dead cell, including the dead cells just outside
# the grid, must not have exactly 3 live neighbours, or it would come alive.
import functools
import itertools
import operator

from hermax.model import Model


def clause(lits):
    """The disjunction of the given literals."""
    return functools.reduce(operator.or_, lits)


def build(instance):
    n = instance["n"]  # rows of the active grid
    m_cols = instance["m"]  # columns of the active grid

    m = Model()
    # grid[i][j] = cell (i, j) is alive
    grid = m.bool_matrix("grid", n, m_cols)

    for i in range(n):
        for j in range(m_cols):
            # the live cells among the (up to eight) neighbours of the cell inside the grid
            around = [grid[i + di][j + dj] for di in (-1, 0, 1) for dj in (-1, 0, 1)
                      if (di, dj) != (0, 0) and 0 <= i + di < n and 0 <= j + dj < m_cols]
            cell = grid[i][j]
            count = len(around)

            # A live cell has at least 2 live neighbours: dropping any one neighbour
            # still leaves a live one among the rest. (A cell with fewer than 2
            # neighbours cannot be alive.)
            if count < 2:
                m &= ~cell
            else:
                for rest in itertools.combinations(around, count - 1):
                    m &= (~cell | clause(rest))
            # A live cell has at most 3 live neighbours: no four neighbours are all alive.
            for four in itertools.combinations(around, 4):
                m &= (~cell | clause([~x for x in four]))
            # A dead cell does not have exactly 3 live neighbours: if three neighbours are
            # alive, one of the others is alive too, or the cell itself is alive.
            for three in itertools.combinations(range(count), 3):
                others = [around[k] for k in range(count) if k not in three]
                m &= (cell | clause([~around[k] for k in three] + others))

    # The dead cells just outside the grid must not have exactly 3 live neighbours
    # either. A cell beside the top, bottom, left or right edge touches up to three
    # cells of that edge, so those three cells must not all be alive.
    for j in range(1, m_cols - 1):
        for i in (0, n - 1):
            m &= clause([~grid[i][j - 1], ~grid[i][j], ~grid[i][j + 1]])
    for i in range(1, n - 1):
        for j in (0, m_cols - 1):
            m &= clause([~grid[i - 1][j], ~grid[i][j], ~grid[i + 1][j]])

    # Maximise the number of live cells. A soft clause pays when its literal is false,
    # so every dead cell pays 1.
    for i in range(n):
        for j in range(m_cols):
            m.obj[1] += grid[i][j]

    return m, {"grid": grid}
