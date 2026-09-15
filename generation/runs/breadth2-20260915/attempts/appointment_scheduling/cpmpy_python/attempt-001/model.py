import cpmpy as cp


def build(instance):
    free = instance["m"]
    n = len(free)
    booked = cp.boolvar(shape=(n, n), name="x")
    model = cp.Model()
    for i in range(n):
        model += cp.sum([free[i][j] * booked[i, j] for j in range(n)]) == 1
        model += cp.sum([booked[i, j] for j in range(n)]) == 1
        model += cp.sum([booked[j, i] for j in range(n)]) == 1
    return model, {"x": [[booked[i, j] for j in range(n)] for i in range(n)]}
