# Reconstruct a 0/1 matrix from its row and column sums.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    row_sums = instance["row_sums"]
    col_sums = instance["col_sums"]
    rows, cols = len(row_sums), len(col_sums)

    pool = IDPool()
    # 0/1 integer variables rather than literals: the brief declares integers.
    matrix = [[Integer(f"m{i}_{j}", 0, 1, vpool=pool) for j in range(cols)]
              for i in range(rows)]
    flat = [cell for row in matrix for cell in row]
    engine = IntegerEngine(vars=flat, vpool=pool)
    for i in range(rows):
        engine.add_linear(sum(matrix[i][j] for j in range(cols)) == row_sums[i])
    for j in range(cols):
        engine.add_linear(sum(matrix[i][j] for i in range(rows)) == col_sums[j])
    return engine.clausify(), {"matrix": matrix}
