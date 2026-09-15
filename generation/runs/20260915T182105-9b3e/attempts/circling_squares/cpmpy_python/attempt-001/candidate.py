import cpmpy as cp


def build(instance):
    """Circling the squares: ten different numbers around a circle where any
    two adjacent squares sum to the same as the two diametrically opposite.

    The puzzle states its own four given numbers, so `instance` is unused.
    """
    del instance

    n = 10
    x = cp.intvar(1, 99, shape=n, name="x")
    a, b, c, d, e, f, g, h, i, k = x

    def balanced(first, second, third, fourth):
        return first * first + second * second == third * third + fourth * fourth

    model = cp.Model(
        cp.AllDifferent(x),
        # The four numbers given as examples.
        a == 16,
        b == 2,
        f == 8,
        g == 14,
        balanced(a, b, f, g),
        balanced(b, c, g, h),
        balanced(c, d, h, i),
        balanced(d, e, i, k),
        balanced(e, f, k, a),
    )

    return model, {
        "A": a, "B": b, "C": c, "D": d, "E": e,
        "F": f, "G": g, "H": h, "I": i, "K": k,
    }
