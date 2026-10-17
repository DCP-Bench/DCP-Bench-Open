import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    x, y = cz.Ints("x y")
    # cvc5 integers are unbounded, so the bounds the reference declares must be added.
    bounds = [x >= 0, x <= n, y >= 0, y <= n]
    if instance["optimize"]:
        return bounds + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
    return bounds + [x + y == n], {"x": x, "y": y}
