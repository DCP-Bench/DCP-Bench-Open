import cpmpy as cp


def build(instance):
    """Bank card: a four-digit PIN abcd where cd is three times ab and da is
    twice bc.

    The puzzle states its own rules, so `instance` is unused.
    """
    del instance

    a, b, c, d = cp.intvar(0, 9, shape=4, name="pin")

    model = cp.Model(
        cp.AllDifferent([a, b, c, d]),
        10 * c + d == 3 * (10 * a + b),
        10 * d + a == 2 * (10 * b + c),
    )

    return model, {"a": a, "b": b, "c": c, "d": d}
