import cpmpy as cp


def build(instance):
    n = instance["n"]
    x = cp.intvar(0, n - 1, shape=n, name="x")
    model = cp.Model([x[i] == cp.Count(x, i) for i in range(n)])
    return model, {"x": [x[i] for i in range(n)]}
