import cpmpy as cp


def build(instance):
    """Equal sized groups: cut a sorted list into k groups as close as possible
    to the ideal size, without splitting a run of equal values.
    """
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    gsize = round(n / k)

    # s[i] is the size of group i, x[i] the 1-based index of break point i.
    s = cp.intvar(1, n, shape=k, name="s")
    x = cp.intvar(1, n, shape=k - 1, name="x")
    z = cp.intvar(0, n, name="z")

    constraints = [
        z == cp.sum([cp.abs(s[i] - gsize) for i in range(k)]),
        # The first break point index is the size of the first group.
        s[0] == x[0],
    ]
    for i in range(1, k - 1):
        constraints.append(s[i] == x[i] - x[i - 1])
    constraints.append(s[k - 1] == n - x[k - 2])

    # Equal values stay together: where two neighbours are equal, no break
    # point may sit between them.  The comparison is over instance data, so it
    # resolves at build time and only the real restrictions are posted.
    for j in range(1, n):
        if a[j - 1] == a[j]:
            constraints += [x[p] != j for p in range(k - 1)]

    model = cp.Model(constraints)
    model.minimize(z)

    return model, {"x": x}
