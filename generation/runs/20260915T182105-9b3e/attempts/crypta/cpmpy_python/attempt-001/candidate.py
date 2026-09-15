import cpmpy as cp


def build(instance):
    """Crypta: a twenty-letter cryptarithmetic addition over ten distinct
    digits.

    The puzzle states its own sum, so `instance` is unused.  The addition is
    checked seven digits at a time, with Sr1 and Sr2 carrying between blocks,
    exactly as the reference splits it.
    """
    del instance

    letters = cp.intvar(0, 9, shape=10, name="LD")
    a, b, c, d, e, f, g, h, i, j = letters

    carry1 = cp.intvar(0, 1, name="Sr1")
    carry2 = cp.intvar(0, 1, name="Sr2")

    model = cp.Model(cp.AllDifferent(letters))
    # No number may start with a zero.
    model += b >= 1
    model += d >= 1
    model += g >= 1

    model += (
        a + 10 * e + 100 * j + 1000 * b + 10000 * b + 100000 * e
        + 1000000 * f + e + 10 * j + 100 * e + 1000 * f + 10000 * g
        + 100000 * a + 1000000 * f
        == f + 10 * e + 100 * e + 1000 * h + 10000 * i + 100000 * f
        + 1000000 * b + 10000000 * carry1
    )
    model += (
        c + 10 * f + 100 * h + 1000 * a + 10000 * i + 100000 * i
        + 1000000 * j + f + 10 * i + 100 * b + 1000 * d + 10000 * i
        + 100000 * d + 1000000 * c + carry1
        == j + 10 * f + 100 * a + 1000 * f + 10000 * h + 100000 * d
        + 1000000 * d + 10000000 * carry2
    )
    model += (
        a + 10 * j + 100 * j + 1000 * i + 10000 * a + 100000 * b + b
        + 10 * a + 100 * g + 1000 * f + 10000 * h + 100000 * d + carry2
        == c + 10 * a + 100 * g + 1000 * e + 10000 * j + 100000 * g
    )

    return model, {
        "A": a, "B": b, "C": c, "D": d, "E": e,
        "F": f, "G": g, "H": h, "I": i, "J": j,
    }
