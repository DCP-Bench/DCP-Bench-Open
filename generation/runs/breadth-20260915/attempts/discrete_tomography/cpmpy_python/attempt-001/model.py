import cpmpy as cp


def build(instance):
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, columns = len(row_sums), len(col_sums)
    matrix = cp.intvar(0, 1, shape=(rows, columns), name="x")
    model = cp.Model()
    for i in range(rows):
        model += cp.sum([matrix[i, j] for j in range(columns)]) == row_sums[i]
    for j in range(columns):
        model += cp.sum([matrix[i, j] for i in range(rows)]) == col_sums[j]
    return model, {"matrix": [[matrix[i, j] for j in range(columns)] for i in range(rows)]}
