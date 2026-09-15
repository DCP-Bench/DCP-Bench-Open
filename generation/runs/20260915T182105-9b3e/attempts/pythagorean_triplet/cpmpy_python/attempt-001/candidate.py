import cpmpy as cp


def build(instance):
    """Pythagorean triplet: the one whose three members sum to 1000.

    The puzzle states its own total, so `instance` is unused.
    """
    del instance

    a, b, c = cp.intvar(1, 500, shape=3, name="x")

    model = cp.Model(
        a + b + c == 1000,
        a * a + b * b == c * c,
    )

    return model, {"a": a, "b": b, "c": c}
