# Perfect square placement: pack squares of given integer sizes into a big
# square without overlap and without any spare room, with all sides parallel
# to the sides of the big square.
import functools
import operator

from hermax.model import Model


def post_before(m, gate, first, first_side, second):
    """Post: if `gate` holds then first + first_side <= second.

    Both variables count from 0. hermax integers use an order encoding, where
    the literal (x >= k) says "x is at least k"; the difference constraint is
    written out on those literals (first >= k forces second >= k + first_side)
    so that it costs one short clause per value of `first`, instead of a
    pseudo-Boolean sum over the whole coordinate range.
    """
    for k in range(first.ub + 1):
        clause = [~gate]
        if k > 0:
            clause.append(~(first >= k))  # only matters once first >= k
        if k + first_side <= second.ub:
            clause.append(second >= k + first_side)
        m &= functools.reduce(operator.or_, clause)


def build(instance):
    base = instance["base"]  # side length of the big square
    sides = instance["sides"]  # side length of each small square
    n = len(sides)

    m = Model()
    # Each square lies inside the big square, so its lower-left corner can be no
    # further than base - side from the origin; this bound is the in-bounds
    # constraint of the problem stated as a domain.
    # x_coords[i], y_coords[i] = the lower-left corner of square i (counted from 0)
    x_coords = [m.int(f"x_{i}", 0, base - sides[i]) for i in range(n)]
    y_coords = [m.int(f"y_{i}", 0, base - sides[i]) for i in range(n)]

    # No two squares overlap: for every pair, one lies completely to the left of,
    # to the right of, below or above the other. One selector per way of
    # separating them; at least one selector must hold.
    for a in range(n):
        for b in range(a + 1, n):
            apart = m.bool_vector(f"apart_{a}_{b}", 4)
            left, right, below, above = apart[0], apart[1], apart[2], apart[3]
            m &= (left | right | below | above)
            post_before(m, left, x_coords[a], sides[a], x_coords[b])
            post_before(m, right, x_coords[b], sides[b], x_coords[a])
            post_before(m, below, y_coords[a], sides[a], y_coords[b])
            post_before(m, above, y_coords[b], sides[b], y_coords[a])

    return m, {"x_coords": x_coords, "y_coords": y_coords}
