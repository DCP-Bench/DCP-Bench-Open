import cpmpy as cp


def build(instance):
    m = instance["m"]
    quasigroup = cp.intvar(0, m - 1, shape=(m, m), name="quasigroup")
    model = cp.Model()
    for i in range(m):
        model += cp.AllDifferent(quasigroup[i, :])
        model += cp.AllDifferent(quasigroup[:, i])
    # QG3.m: (a * b) * (b * a) = a.
    for a in range(m):
        for b in range(m):
            model += quasigroup[quasigroup[a, b], quasigroup[b, a]] == a
    return model, {"quasigroup": [[quasigroup[i, j] for j in range(m)] for i in range(m)]}
