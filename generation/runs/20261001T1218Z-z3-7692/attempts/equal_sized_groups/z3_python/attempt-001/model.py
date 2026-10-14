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

    # Equal values must be in the same group: a break point cannot fall between two
    # neighbouring elements j - 1 and j (1-based j) with the same value. The allowed
    # break indices are listed once, instead of a not-equal test for every break
    # point and every forbidden index.
    allowed = [j for j in range(1, n + 1) if j == n or a[j - 1] != a[j]]
    for xi in x:
        solver.add(z3.Or([xi == j for j in allowed]))

    # Minimise the error.
    return solver, {"x": x}, ("minimize", z)
