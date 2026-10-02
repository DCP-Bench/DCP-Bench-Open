# Vessel loading: place rectangular containers on a rectangular deck, in one
# layer, with sides parallel to the deck, without overlap, so that containers
# of classes that need a minimum separation are kept at least that far apart.
# Each container may be turned a quarter turn.
import functools
import operator

from hermax.model import Model


def post_before(m, gate, first, offset, second):
    """Post: if `gate` holds then first + offset <= second.

    Both variables count from 0. hermax integers use an order encoding, where
    the literal (x >= k) says "x is at least k". The relation is written on
    those literals (first >= k forces second >= k + offset), one short clause
    per value of `first`, instead of a pseudo-Boolean sum over the whole range.
    """
    for k in range(first.ub + 1):
        needed = k + offset  # the least value `second` must then have
        if needed <= 0:
            continue  # second >= 0 always holds
        clause = [~gate]
        if k > 0:
            clause.append(~(first >= k))  # only matters once first >= k
        if needed <= second.ub:
            clause.append(second >= needed)
        m &= functools.reduce(operator.or_, clause)


def post_equal_offset(m, gate, low, offset, high):
    """Post: if `gate` holds then high == low + offset."""
    post_before(m, gate, low, offset, high)
    post_before(m, gate, high, -offset, low)


def build(instance):
    deck_width = instance["deck_width"]
    deck_length = instance["deck_length"]
    n = instance["n_containers"]
    width = instance["width"]  # width of each container
    length = instance["length"]  # length of each container
    classes = instance["classes"]  # class of each container, numbered from 1
    separation = instance["separation"]  # minimum gap between two classes

    m = Model()
    # The sides of each container, counted from the bottom left corner of the
    # deck; the ranges are the deck's own extent.
    left = m.int_vector("left", n, 0, deck_width)
    right = m.int_vector("right", n, 0, deck_width)
    top = m.int_vector("top", n, 0, deck_length)
    bottom = m.int_vector("bottom", n, 0, deck_length)

    # Each container has its given width across and length along the deck, or
    # the other way round. turn[i][0] is "as given", turn[i][1] is "turned".
    for i in range(n):
        turn = m.bool_vector(f"turn_{i}", 2)
        m &= (turn[0] | turn[1])
        post_equal_offset(m, turn[0], left[i], width[i], right[i])
        post_equal_offset(m, turn[0], bottom[i], length[i], top[i])
        post_equal_offset(m, turn[1], left[i], length[i], right[i])
        post_equal_offset(m, turn[1], bottom[i], width[i], top[i])

    # No two containers overlap, and containers of classes with a separation are
    # at least that far apart: one lies at least `gap` to the left of, to the
    # right of, below or above the other. One selector per way of separating
    # them; at least one selector holds.
    for x in range(n):
        for y in range(x + 1, n):
            gap = separation[classes[x] - 1][classes[y] - 1]
            apart = m.bool_vector(f"apart_{x}_{y}", 4)
            m &= (apart[0] | apart[1] | apart[2] | apart[3])
            post_before(m, apart[0], right[x], gap, left[y])  # x left of y
            post_before(m, apart[1], right[y], gap, left[x])  # x right of y
            post_before(m, apart[2], top[x], gap, bottom[y])  # x under y
            post_before(m, apart[3], top[y], gap, bottom[x])  # x above y

    return m, {"left": left, "right": right, "top": top, "bottom": bottom}
