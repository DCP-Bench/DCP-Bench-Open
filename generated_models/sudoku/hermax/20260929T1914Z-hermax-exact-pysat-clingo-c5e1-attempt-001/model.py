# Sudoku: complete a 9 x 9 grid so that every row, column and 3 x 3 box holds
# each of the digits 1..9 once, keeping the digits already given.
from hermax.model import Model


def build(instance):
    given = instance["input_grid"]  # 0 marks an empty cell
    n = len(given)
    box = 3  # side of a box

    m = Model()
    # grid[r][c] = the digit in cell (r, c)
    grid = m.int_matrix("grid", n, n, 1, n)

    # the given digits stay
    for r in range(n):
        for c in range(n):
            if given[r][c] != 0:
                m &= (grid[r][c] == given[r][c])

    # each row and each column holds different digits
    for i in range(n):
        m &= grid.row(i).all_different()
        m &= grid.col(i).all_different()
    # each 3 x 3 box holds different digits
    for i in range(0, n, box):
        for j in range(0, n, box):
            cells = [grid[r][c] for r in range(i, i + box) for c in range(j, j + box)]
            m &= m.vector(cells).all_different()

    return m, {"grid": grid}
