# Flip rows and columns (Einav's puzzle): choose, for every row and column,
# whether to flip its sign so that every row sum and every column sum is
# non-negative, with the smallest possible total of the whole matrix.
from hermax.model import Model


def build(instance):
    matrix = instance["input_matrix"]
    rows, cols = len(matrix), len(matrix[0])

    m = Model()
    # row_flipped[i] / col_flipped[j] is true when that row / column has its sign flipped
    row_flipped = m.bool_vector("row_flipped", rows)
    col_flipped = m.bool_vector("col_flipped", cols)
    # the signs themselves, -1 or +1 (never 0): reported as the outputs
    row_signs = m.int_vector("row_signs", rows, -1, 1)
    col_signs = m.int_vector("col_signs", cols, -1, 1)
    for i in range(rows):
        m &= (~row_flipped[i] | (row_signs[i] == -1))
        m &= (row_flipped[i] | (row_signs[i] == 1))
    for j in range(cols):
        m &= (~col_flipped[j] | (col_signs[j] == -1))
        m &= (col_flipped[j] | (col_signs[j] == 1))

    # cell_flipped[i][j]: the cell changes sign, exactly when its row or its column
    # (not both) is flipped
    cell_flipped = [[m.bool(f"cell_flipped_{i}_{j}") for j in range(cols)] for i in range(rows)]
    for i in range(rows):
        for j in range(cols):
            f, r, c = cell_flipped[i][j], row_flipped[i], col_flipped[j]
            m &= (~f | r | c)
            m &= (~f | ~r | ~c)
            m &= (f | ~r | c)
            m &= (f | r | ~c)

    # A cell is worth matrix[i][j] * (1 - 2 * flipped), so a line adds up to its plain sum
    # minus twice the flipped entries. Every row and column sums to at least 0 (the
    # reference declares a sum to lie in 0..300, which is mirrored here).
    def flipped(cells):
        return sum(-2 * matrix[i][j] * cell_flipped[i][j] for i, j in cells if matrix[i][j] != 0)

    for i in range(rows):
        line = [(i, j) for j in range(cols)]
        base = sum(matrix[i][j] for _, j in line)
        m &= (flipped(line) >= -base)
        m &= (flipped(line) <= 300 - base)
    for j in range(cols):
        line = [(i, j) for i in range(rows)]
        base = sum(matrix[i][j] for i, _ in line)
        m &= (flipped(line) >= -base)
        m &= (flipped(line) <= 300 - base)
    # the total of the matrix lies in the declared range 0..1000
    everything = [(i, j) for i in range(rows) for j in range(cols)]
    offset = sum(matrix[i][j] for i, j in everything)
    m &= (flipped(everything) >= -offset)
    m &= (flipped(everything) <= 1000 - offset)

    # Minimise the total. The total is offset - 2 * sum(matrix * flipped), so the
    # aim is to flip cells with positive entries and keep cells with negative ones
    # unflipped: a positive cell not flipped pays its size (the literal itself),
    # a negative cell flipped pays its size (the negated literal).
    for i, j in everything:
        if matrix[i][j] > 0:
            m.obj[matrix[i][j]] += cell_flipped[i][j]
        elif matrix[i][j] < 0:
            m.obj[-matrix[i][j]] += ~cell_flipped[i][j]

    return m, {"row_signs": row_signs, "col_signs": col_signs}
