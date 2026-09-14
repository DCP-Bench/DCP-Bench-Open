import z3


def build(instance):
    m = instance["m"]
    table = [[z3.Int(f"q_{i}_{j}") for j in range(m)] for i in range(m)]
    constraints = []
    for row in table:
        for cell in row:
            constraints.append(z3.And(cell >= 0, cell <= m - 1))
    for i in range(m):
        constraints.append(z3.Distinct(table[i]))
        constraints.append(z3.Distinct([table[r][i] for r in range(m)]))
    # The QG3 property indexes the table by two decision variables at once.
    # Z3 has no Element, so mirror the table into a flat array and read it with
    # Select at the computed offset row * m + column.
    flat = z3.Array("quasigroup_flat", z3.IntSort(), z3.IntSort())
    for i in range(m):
        for j in range(m):
            constraints.append(z3.Select(flat, i * m + j) == table[i][j])
    for a in range(m):
        for b in range(m):
            constraints.append(z3.Select(flat, table[a][b] * m + table[b][a]) == a)
    return constraints, {"quasigroup": table}
