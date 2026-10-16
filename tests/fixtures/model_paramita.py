from paramita.modelling import Bool


def build(instance):
    n = instance["n"]
    # x and y each take a value in 0..n as a unary sum of Bools, with the order
    # constraint that a higher Bool is set only when the one below it is.
    xs = [Bool(f"x{i}") for i in range(n)]
    ys = [Bool(f"y{i}") for i in range(n)]
    order = [~xs[i + 1] | xs[i] for i in range(n - 1)] + [~ys[i + 1] | ys[i] for i in range(n - 1)]
    x = sum(xs)
    y = sum(ys)
    if not instance["optimize"]:
        return order + [x + y == n], {"x": x, "y": y}
    return order + [x + y >= n], {"x": x, "y": y}, ("minimize", x + y)
