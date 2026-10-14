# Equal sized groups: split a sorted list of n elements into k consecutive
# groups by choosing k-1 break points, never separating equal values, so that
# the group sizes are as close as possible to the ideal size round(n / k)
# (minimise the sum of the absolute differences from it).
import functools
import operator

from hermax.model import Model


def build(instance):
    a = instance["a"]  # the sorted elements
    k = instance["k"]  # number of groups
    n = len(a)
    ideal = round(n / k)  # ideal group size, rounded the way the problem statement does

    # A break point x means "the first x elements form the groups before the break"
    # (1-based, as in the declared output). It may not fall between two equal
    # values, so the usable break points are the places where the value changes.
    breaks = [j for j in range(1, n) if a[j - 1] != a[j]]

    # The groups form a path through the places 0 (before the first element), the
    # usable break points and n (after the last element). Taking an edge p -> q
    # means one group holds the elements between places p and q; its error
    # is |q - p - ideal|. Choosing k groups is choosing a path with k edges.
    places = [0] + breaks + [n]
    last = len(places) - 1  # index of the place n

    m = Model()
    # edge[(p, q)] = a group runs from place p to place q (p < q, as indices of `places`)
    edge = {(p, q): m.bool(f"edge_{p}_{q}") for p in range(last) for q in range(p + 1, last + 1)}
    # used[c] = the break point places[c] is one of the chosen break points
    used = m.bool_vector("used", last + 1)

    leaving = {p: [edge[(p, q)] for q in range(p + 1, last + 1)] for p in range(last)}
    entering = {q: [edge[(p, q)] for p in range(q)] for q in range(1, last + 1)}

    # The path starts at place 0 with exactly one group and ends at place n with
    # exactly one group.
    m &= (sum(leaving[0]) == 1)
    m &= (sum(entering[last]) == 1)

    # A break point is used when a group ends there, and then also when a group
    # starts there; at most one group ends and one starts at each break point.
    for c in range(1, last):
        m &= (sum(entering[c]) <= 1)
        m &= (sum(leaving[c]) <= 1)
        for e in entering[c] + leaving[c]:
            m &= (~e | used[c])
        m &= (~used[c] | functools.reduce(operator.or_, entering[c]))
        m &= (~used[c] | functools.reduce(operator.or_, leaving[c]))

    # k groups need k - 1 break points
    m &= (sum(used[c] for c in range(1, last)) == k - 1)

    # Minimise the total error: a group between places p and q that is not of the
    # ideal size costs |q - p - ideal|. A soft clause pays when its literal is
    # false, so the group is charged on the negated edge literal.
    for (p, q), e in edge.items():
        error = abs(places[q] - places[p] - ideal)
        if error > 0:
            m.obj[error] += ~e

    # x[i] = the i-th break point (the declared output). reaches[i][c] says the
    # i-th group (counting from 0) ends at place c; it is forced by the path, and
    # the break point it names is then the value of x[i].
    x = m.int_vector("x", k - 1, breaks[0], breaks[-1])
    reaches = [{c: m.bool(f"reaches_{i}_{c}") for c in range(1, last)} for i in range(k - 1)]
    for c in range(1, last):
        m &= (~edge[(0, c)] | reaches[0][c])
    for i in range(1, k - 1):
        for p in range(1, last):
            for q in range(p + 1, last):
                m &= (~reaches[i - 1][p] | ~edge[(p, q)] | reaches[i][q])
    for i in range(k - 1):
        for c in range(1, last):
            m &= (~reaches[i][c] | (x[i] == places[c]))

    return m, {"x": x}
