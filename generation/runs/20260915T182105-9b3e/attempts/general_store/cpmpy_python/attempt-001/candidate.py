import cpmpy as cp


def build(instance):
    """General store: a sixteen-line alphametic whose total is ALL WOOL.

    The puzzle states its own sign, so `instance` is unused.  Each of the ten
    letters stands for a different digit.
    """
    del instance

    n = 10
    x = cp.intvar(0, 9, shape=n, name="x")
    C, H, E, S, A, B, O, W, P, L = x

    model = cp.Model(
        cp.AllDifferent(x),
        10000 * C + 1000 * H + 100 * E + 10 * S + S
        + 1000 * C + 100 * A + 10 * S + H
        + 100000 * B + 10000 * O + 1000 * W + 100 * W + 10 * O + W
        + 10000 * C + 1000 * H + 100 * O + 10 * P + S
        + 100000 * A + 10000 * L + 1000 * S + 100 * O + 10 * P + S
        + 1000000 * P + 100000 * A + 10000 * L + 1000 * E + 100 * A + 10 * L + E
        + 1000 * C + 100 * O + 10 * O + L
        + 1000 * B + 100 * A + 10 * S + S
        + 1000 * H + 100 * O + 10 * P + S
        + 1000 * A + 100 * L + 10 * E + S
        + 1000 * H + 100 * O + 10 * E + S
        + 100000 * A + 10000 * P + 1000 * P + 100 * L + 10 * E + S
        + 1000 * C + 100 * O + 10 * W + S
        + 100000 * C + 10000 * H + 1000 * E + 100 * E + 10 * S + E
        + 100000 * C + 10000 * H + 1000 * S + 100 * O + 10 * A + P
        + 10000 * S + 1000 * H + 100 * E + 10 * E + P
        == 1000000 * A + 100000 * L + 10000 * L + 1000 * W + 100 * O + 10 * O + L,
    )

    return model, {
        "C": C, "H": H, "E": E, "S": S, "A": A,
        "B": B, "O": O, "W": W, "P": P, "L": L,
    }
