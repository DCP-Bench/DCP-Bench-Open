from pychoco.model import Model


def build(instance):
    """Bowls and oranges: place m oranges in n bowls spaced a metre apart so
    that no three of them are evenly spaced.
    """
    n = instance["n"]
    m = instance["m"]

    model = Model()
    x = [model.intvar(1, n, name=f"x{i}") for i in range(m)]

    model.all_different(x).post()
    # Positions are reported in ascending order.
    for i in range(1, m):
        model.arithm(x[i - 1], "<=", x[i]).post()
    # No three oranges A, B, C with B as far from A as C is from B.
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                model.scalar([x[j], x[i], x[k]], [2, -1, -1], "!=", 0).post()

    return model, {"x": x}
