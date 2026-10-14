# Equal-sized groups: split a sorted list of n elements into k consecutive groups by choosing
# k-1 break points, never separating equal values, so that the group sizes are as close as
# possible to the ideal size round(n / k) (minimise the sum of the absolute size errors).
from exact import Exact


def build(instance):
    a = instance["a"]  # the sorted elements to divide
    k = instance["k"]  # number of groups
    n = len(a)
    ideal = round(n / k)  # ideal (average) size of a group

    # A break point x = j puts the first j elements before it. Equal values must stay in one
    # group, so j is allowed only where a[j-1] differs from a[j]; this is where the problem
    # statement's "same value in the same group" rule is used.
    allowed = [j for j in range(1, n) if a[j - 1] != a[j]]

    solver = Exact()

    # x[p] is the p-th break point, the 1-based index of the last element of group p
    x = [f"break_{p}" for p in range(k - 1)]
    for name in x:
        solver.addVariable(name, 1, n - 1)

    # at[p][j] = 1 when break point p is at index j. Restricting x to the allowed positions is a
    # set-membership constraint, which Exact has no native form for, so indicators over the
    # allowed positions (at most the number of distinct values) are used.
    at = [[f"break_{p}_at_{j}" for j in allowed] for p in range(k - 1)]
    for p in range(k - 1):
        for name in at[p]:
            solver.addVariable(name, 0, 1)
        solver.addConstraint([(1, name) for name in at[p]], True, 1, True, 1)
        solver.addConstraint([(j, name) for j, name in zip(allowed, at[p])] + [(-1, x[p])],
                             True, 0, True, 0)

    # every group is nonempty, so the break points are strictly increasing
    for p in range(1, k - 1):
        solver.addConstraint([(1, x[p]), (-1, x[p - 1])], True, 1)

    # the size of group i: the first group ends at x[0], the last starts after x[k-2]
    sizes = []
    for i in range(k):
        if i == 0:
            sizes.append(([(1, x[0])], 0))
        elif i < k - 1:
            sizes.append(([(1, x[i]), (-1, x[i - 1])], 0))
        else:
            sizes.append(([(-1, x[k - 2])], n))  # n - x[k-2]

    # error[i] is the difference between the size of group i and the ideal size. It is bounded
    # below by both signed differences, which for a minimised sum makes it equal to the absolute
    # difference (the reference's abs).
    error = [f"error_{i}" for i in range(k)]
    for i in range(k):
        solver.addVariable(error[i], 0, n)
        terms, constant = sizes[i]
        # error >= size - ideal  and  error >= ideal - size
        solver.addConstraint([(1, error[i])] + [(-c, v) for c, v in terms], True, constant - ideal)
        solver.addConstraint([(1, error[i])] + terms, True, ideal - constant)

    # minimise the total error
    return solver, {"x": x}, ("minimize", [(1, name) for name in error])
