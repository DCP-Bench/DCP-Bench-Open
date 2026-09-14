from ortools.sat.python import cp_model


def build(instance):
    m = instance["m"]
    model = cp_model.CpModel()
    q = [[model.new_int_var(0, m - 1, f"q_{i}_{j}") for j in range(m)] for i in range(m)]
    for i in range(m):
        model.add_all_different(q[i])
        model.add_all_different([q[j][i] for j in range(m)])
    flat = [q[i][j] for i in range(m) for j in range(m)]
    # QG3.m: (a * b) * (b * a) = a, as an element constraint on the flattened table.
    for a in range(m):
        for b in range(m):
            index = model.new_int_var(0, m * m - 1, f"index_{a}_{b}")
            model.add(index == m * q[a][b] + q[b][a])
            model.add_element(index, flat, a)
    return model, {"quasigroup": q}
