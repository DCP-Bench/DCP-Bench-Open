import cpmpy as cp


def build(instance):
    """Hanging weights: thirteen distinct weights on a mobile of bars, each
    pivot balanced by distance-weighted load.

    The puzzle states its own diagram, so `instance` is unused.
    """
    del instance

    n = 13
    x = cp.intvar(1, n, shape=n, name="x")
    a, b, c, d, e, f, g, h, i, j, k, l, m = x

    model = cp.Model(
        cp.AllDifferent(x),
        4 * a == b,
        5 * c == d,
        3 * e == 2 * f,
        # A bar hanging under another contributes its whole load.
        3 * g == 2 * (c + d),
        3 * (a + b) + 2 * j == k + 2 * (g + c + d),
        3 * h == 2 * (e + f) + 3 * i,
        (h + i + e + f) == l + 4 * m,
        4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d),
    )

    return model, {
        "a": a, "b": b, "c": c, "d": d, "e": e, "f": f, "g": g,
        "h": h, "i": i, "j": j, "k": k, "l": l, "m": m,
    }
