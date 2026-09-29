# Flip rows and columns (Einav's puzzle): choose, for every row and column,
# whether to flip its sign so that every row sum and every column sum is
# non-negative, with the smallest possible total of the whole matrix.
from exact import Exact


def build(instance):
    matrix = instance["input_matrix"]
    rows, cols = len(matrix), len(matrix[0])

    solver = Exact()
    # row_flipped[i] / col_flipped[j] is 1 when that row / column has its sign flipped
    row_flipped = [f"row_flipped_{i}" for i in range(rows)]
    col_flipped = [f"col_flipped_{j}" for j in range(cols)]
    row_signs = [f"row_sign_{i}" for i in range(rows)]
    col_signs = [f"col_sign_{j}" for j in range(cols)]
    for i in range(rows):
        solver.addVariable(row_flipped[i], 0, 1)
        # the sign is 1 - 2 * flipped: -1 or +1, never 0
        solver.addVariable(row_signs[i], -1, 1)
        solver.addConstraint([(1, row_signs[i]), (2, row_flipped[i])], True, 1, True, 1)
    for j in range(cols):
        solver.addVariable(col_flipped[j], 0, 1)
        solver.addVariable(col_signs[j], -1, 1)
        solver.addConstraint([(1, col_signs[j]), (2, col_flipped[j])], True, 1, True, 1)

    # cell_flipped[i][j] = row_flipped xor col_flipped: the cell changes sign exactly
    # when its row or its column (not both) is flipped
    cell_flipped = [[f"cell_flipped_{i}_{j}" for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            f, r, c = cell_flipped[i][j], row_flipped[i], col_flipped[j]
            solver.addVariable(f, 0, 1)
            solver.addConstraint([(1, f), (-1, r), (-1, c)], False, 0, True, 0)  # f <= r + c ... written as f - r - c <= 0
            solver.addConstraint([(1, f), (1, r), (1, c)], False, 0, True, 2)  # f + r + c <= 2
            solver.addConstraint([(1, f), (1, r), (-1, c)], True, 0)  # f >= c - r
            solver.addConstraint([(1, f), (-1, r), (1, c)], True, 0)  # f >= r - c

    # A cell is worth matrix[i][j] * (1 - 2 * flipped). Every row and column sums to at
    # least 0 (the reference declares a sum to lie in 0..300, which is mirrored here).
    def flipped_terms(cells):
        return [(-2 * matrix[i][j], cell_flipped[i][j]) for i, j in cells if matrix[i][j] != 0]

    for i in range(rows):
        line = [(i, j) for j in range(cols)]
        base = sum(matrix[i][j] for _, j in line)
        solver.addConstraint(flipped_terms(line), True, -base, True, 300 - base)
    for j in range(cols):
        line = [(i, j) for i in range(rows)]
        base = sum(matrix[i][j] for i, _ in line)
        solver.addConstraint(flipped_terms(line), True, -base, True, 300 - base)
    # the total of the matrix lies in the declared range 0..1000
    everything = [(i, j) for i in range(rows) for j in range(cols)]
    offset = sum(matrix[i][j] for i, j in everything)
    solver.addConstraint(flipped_terms(everything), True, -offset, True, 1000 - offset)

    # minimise the total: offset + the flipped terms, and the offset is a constant
    return solver, {"row_signs": row_signs, "col_signs": col_signs}, ("minimize", flipped_terms(everything))
