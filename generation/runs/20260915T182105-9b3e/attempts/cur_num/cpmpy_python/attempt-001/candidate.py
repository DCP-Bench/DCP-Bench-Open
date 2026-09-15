import cpmpy as cp


def build(instance):
    """Curious number: one more than it is a square, and one more than its
    half is a square too - and it is not 48, which is the known example.

    The puzzle fixes its own range, so `instance` is unused.
    """
    del instance

    peculiar, a, b, c, d, e = cp.intvar(1, 10000, shape=6, name="x")

    model = cp.Model(
        peculiar != 48,
        # Add one and you get a square.
        peculiar + 1 == a,
        a == b * b,
        # Halve it, add one, and you get a square again.
        peculiar == 2 * c,
        c + 1 == d,
        d == e * e,
    )

    return model, {"peculiar": peculiar}
