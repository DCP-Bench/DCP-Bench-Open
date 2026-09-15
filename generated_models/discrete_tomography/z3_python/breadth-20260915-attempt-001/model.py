import z3


def build(instance):
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, columns = len(row_sums), len(col_sums)
    matrix = [[z3.Int(f"x_{i}_{j}") for j in range(columns)] for i in range(rows)]
    constraints = [cell >= 0 for row in matrix for cell in row]
    constraints += [cell <= 1 for row in matrix for cell in row]
    for i in range(rows):
        constraints.append(z3.Sum(matrix[i]) == row_sums[i])
    for j in range(columns):
        constraints.append(z3.Sum([matrix[i][j] for i in range(rows)]) == col_sums[j])
    return constraints, {"matrix": matrix}
