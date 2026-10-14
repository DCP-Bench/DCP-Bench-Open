# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_size so that all
# pairwise differences a_j - a_i are distinct, with the ruler (the last mark) as short as possible.
from exact import Exact


def build(instance):
    size = instance["size"]  # number of marks
    longest = size * size  # the reference lets every mark sit anywhere in 0..size*size

    solver = Exact()

    # marks[i] is the position of mark i. Its range is narrowed by something the problem itself
    # implies: the gaps between consecutive marks are differences, hence distinct positive
    # integers, so the i gaps before mark i add up to at least 1 + 2 + ... + i, and the
    # size - 1 - i gaps after it add up to at least 1 + 2 + ... + (size - 1 - i), which must still
    # fit inside the largest allowed position.
    smallest_sum = lambda gaps: gaps * (gaps + 1) // 2
    low = [smallest_sum(i) for i in range(size)]
    high = [longest - smallest_sum(size - 1 - i) for i in range(size)]
    marks = [f"marks_{i}" for i in range(size)]
    for i in range(size):
        solver.addVariable(marks[i], low[i], high[i])

    # the first mark is at 0
    solver.addConstraint([(1, marks[0])], True, 0, True, 0)

    # marks are strictly increasing
    for i in range(size - 1):
        solver.addConstraint([(1, marks[i + 1]), (-1, marks[i])], True, 1)

    # the length of the ruler is the position of the last mark. All C(size, 2) differences are
    # distinct positive integers, so the largest of them, which is the length, is at least C(size, 2).
    pairs = size * (size - 1) // 2
    solver.addVariable("length", pairs, longest)
    solver.addConstraint([(1, "length"), (-1, marks[size - 1])], True, 0, True, 0)

    # More consequences of "all differences are distinct positive integers", which the solver
    # cannot see in the position indicators below:
    # - the span of marks i < j is made of j - i distinct gaps, so it is at least 1 + 2 + ... + (j - i);
    #   the rest of the ruler (i gaps before mark i, size - 1 - j gaps after mark j) is at least
    #   as long as the same sums for those gaps, so the span leaves at most length minus that;
    # - the differences between marks at most g places apart (size - 1 of them for distance 1,
    #   size - 2 for distance 2, ...) are distinct positive integers, so for each g their count
    #   c(g) gives a sum of at least 1 + 2 + ... + c(g). The sum of those differences is
    #   the sum over marks of marks[k] * (min(g, k) - min(g, size - 1 - k)).
    for i in range(size - 1):
        for j in range(i + 1, size):
            solver.addConstraint([(1, marks[j]), (-1, marks[i])], True, smallest_sum(j - i))
            if (i, j) != (0, size - 1):
                solver.addConstraint([(1, "length"), (-1, marks[j]), (1, marks[i])],
                                     True, smallest_sum(i) + smallest_sum(size - 1 - j))
    for g in range(1, size):
        count = sum(size - s for s in range(1, g + 1))
        weights = [(min(g, k) - min(g, size - 1 - k), marks[k]) for k in range(size)]
        solver.addConstraint([(w, name) for w, name in weights if w], True, smallest_sum(count))

    # Exact has no all-different constraint, so the distinct differences are stated on positions:
    # at_position[i][p] = 1 when mark i sits at position p, and has_mark[p] = 1 when some mark does.
    at_position = [{p: f"mark_{i}_at_{p}" for p in range(low[i], high[i] + 1)} for i in range(size)]
    has_mark = [f"has_mark_at_{p}" for p in range(longest + 1)]
    for p in range(longest + 1):
        solver.addVariable(has_mark[p], 0, 1)
    for i in range(size):
        for name in at_position[i].values():
            solver.addVariable(name, 0, 1)
        # each mark has exactly one position, and marks[i] is that position
        solver.addConstraint([(1, name) for name in at_position[i].values()], True, 1, True, 1)
        solver.addConstraint([(p, name) for p, name in at_position[i].items() if p] + [(-1, marks[i])],
                             True, 0, True, 0)
    for p in range(longest + 1):
        holders = [at_position[i][p] for i in range(size) if p in at_position[i]]
        # a position holds a mark exactly when one of the marks is placed there (and holds at most one)
        solver.addConstraint([(1, name) for name in holders] + [(-1, has_mark[p])], True, 0, True, 0)

    # all differences are distinct: for every distance d, at most one pair of marked positions
    # (p, p + d) exists. both[p][d] is forced to 1 when positions p and p + d both hold a mark.
    for d in range(1, longest + 1):
        pair_exists = []
        for p in range(longest - d + 1):
            name = f"marks_at_{p}_and_{p + d}"
            solver.addVariable(name, 0, 1)
            solver.addConstraint([(1, name), (-1, has_mark[p]), (-1, has_mark[p + d])], True, -1)
            pair_exists.append((1, name))
        solver.addConstraint(pair_exists, False, 0, True, 1)

    # find the shortest ruler
    return solver, {"marks": marks, "length": "length"}, ("minimize", [(1, "length")])
