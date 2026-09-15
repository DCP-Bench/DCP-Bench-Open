import cpmpy as cp


def build(instance):
    """Clock triplets: rearrange 1..12 around a clock face so that no three
    adjacent numbers sum above 21.

    The puzzle fixes the clock, so `instance` is unused.
    """
    del instance

    n = 12
    x = cp.intvar(1, n, shape=n, name="x")
    # The reference caps the largest triplet sum at 21 by declaring the
    # variable's domain rather than by optimizing.
    triplet_sum = cp.intvar(0, 21, name="triplet_sum")

    model = cp.Model(cp.AllDifferent(x))
    # Triplets wrap around the face, as the reference's negative indices do.
    for i in range(n):
        model += x[i] + x[(i - 1) % n] + x[(i - 2) % n] <= triplet_sum

    return model, {"x": x}
