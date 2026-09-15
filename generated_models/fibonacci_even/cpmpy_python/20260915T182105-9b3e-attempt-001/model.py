import cpmpy as cp


def build(instance):
    """Fibonacci even: sum the even Fibonacci terms below four million.

    The puzzle states its own sequence and cutoff, so `instance` is unused.
    Thirty-five terms is enough to pass four million comfortably.
    """
    del instance

    n = 35
    cutoff = 4000000

    f = cp.intvar(0, 10000000, shape=n + 1, name="f")
    x = cp.boolvar(shape=n + 1, name="x")
    res = cp.intvar(0, 100000000, name="res")

    model = cp.Model(
        res == cp.sum([x[i] * f[i] for i in range(1, n + 1)]),
        f[0] == 0,
        f[1] == 1,
        f[2] == 1,
        x[0] == 0,
        [f[i] == f[i - 1] + f[i - 2] for i in range(3, n + 1)],
        # A term counts exactly when it is even and below the cutoff.
        [
            ((f[i] % 2 == 0) & (f[i] < cutoff)) == (x[i] == 1)
            for i in range(1, n + 1)
        ],
    )

    return model, {"res": res}
