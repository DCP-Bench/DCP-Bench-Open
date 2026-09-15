import cpmpy as cp


def build(instance):
    """Age changing: the same four operations, applied in two different orders,
    turn each spouse's age into the other's.

    The puzzle states its own operations and age range, so `instance` is
    unused.  The four operations are +2, /8, -3 and *7, numbered in that order.
    """
    del instance

    n = 4
    age_low, age_high = 16, 120

    m = cp.intvar(age_low, age_high, name="m")
    h = cp.intvar(age_low, age_high, name="h")

    perm1 = cp.intvar(0, n - 1, shape=n, name="perm1")
    perm2 = cp.intvar(0, n - 1, shape=n, name="perm2")

    # Running values as each operation is applied in turn.
    mlist = cp.intvar(1, 1000, shape=n + 1, name="mlist")
    hlist = cp.intvar(1, 1000, shape=n + 1, name="hlist")

    def check(op, old, new):
        # Division is stated as a multiplication so that only exact eighths
        # count, which is what the reference does.
        return [
            (op == 0).implies(new == old + 2),
            (op == 1).implies(8 * new == old),
            (op == 2).implies(new == old - 3),
            (op == 3).implies(new == old * 7),
        ]

    model = cp.Model(
        cp.AllDifferent(perm1),
        cp.AllDifferent(perm2),
        # The same operations, but in a different order.
        cp.sum([perm1[i] != perm2[i] for i in range(n)]) > 0,
        # Start from my age and finish at my husband's.
        hlist[0] == m,
        h == hlist[n],
        # Start from his age and finish at mine.
        mlist[0] == h,
        m == mlist[n],
    )
    for i in range(n):
        model += check(perm1[i], hlist[i], hlist[i + 1])
        model += check(perm2[i], mlist[i], mlist[i + 1])

    return model, {"m": m, "h": h}
