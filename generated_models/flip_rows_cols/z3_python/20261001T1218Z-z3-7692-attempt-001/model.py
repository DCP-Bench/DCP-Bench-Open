# Flip rows and columns: choose a sign (+1 or -1) for every row and every column of a
# matrix of numbers, so that every row and column of the signed matrix sums to a value
# of zero or more, and the sum of all the entries is as small as possible.
import z3


def build(instance):
    a = instance["input_matrix"]  # the matrix of positive and negative numbers
    rows = len(a)
    cols = len(a[0])

    # row_signs[i] / col_signs[j] is -1 if that row / column is flipped, 1 if it is not.
    # The sign of the entry (i, j) is row_signs[i] * col_signs[j]. Products of two
    # variables are slow for Z3, so each sign is mirrored by a Boolean "flipped" and the
    # signed entry is picked with an If: the entry keeps its sign when row and column are
    # both flipped or both not flipped, and changes sign otherwise.
    row_signs = [z3.Int(f"row_signs_{i}") for i in range(rows)]
    col_signs = [z3.Int(f"col_signs_{j}") for j in range(cols)]
    row_flipped = [z3.Bool(f"row_flipped_{i}") for i in range(rows)]
    col_flipped = [z3.Bool(f"col_flipped_{j}") for j in range(cols)]

    # Sums of the signed rows and columns, and the total sum (to be minimized).
    row_sums = [z3.Int(f"row_sums_{i}") for i in range(rows)]
    col_sums = [z3.Int(f"col_sums_{j}") for j in range(cols)]
    total_sum = z3.Int("total_sum")

    solver = z3.Solver()

    # A sign is -1 or 1 (not 0).
    for i in range(rows):
        solver.add(row_signs[i] == z3.If(row_flipped[i], -1, 1))
    for j in range(cols):
        solver.add(col_signs[j] == z3.If(col_flipped[j], -1, 1))

    # signed[i][j] is the entry (i, j) after the flips.
    signed = [[z3.If(row_flipped[i] == col_flipped[j], a[i][j], -a[i][j])
               for j in range(cols)] for i in range(rows)]

    # Every row and every column sums to zero or more. The upper bounds 300 (and 1000 for
    # the total) are the domains the reference declares for these sums.
    for i in range(rows):
        solver.add(row_sums[i] == z3.Sum(signed[i]))
        solver.add(row_sums[i] >= 0, row_sums[i] <= 300)
    for j in range(cols):
        solver.add(col_sums[j] == z3.Sum([signed[i][j] for i in range(rows)]))
        solver.add(col_sums[j] >= 0, col_sums[j] <= 300)

    # The overall sum of the matrix is the sum of the row sums.
    solver.add(total_sum == z3.Sum(row_sums))
    solver.add(total_sum >= 0, total_sum <= 1000)

    # Minimize the overall sum.
    return solver, {"row_signs": row_signs, "col_signs": col_signs}, ("minimize", total_sum)
