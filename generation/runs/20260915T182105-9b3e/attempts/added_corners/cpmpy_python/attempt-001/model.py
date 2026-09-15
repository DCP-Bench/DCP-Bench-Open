import cpmpy as cp


def build(instance):
    """Added corners: digits 1..8 around a ring, each square the sum of its
    two adjoining circles.

    The puzzle fixes its own size and layout, so `instance` carries nothing.
    """
    del instance

    n = 8
    positions = cp.intvar(1, n, shape=n, name="positions")
    a, b, c, d, e, f, g, h = positions

    model = cp.Model(
        cp.AllDifferent(positions),
        # Reading order: a b c / d _ e / f g h. Each of b, d, e and g is a
        # square flanked by two circles.
        b == a + c,
        d == a + f,
        e == c + h,
        g == f + h,
    )

    return model, {"positions": positions}
