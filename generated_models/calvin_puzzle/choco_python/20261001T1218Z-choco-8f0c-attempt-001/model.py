# Calvin puzzle: fill an n x n grid with the numbers 1..n*n so that each next number is placed
# exactly three squares away horizontally or vertically, or exactly two squares away diagonally,
# from the previous one.
from pychoco.model import Model

# The two movement types of the puzzle as (row change, column change): type I moves three squares
# along a row or column, type II moves two squares along a diagonal.
MOVES = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def build(instance):
    n = instance["n"]  # side of the grid
    size = n * n

    model = Model()

    # Cells are numbered 1..size in reading order; cell (i, j) is cell i * n + j + 1.
    # x_flat[cell - 1] = the number written in that cell
    x_flat = [model.intvar(1, size, name=f"x_{c}") for c in range(size)]
    # where[k - 1] = the cell that holds the number k. It is the inverse of x_flat and lets the
    # movement rule be stated as a rule on pairs of cells.
    where = [model.intvar(1, size, name=f"where_{k}") for k in range(1, size + 1)]

    # Every square is filled, each number 1..n*n used once.
    model.all_different(x_flat).post()
    model.inverse_channeling(x_flat, where, 1, 1).post()

    # Pairs of cells one legal move apart, staying inside the grid.
    one_move_apart = []
    for i in range(n):
        for j in range(n):
            for di, dj in MOVES:
                if 0 <= i + di < n and 0 <= j + dj < n:
                    one_move_apart.append([i * n + j + 1, (i + di) * n + (j + dj) + 1])

    # The number k + 1 is one legal move away from the number k.
    for k in range(size - 1):
        model.table([where[k], where[k + 1]], one_move_apart).post()

    x = [[x_flat[i * n + j] for j in range(n)] for i in range(n)]
    return model, {"x": x}
