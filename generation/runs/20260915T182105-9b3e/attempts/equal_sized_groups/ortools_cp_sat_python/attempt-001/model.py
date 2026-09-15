from ortools.sat.python import cp_model


def build(instance):
    """Equal sized groups: cut a sorted list into k groups as close as possible
    to the ideal size, without splitting a run of equal values.
    """
    a = instance["a"]
    k = instance["k"]
    n = len(a)
    gsize = round(n / k)

    model = cp_model.CpModel()
    # s[i] is the size of group i, x[i] the 1-based index of break point i.
    s = [model.new_int_var(1, n, f"s{i}") for i in range(k)]
    x = [model.new_int_var(1, n, f"x{i}") for i in range(k - 1)]
    z = model.new_int_var(0, n, "z")

    errors = []
    for i in range(k):
        error = model.new_int_var(0, n, f"err{i}")
        model.add_abs_equality(error, s[i] - gsize)
        errors.append(error)
    model.add(z == sum(errors))

    # The first break point index is the size of the first group.
    model.add(s[0] == x[0])
    for i in range(1, k - 1):
        model.add(s[i] == x[i] - x[i - 1])
    model.add(s[k - 1] == n - x[k - 2])

    # Equal values stay together: where two neighbours are equal, no break
    # point may sit between them.  The comparison is over instance data, so it
    # resolves at build time and only the real restrictions are posted.
    for j in range(1, n):
        if a[j - 1] == a[j]:
            for p in range(k - 1):
                model.add(x[p] != j)

    model.minimize(z)

    return model, {"x": x}
