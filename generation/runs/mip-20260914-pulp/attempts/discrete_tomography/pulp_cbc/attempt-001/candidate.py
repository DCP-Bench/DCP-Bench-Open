import pulp


def build(instance):
    row_sums, col_sums = instance["row_sums"], instance["col_sums"]
    rows, columns = range(len(row_sums)), range(len(col_sums))
    problem = pulp.LpProblem("discrete_tomography", pulp.LpMinimize)
    matrix = [[pulp.LpVariable(f"cell_{i}_{j}", cat="Binary") for j in columns] for i in rows]
    for i in rows:
        problem += pulp.lpSum(matrix[i]) == row_sums[i]
    for j in columns:
        problem += pulp.lpSum(matrix[i][j] for i in rows) == col_sums[j]
    return problem, {"matrix": matrix}
