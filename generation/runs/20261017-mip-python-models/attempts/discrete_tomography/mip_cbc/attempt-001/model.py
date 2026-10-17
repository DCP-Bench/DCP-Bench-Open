# Discrete tomography: find a 0/1 matrix whose row sums and column sums match the
# given totals. Satisfaction problem. Output: matrix (0/1 values, list of lists).
import mip


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    n_rows = len(row_sums)
    n_cols = len(col_sums)

    model = mip.Model(sense=mip.MINIMIZE, solver_name="CBC")

    x = [[model.add_var(f"x_{i}_{j}", var_type=mip.BINARY) for j in range(n_cols)]
         for i in range(n_rows)]

    # A matrix which contains zeroes and ones gets x-rayed vertically and horizontally,
    # giving the total number of ones in each row and column.
    for i in range(n_rows):
        model += mip.xsum(x[i][j] for j in range(n_cols)) == row_sums[i]

    # The problem is to reconstruct the contents of the matrix from this information.
    for j in range(n_cols):
        model += mip.xsum(x[i][j] for i in range(n_rows)) == col_sums[j]

    return model, {"matrix": x}
