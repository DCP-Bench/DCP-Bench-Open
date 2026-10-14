# Equal sized groups: split a sorted list into k groups by choosing k - 1 break
# points, keeping equal values together, so that the group sizes are as close as
# possible to the ideal size round(n / k).
import z3


def build(instance):
    a = instance["a"]  # the sorted list of elements to divide
    k = instance["k"]  # number of groups
    n = len(a)
    gsize = round(n / k)  # ideal size of each group

    # Equal values must be in the same group, so a break point (the 1-based index of the
    # last element of a group) cannot fall between neighbouring elements j and j + 1 with
    # the same value. The last group must be non-empty, so no break is at index n.
    positions = [j for j in range(1, n) if a[j - 1] != a[j]]
    m = len(positions)

    # at[i][c] is true if break point i is at index positions[c]. Choosing each break
    # point by Booleans lets Z3 learn from conflicts between neighbouring break points,
    # which it cannot do over integer variables restricted to a long list of values.
    at = [[z3.Bool(f"at_{i}_{c}") for c in range(m)] for i in range(k - 1)]
    # upto[i][c] is true if break point i is at one of the first c + 1 allowed indices.
    upto = [[z3.Bool(f"upto_{i}_{c}") for c in range(m)] for i in range(k - 1)]
    # x[i] is the (1-based) index of the i-th break point: the last element of group i.
    x = [z3.Int(f"x_{i}") for i in range(k - 1)]
    # s[i] is the number of elements in group i.
    s = [z3.Int(f"s_{i}") for i in range(k)]
    # z is the total error: the sum of the differences between group sizes and gsize.
    z = z3.Int("z")

    solver = z3.Solver()

    # Each break point sits at exactly one allowed index.
    for i in range(k - 1):
        solver.add(z3.PbEq([(at[i][c], 1) for c in range(m)], 1))
        for c in range(m):
            solver.add(upto[i][c] == (at[i][c] if c == 0 else z3.Or(upto[i][c - 1], at[i][c])))
        # x[i] is the index it sits at.
        solver.add(x[i] == z3.Sum([z3.If(at[i][c], positions[c], 0) for c in range(m)]))

    # The break points are in increasing order: break point i comes after break point i - 1.
    for i in range(1, k - 1):
        for c in range(m):
            solver.add(z3.Implies(at[i - 1][c], z3.Not(upto[i][c])))

    # The size of the first group is the index of the first break point, the size of a
    # middle group is the difference between its two break points, and the last group
    # holds the rest.
    solver.add(s[0] == x[0])
    for i in range(1, k - 1):
        solver.add(s[i] == x[i] - x[i - 1])
    solver.add(s[k - 1] == n - x[k - 2])
    for si in s:
        solver.add(si >= 1, si <= n)

    # The error is the sum of the differences between each group size and the ideal size.
    solver.add(z >= 0, z <= n)
    solver.add(z == z3.Sum([z3.Abs(s[i] - gsize) for i in range(k)]))

    # Implied constraint: the first i + 1 groups together miss the ideal size
    # (i + 1) * gsize by at most the sum of their individual misses, and that sum is at
    # most z. So break point i lies within z of (i + 1) * gsize.
    for i in range(k - 1):
        solver.add(x[i] - (i + 1) * gsize <= z, (i + 1) * gsize - x[i] <= z)

    # Minimise the error.
    return solver, {"x": x}, ("minimize", z)
