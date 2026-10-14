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

    # is_value[i][j][v] is true when i * j = v
    is_value = [[[model.arithm(quasigroup[i][j], "=", v).reify() for v in range(m)]
                 for j in range(m)] for i in range(m)]

    # QG3.m property: (a * b) * (b * a) = a.
    # Written as an implication between the Booleans above for every a, b and every
    # possible value u = a * b and w = b * a: if a * b = u and b * a = w, then u * w = a.
    # This form propagates as soon as two of the three values are known. An element
    # constraint on the table of products (index a * b times m plus b * a) did not
    # solve order 9 within the time limit.
    for a in range(m):
        for b in range(m):
            for u in range(m):
                for w in range(m):
                    if a == b:
                        # a * a = u = w, so a * a = u implies u * u = a
                        if u == w:
                            model.scalar([is_value[a][a][u], is_value[u][u][a]], [1, -1], "<=", 0).post()
                    else:
                        # not (a * b = u and b * a = w) or u * w = a  <=>  x + y - z <= 1
                        model.scalar([is_value[a][b][u], is_value[b][a][w], is_value[u][w][a]],
                                     [1, 1, -1], "<=", 1).post()

    return model, {"quasigroup": quasigroup}
