import cpmpy as cp


def build(instance):
    """Bowls and oranges: place m oranges in n bowls spaced a metre apart so
    that no three of them are evenly spaced.
    """
    n = instance["n"]
    m = instance["m"]

    x = cp.intvar(1, n, shape=m, name="x")

    model = cp.Model(cp.AllDifferent(x))
    # Positions are reported in ascending order.
    model += [x[i - 1] <= x[i] for i in range(1, m)]
    # No three oranges A, B, C with B as far from A as C is from B.
    for i in range(m):
        for j in range(i + 1, m):
            for k in range(j + 1, m):
                model += (x[j] - x[i]) != (x[k] - x[j])

    return model, {"x": x}
