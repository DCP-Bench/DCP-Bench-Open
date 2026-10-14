# Equal sized groups: split a sorted list into k groups by choosing k - 1 break
# points, keeping equal values together, so that the group sizes are as close as
# possible to the ideal size round(n / k).
import functools
import operator

import z3


def build(instance):
    a = instance["a"]  # the sorted list of elements to divide
    k = instance["k"]  # number of groups
    n = len(a)
    gsize = round(n / k)  # ideal size of each group

    # The break points are bit-vectors: Z3's bit-vector solver turns the sums and
    # differences of group sizes into Boolean circuits, and learns from conflicts between
    # break points much better than its integer solver does on this problem. The width
    # leaves room for the sum of k group-size errors, so nothing wraps round.
    width = (k * n).bit_length() + 1

    def const(value):
        return z3.BitVecVal(value, width)

    # x[i] is the (1-based) index of the i-th break point: the last element of group i.
    x = [z3.BitVec(f"x_{i}", width) for i in range(k - 1)]

    solver = z3.Solver()

    # Break points are indices 1..n.
    for xi in x:
        solver.add(z3.UGE(xi, const(1)), z3.ULE(xi, const(n)))

    # s[i] is the number of elements in group i: the size of the first group is the
    # index of the first break point, the size of a middle group is the difference between
    # its two break points, and the last group holds the rest. Every group is non-empty,
    # so the break points are strictly increasing and the last one is below n.
    s = [x[0]]
    for i in range(1, k - 1):
        solver.add(z3.UGT(x[i], x[i - 1]))
        s.append(x[i] - x[i - 1])
    solver.add(z3.ULT(x[k - 2], const(n)))
    s.append(const(n) - x[k - 2])

    # Equal values must be in the same group: no break point may fall between the
    # neighbouring elements j - 1 and j (1-based j) when they have the same value.
    # Only the indices where the value changes are allowed (and n, which is excluded above).
    allowed = [j for j in range(1, n + 1) if j == n or a[j - 1] != a[j]]
    for xi in x:
        solver.add(z3.Or([xi == const(j) for j in allowed]))

    # z is the total error: the sum of the differences between group sizes and gsize.
    def miss(size):
        return z3.If(z3.UGE(size, const(gsize)), size - const(gsize), const(gsize) - size)

    z = functools.reduce(operator.add, [miss(si) for si in s])
    solver.add(z3.ULE(z, const(n)))  # the reference bounds the error between 0 and n

    # Minimise the error; the break points are reported as integers.
    return solver, {"x": [z3.BV2Int(xi) for xi in x]}, ("minimize", z3.BV2Int(z))
