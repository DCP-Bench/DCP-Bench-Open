import cpmpy as cp


def build(instance):
    """Broken weights: split a weight of m pounds into n whole pieces that can
    weigh every integer load from 1 to m on a balance scale.
    """
    m = instance["m"]
    n = instance["n"]

    weights = cp.intvar(1, m, shape=n, name="weights")
    # x[i, j] is -1, 0 or 1: which pan piece j goes in when weighing load i + 1,
    # or neither. Both pans are allowed, which is what makes a balance scale
    # able to weigh more loads than a simple subset sum.
    x = cp.intvar(-1, 1, shape=(m, n), name="x")

    model = cp.Model(
        cp.AllDifferent(weights),
        cp.sum(weights) == m,
    )
    for i in range(m):
        model += cp.sum([weights[j] * x[i, j] for j in range(n)]) == i + 1

    return model, {"weights": weights}
