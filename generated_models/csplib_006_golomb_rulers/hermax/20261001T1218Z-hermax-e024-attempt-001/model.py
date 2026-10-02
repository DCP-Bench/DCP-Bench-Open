# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... so
# that all differences between two marks are distinct, and make the ruler as
# short as possible (the position of the last mark is its length).
import functools
import operator

from hermax.model import Model


def build(instance):
    size = instance["size"]  # number of marks
    longest = size * size  # the largest position, as in the problem's own domain

    m = Model()
    # marks[i] = the position of the i-th mark
    marks = m.int_vector("marks", size, 0, longest)

    # the first mark is at 0
    m &= (marks[0] == 0)

    # the marks are in strictly increasing order: if mark i is at k or beyond,
    # mark i+1 is at k+1 or beyond (and mark i+1 is at 1 or beyond, whatever k)
    for i in range(size - 1):
        for k in range(longest + 1):
            clause = []
            if k > 0:
                clause.append(~(marks[i] >= k))
            if k + 1 <= longest:
                clause.append(marks[i + 1] >= k + 1)
            m &= functools.reduce(operator.or_, clause)

    # taken[p] = there is a mark at position p (true wherever a mark is placed)
    taken = m.bool_vector("taken", longest + 1)
    for i in range(size):
        for p in range(longest + 1):
            m &= (~(marks[i] == p) | taken[p])

    # All differences between two marks are different. For each difference d, at
    # most one pair of marked positions (p, p + d) may exist. pair[d][p] is
    # forced true when positions p and p + d are both marked.
    for d in range(1, longest + 1):
        if longest + 1 - d < 2:
            continue  # a single pair of positions cannot repeat the difference
        pair = m.bool_vector(f"pair_{d}", longest + 1 - d)
        for p in range(longest + 1 - d):
            m &= (~taken[p] | ~taken[p + d] | pair[p])
        m &= pair.at_most_one()

    # Minimise the length of the ruler, the position of the last mark: each
    # unit of position pays one, unit k being paid when marks[-1] >= k holds. A
    # soft clause pays when its literal is false, so it is the negation.
    last = marks[size - 1]
    for k in range(1, longest + 1):
        m.obj[1] += ~(last >= k)

    return m, {"marks": marks, "length": last}
