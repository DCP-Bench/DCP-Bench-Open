# Equal sized groups: split a sorted list into k groups by choosing k - 1 break
# points, keeping equal values together, so that the group sizes are as close as
# possible to the ideal size round(n / k).
import z3


def build(instance):
    a = instance["a"]  # the sorted list of elements to divide
    k = instance["k"]  # number of groups
    n = len(a)
    gsize = round(n / k)  # ideal size of each group

    # s[i] is the number of elements in group i.
    s = [z3.Int(f"s_{i}") for i in range(k)]
    # x[i] is the (1-based) index of the i-th break point: the last element of group i.
    x = [z3.Int(f"x_{i}") for i in range(k - 1)]
    # z is the total error: the sum of the differences between group sizes and gsize.
    z = z3.Int("z")

    solver = z3.Solver()

    for si in s:
        solver.add(si >= 1, si <= n)
    for xi in x:
        solver.add(xi >= 1, xi <= n)
    solver.add(z >= 0, z <= n)

    # The error is the sum of the differences between each group size and the ideal size.
    solver.add(z == z3.Sum([z3.Abs(s[i] - gsize) for i in range(k)]))

    # The size of the first group is the index of the first break point, the size of a
    # middle group is the difference between its two break points, and the last group
    # holds the rest.
    solver.add(s[0] == x[0])
    for i in range(1, k - 1):
        solver.add(s[i] == x[i] - x[i - 1])
    solver.add(s[k - 1] == n - x[k - 2])

    # Equal values must be in the same group: no break point may fall between the
    # neighbouring elements j - 1 and j (1-based j) when they have the same value.
    # Written as separate not-equal tests, which Z3 checks lazily, instead of a long
    # disjunction of the allowed indices.
    for j in range(1, n):
        if a[j - 1] == a[j]:
            for xi in x:
                solver.add(xi != j)

    # Implied constraint: the first i + 1 groups together miss the ideal size
    # (i + 1) * gsize by at most the sum of their individual misses, and that sum is at
    # most z. So break point i lies within z of (i + 1) * gsize.
    for i in range(k - 1):
        solver.add(x[i] - (i + 1) * gsize <= z, (i + 1) * gsize - x[i] <= z)

    # Minimise the error.
    return solver, {"x": x}, ("minimize", z)
