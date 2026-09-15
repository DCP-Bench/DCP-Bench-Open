import cpmpy as cp


def build(instance):
    """Hardy's 1729 square: four distinct numbers in 1..100 with
    a^2 + b^2 = c^2 + d^2.

    The puzzle states its own range, so `instance` is unused.
    """
    del instance

    range_min, range_max = 1, 100
    a, b, c, d = cp.intvar(range_min, range_max, shape=4, name="x")

    model = cp.Model(
        (a ** 2 + b ** 2) == (c ** 2 + d ** 2),
        cp.AllDifferent([a, b, c, d]),
    )

    return model, {"a": a, "b": b, "c": c, "d": d}
