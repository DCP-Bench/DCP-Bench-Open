import z3


def build(instance):
    n = instance["n"]
    x, y = z3.Ints("x y")
    # z3.Int has no domain, so the bounds the reference declares must be added.
    bounds = [x >= 0, x <= n, y >= 0, y <= n]
    if instance["optimize"]:
        return bounds + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
    return bounds + [x + y == n], {"x": x, "y": y}
