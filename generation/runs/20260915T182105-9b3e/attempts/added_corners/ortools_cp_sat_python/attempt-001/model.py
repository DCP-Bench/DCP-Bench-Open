from ortools.sat.python import cp_model


def build(instance):
    """Added corners: digits 1..8 around a ring, each square the sum of its
    two adjoining circles.

    The puzzle fixes its own size and layout, so `instance` carries nothing.
    """
    del instance

    n = 8
    model = cp_model.CpModel()
    positions = [model.new_int_var(1, n, f"p{i}") for i in range(n)]
    a, b, c, d, e, f, g, h = positions

    model.add_all_different(positions)
    # Reading order: a b c / d _ e / f g h. Each of b, d, e and g is a square
    # flanked by two circles.
    model.add(b == a + c)
    model.add(d == a + f)
    model.add(e == c + h)
    model.add(g == f + h)

    return model, {"positions": positions}
