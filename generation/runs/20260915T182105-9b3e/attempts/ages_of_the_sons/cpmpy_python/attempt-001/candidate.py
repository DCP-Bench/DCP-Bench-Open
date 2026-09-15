import cpmpy as cp


def build(instance):
    """Ages of the sons: the product is 36, the sum is ambiguous, and there is
    a unique oldest.

    The puzzle states its own product, so `instance` is unused.  The second
    triple B is what makes the sum ambiguous: it is a different factorisation
    of 36 with the same sum, which is why the mathematician needed the extra
    clue about the oldest son.
    """
    del instance

    a1 = cp.intvar(0, 36, name="A1")
    a2 = cp.intvar(0, 36, name="A2")
    a3 = cp.intvar(0, 36, name="A3")

    b1 = cp.intvar(0, 36, name="B1")
    b2 = cp.intvar(0, 36, name="B2")
    b3 = cp.intvar(0, 36, name="B3")

    a_sum = cp.intvar(0, 1000, name="AS")
    b_sum = cp.intvar(0, 1000, name="BS")

    model = cp.Model(
        # A has a strictly oldest son.
        a1 > a2,
        a2 >= a3,
        36 == a1 * a2 * a3,
        # B is another triple with the same product and the same sum, and a
        # different eldest, so the sum alone could not decide between them.
        b1 >= b2,
        b2 >= b3,
        a1 != b1,
        36 == b1 * b2 * b3,
        a_sum == a1 + a2 + a3,
        b_sum == b1 + b2 + b3,
        a_sum == b_sum,
    )

    return model, {"A1": a1, "A2": a2, "A3": a3}
