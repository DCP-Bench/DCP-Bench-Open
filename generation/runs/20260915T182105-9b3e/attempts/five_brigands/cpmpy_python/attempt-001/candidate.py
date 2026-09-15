import cpmpy as cp


def build(instance):
    """Five brigands: 200 doubloons shared so that the reweighted shares also
    come to 200.

    The puzzle states its own total, so `instance` is unused.  The reweighting
    is 12A + 3B + C + D/2 + E/3; multiplying through by six clears both
    fractions, which is what the reference does.
    """
    del instance

    x = cp.intvar(1, 200, shape=5, name="x")
    a, b, c, d, e = x

    model = cp.Model(
        a + b + c + d + e == 200,
        6 * (a * 12 + b * 3 + c) + 3 * d + 2 * e == 6 * 200,
    )

    return model, {"A": a, "B": b, "C": c, "D": d, "E": e}
