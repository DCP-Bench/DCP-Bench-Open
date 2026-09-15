from ortools.sat.python import cp_model


def build(instance):
    """Hanging weights: thirteen distinct weights on a mobile of bars, each
    pivot balanced by distance-weighted load.

    The puzzle states its own diagram, so `instance` is unused.
    """
    del instance

    n = 13
    model = cp_model.CpModel()
    names = "abcdefghijklm"
    x = [model.new_int_var(1, n, name) for name in names]
    a, b, c, d, e, f, g, h, i, j, k, l, m = x

    model.add_all_different(x)
    model.add(4 * a == b)
    model.add(5 * c == d)
    model.add(3 * e == 2 * f)
    # A bar hanging under another contributes its whole load.
    model.add(3 * g == 2 * (c + d))
    model.add(3 * (a + b) + 2 * j == k + 2 * (g + c + d))
    model.add(3 * h == 2 * (e + f) + 3 * i)
    model.add(h + i + e + f == l + 4 * m)
    model.add(4 * (l + m + h + i + e + f) == 3 * (j + k + g + a + b + c + d))

    return model, dict(zip(names, x))
