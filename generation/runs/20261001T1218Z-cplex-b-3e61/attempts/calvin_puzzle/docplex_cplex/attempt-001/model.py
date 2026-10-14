"""Calvin's puzzle: fill an n-by-n grid with the numbers 1..n^2 so that each next number is placed
either three squares away horizontally or vertically (a two-square gap), or two squares away
diagonally (a one-square gap) from the previous number.

The model reports the completed grid.
"""
from docplex.mp.model import Model

# The allowed steps between consecutive numbers (part of the puzzle, not of the instance):
# three squares along a row or column, or two squares along a diagonal.
STEPS = [(3, 0), (-3, 0), (0, 3), (0, -3), (2, 2), (2, -2), (-2, 2), (-2, -2)]


def build(instance):
    n = instance["n"]  # size of the grid
    squares = [(i, j) for i in range(n) for j in range(n)]
    last = n * n

    model = Model("calvin_puzzle")

    # x[i][j] is the number placed on square (i, j).
    x = {sq: model.integer_var(1, last, name=f"x_{sq[0]}_{sq[1]}") for sq in squares}

    # The filling order is encoded by its steps rather than by a one-hot square-to-number table:
    # step[a, b] = 1 when the number after the one on square a is placed on square b. There is
    # one binary per allowed step on the board, where a one-hot table needs n^4 binaries.
    step = {}
    for (i, j) in squares:
        for di, dj in STEPS:
            if 0 <= i + di < n and 0 <= j + dj < n:
                step[(i, j), (i + di, j + dj)] = model.binary_var(name=f"step_{i}_{j}_{i + di}_{j + dj}")

    # Every square is followed by at most one square and preceded by at most one square.
    for sq in squares:
        model.add_constraint(model.sum(v for (a, b), v in step.items() if a == sq) <= 1)
        model.add_constraint(model.sum(v for (a, b), v in step.items() if b == sq) <= 1)

    # Filling n^2 squares takes n^2 - 1 steps.
    model.add_constraint(model.sum(step.values()) == last - 1)

    # A step from a to b means b holds the number after a's. Numbers then rise by one along
    # every chain of steps, so no chain closes into a loop; with n^2 - 1 steps and at most one
    # step in and out of each square, the steps form one path through all squares, numbered
    # 1..n^2 in order, so every square gets a different number.
    for (a, b), v in step.items():
        model.add_indicator(v, x[b] == x[a] + 1)

    return model, {"x": [[x[i, j] for j in range(n)] for i in range(n)]}
