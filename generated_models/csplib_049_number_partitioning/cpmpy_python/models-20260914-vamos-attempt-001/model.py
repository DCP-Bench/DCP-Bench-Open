import cpmpy as cp


def build(instance):
    n = instance["n"]
    half = n // 2
    x = cp.intvar(1, n, shape=half, name="x")
    y = cp.intvar(1, n, shape=half, name="y")
    model = cp.Model(
        cp.AllDifferent([x[i] for i in range(half)] + [y[i] for i in range(half)]),
        cp.sum(x) == cp.sum(y),
        cp.sum(x ** 2) == cp.sum(y ** 2),
    )
    return model, {"A": [x[i] for i in range(half)],
                   "B": [y[i] for i in range(half)]}
