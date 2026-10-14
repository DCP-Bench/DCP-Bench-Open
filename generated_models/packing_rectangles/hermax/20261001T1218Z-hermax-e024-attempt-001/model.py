# Rectangle packing: place rectangles of given widths and heights, without rotation,
# inside a larger rectangle so that they do not overlap and the area of the larger
# rectangle (total_x * total_y) is as small as possible.
import functools
import operator

from hermax.model import Model


def ranged_int(m, name, lo, hi):
    """An integer variable with values lo..hi. hermax wants at least two values, so a
    single-value range gets one spare value that is ruled out."""
    if lo < hi:
        return m.int(name, lo, hi)
    x = m.int(name, lo, lo + 1)
    m &= ~(x >= lo + 1)
    return x


def at_least(x, k):
    """The literal (x >= k); True or False when k is outside the range of x."""
    if k <= x.lb:
        return True
    if k > x.ub:
        return False
    return x >= k


def post(m, *lits):
    """Post the clause over the given literals. True or False entries stand for
    constants: a True entry satisfies the clause and False entries drop out."""
    kept = []
    for lit in lits:
        if lit is True:
            return
        if lit is not False:
            kept.append(lit)
    m &= functools.reduce(operator.or_, kept)


def neg(lit):
    return (not lit) if isinstance(lit, bool) else ~lit


def post_before(m, relax, first, offset, second):
    """Post: first + offset <= second, unless the literal `relax` holds.

    hermax integers use an order encoding, where the literal (x >= k) says "x is at
    least k"; the difference constraint is written out on those literals (first >= k
    forces second >= k + offset), one short clause per value of `first`, instead of a
    pseudo-Boolean sum over the whole coordinate range. A relax of None means always.
    """
    for k in range(first.lb, first.ub + 1):
        lits = [neg(at_least(first, k)), at_least(second, k + offset)]
        if relax is not None:
            lits.append(relax)
        post(m, *lits)


def build(instance):
    widths = instance["widths"]  # widths[i] = width of item i
    heights = instance["heights"]  # heights[i] = height of item i
    n = len(widths)

    # The larger rectangle is at least as wide as the widest item and no wider than
    # all items side by side (and likewise in height); these are the reference's bounds.
    min_x, max_x = max(widths), sum(widths)
    min_y, max_y = max(heights), sum(heights)

    m = Model()
    # pos_x[i], pos_y[i] = lower-left corner of item i, counted from 0. An item has to
    # end inside the larger rectangle, whose size is at most max_x by max_y, so its
    # corner is no further than max_x - width: this bound only restates that.
    pos_x = [ranged_int(m, f"pos_x_{i}", 0, max_x - widths[i]) for i in range(n)]
    pos_y = [ranged_int(m, f"pos_y_{i}", 0, max_y - heights[i]) for i in range(n)]
    # total_x, total_y = width and height of the larger rectangle
    total_x = ranged_int(m, "total_x", min_x, max_x)
    total_y = ranged_int(m, "total_y", min_y, max_y)

    # Every item lies within the larger rectangle: its right and top edges do not
    # pass the sides total_x and total_y.
    for i in range(n):
        post_before(m, None, pos_x[i], widths[i], total_x)
        post_before(m, None, pos_y[i], heights[i], total_y)

    # No two items overlap: for every pair, one lies completely to the left of, to the
    # right of, below or above the other. One selector per way of separating them,
    # and at least one selector must hold.
    for a in range(n):
        for b in range(a + 1, n):
            apart = m.bool_vector(f"apart_{a}_{b}", 4)
            m &= (apart[0] | apart[1] | apart[2] | apart[3])
            post_before(m, ~apart[0], pos_x[a], widths[a], pos_x[b])
            post_before(m, ~apart[1], pos_x[b], widths[b], pos_x[a])
            post_before(m, ~apart[2], pos_y[a], heights[a], pos_y[b])
            post_before(m, ~apart[3], pos_y[b], heights[b], pos_y[a])

    # Implied: the items fit in the larger rectangle, so its area is at least the
    # total area of the items. For a width w this bounds the height from below.
    items_area = sum(widths[i] * heights[i] for i in range(n))
    for w in range(min_x, max_x + 1):
        post(m, neg(at_least(total_x, w)), at_least(total_x, w + 1),
             at_least(total_y, -(-items_area // w)))

    # Symmetry breaking (does not change the declared outputs or the optimal area):
    # (a) Items of identical size can be swapped, so each group of identical items is
    # put in increasing order of corner, compared by pos_x first and pos_y second.
    # Two identical items never share a corner, so the order is strict. This only
    # chooses which of the interchangeable items carries which label.
    groups = {}
    for i in range(n):
        groups.setdefault((widths[i], heights[i]), []).append(i)
    for members in groups.values():
        for a, b in zip(members, members[1:]):
            left_of = m.bool(f"order_{a}_{b}")  # True: strictly smaller pos_x
            post_before(m, ~left_of, pos_x[a], 1, pos_x[b])
            post_before(m, left_of, pos_x[a], 0, pos_x[b])
            post_before(m, left_of, pos_y[a], 1, pos_y[b])
    # (b) A packing mirrored left-to-right (or top-to-bottom) inside the same larger
    # rectangle is another packing of the same area. For the largest item whose size
    # no other item has, its centre is required to lie in the left half (lower half),
    # which keeps one of each mirror pair. The item has no twin, so (a) cannot
    # relabel it, and the two rules can be applied together.
    unique = [i for i in range(n) if len(groups[(widths[i], heights[i])]) == 1]
    if unique:
        k = max(unique, key=lambda i: widths[i] * heights[i])
        for v in range(pos_x[k].lb, pos_x[k].ub + 1):  # 2 * pos_x + width <= total_x
            post(m, neg(at_least(pos_x[k], v)), at_least(total_x, 2 * v + widths[k]))
        for v in range(pos_y[k].lb, pos_y[k].ub + 1):  # 2 * pos_y + height <= total_y
            post(m, neg(at_least(pos_y[k], v)), at_least(total_y, 2 * v + heights[k]))

    # Minimise the area total_x * total_y. Write total_x = min_x + a and total_y =
    # min_y + b, where a counts the literals (total_x >= w) that hold for w > min_x
    # and b the literals (total_y >= h) that hold for h > min_y. Then
    # area = min_x * min_y + min_x * b + min_y * a + a * b, and the product a * b is
    # the number of pairs (w, h) with total_x >= w and total_y >= h. A soft clause
    # pays when its literal is false, so every unit pays through the negation of the
    # literal that says it is present; the constant min_x * min_y is left out.
    for w in range(min_x + 1, max_x + 1):
        m.obj[min_y] += ~(total_x >= w)
    for h in range(min_y + 1, max_y + 1):
        m.obj[min_x] += ~(total_y >= h)
    for w in range(min_x + 1, max_x + 1):
        for h in range(min_y + 1, max_y + 1):
            both = m.bool(f"both_{w}_{h}")  # forced true when both literals hold
            m &= (~(total_x >= w) | ~(total_y >= h) | both)
            m.obj[1] += ~both

    return m, {"pos_x": pos_x, "pos_y": pos_y, "total_x": total_x, "total_y": total_y}
