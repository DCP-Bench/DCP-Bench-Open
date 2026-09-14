import cpmpy as cp


def build(instance):
    n = instance["n"]
    x, y = cp.intvar(0, n, shape=2)
    model = cp.Model(x + y >= n if instance["optimize"] else x + y == n)
    if instance["optimize"]:
        model.minimize(x + y)
    return model, {"x": x, "y": y}
