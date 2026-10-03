# Quasigroup existence, QG3.m: find an order m quasigroup, i.e. an m x m Latin square
# (every value 0..m-1 occurs once in every row and column), such that
# (a * b) * (b * a) = a for all a and b, where a * b is the entry in row a, column b.
from pychoco.model import Model


def build(instance):
    m = instance["m"]  # order of the quasigroup

    model = Model()

    # quasigroup[i][j] = the product i * j, a value between 0 and m-1
    quasigroup = [[model.intvar(0, m - 1, name=f"q_{i}_{j}") for j in range(m)] for i in range(m)]

    # each value occurs once in every row
    for i in range(m):
        model.all_different(quasigroup[i]).post()

    # each value occurs once in every column
    for j in range(m):
        model.all_different([quasigroup[i][j] for i in range(m)]).post()

    # QG3.m property: (a * b) * (b * a) = a.
    # The entry quasigroup[x][y] sits at position x * m + y of the table read row by row,
    # so the left side is looked up with element at x = a * b, y = b * a.
    table = [quasigroup[i][j] for i in range(m) for j in range(m)]
    for a in range(m):
        for b in range(m):
            position = model.intvar(0, m * m - 1, name=f"position_{a}_{b}")
            model.scalar([quasigroup[a][b], quasigroup[b][a], position], [m, 1, -1], "=", 0).post()
            model.element(model.intvar(a, a), table, position).post()

    return model, {"quasigroup": quasigroup}
