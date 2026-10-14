# Golomb ruler: place `size` marks at integer positions 0 = a_1 < a_2 < ... < a_size so that all
# pairwise differences a_j - a_i are distinct, with the ruler (the last mark) as short as possible.
from exact import Exact


def build(instance):
    size = instance["size"]  # number of marks
    longest = size * size  # the reference lets every mark sit anywhere in 0..size*size

    solver = Exact()

    # marks[i] is the position of mark i
    marks = [f"marks_{i}" for i in range(size)]
    for name in marks:
        solver.addVariable(name, 0, longest)

    # the first mark is at 0
    solver.addConstraint([(1, marks[0])], True, 0, True, 0)

    # marks are strictly increasing
    for i in range(size - 1):
        solver.addConstraint([(1, marks[i + 1]), (-1, marks[i])], True, 1)

    # the length of the ruler is the position of the last mark
    solver.addVariable("length", 0, longest)
    solver.addConstraint([(1, "length"), (-1, marks[size - 1])], True, 0, True, 0)

    # all differences marks[j] - marks[i] (i < j) are different. Exact has no all-different
    # constraint, so each difference gets 0/1 indicators for its possible values, and each
    # value can be taken by at most one difference. The range of a difference is narrowed by
    # something the problem itself implies: the j - i gaps it spans are distinct positive
    # integers, so they add up to at least (j-i)(j-i+1)/2, and the gaps before mark i and after
    # mark j, being distinct too and fitting in the ruler, leave at most the rest.
    smallest_span = lambda gaps: gaps * (gaps + 1) // 2
    by_value = {}
    for i in range(size - 1):
        for j in range(i + 1, size):
            low = smallest_span(j - i)
            high = longest - smallest_span(i) - smallest_span(size - 1 - j)
            difference = f"difference_{i}_{j}"
            solver.addVariable(difference, low, high)
            solver.addConstraint([(1, marks[j]), (-1, marks[i]), (-1, difference)], True, 0, True, 0)
            indicators = []
            for v in range(low, high + 1):
                name = f"difference_{i}_{j}_is_{v}"
                solver.addVariable(name, 0, 1)
                indicators.append((v, name))
                by_value.setdefault(v, []).append(name)
            solver.addConstraint([(1, name) for _, name in indicators], True, 1, True, 1)
            solver.addConstraint(indicators + [(-1, difference)], True, 0, True, 0)
    for v, names in by_value.items():
        solver.addConstraint([(1, name) for name in names], False, 0, True, 1)

    # find the shortest ruler
    return solver, {"marks": marks, "length": "length"}, ("minimize", [(1, "length")])
