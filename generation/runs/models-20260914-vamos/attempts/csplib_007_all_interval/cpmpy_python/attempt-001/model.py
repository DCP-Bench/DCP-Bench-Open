import cpmpy as cp


def build(instance):
    n = instance["n"]
    x = cp.intvar(0, n - 1, shape=n, name="x")
    diffs = cp.intvar(1, n - 1, shape=n - 1, name="diffs")
    model = cp.Model(cp.AllDifferent(x), cp.AllDifferent(diffs))
    model += [diffs[i] == cp.abs(x[i + 1] - x[i]) for i in range(n - 1)]
    return model, {"x": [x[i] for i in range(n)],
                   "diffs": [diffs[i] for i in range(n - 1)]}
