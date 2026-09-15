from ortools.sat.python import cp_model


def build(instance):
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, columns = len(row_sums), len(col_sums)
    model = cp_model.CpModel()
    matrix = [[model.new_int_var(0, 1, f"x_{i}_{j}") for j in range(columns)] for i in range(rows)]
    for i in range(rows):
        model.add(sum(matrix[i]) == row_sums[i])
    for j in range(columns):
        model.add(sum(matrix[i][j] for i in range(rows)) == col_sums[j])
    return model, {"matrix": matrix}
