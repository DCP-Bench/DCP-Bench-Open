# Golomb ruler (csplib_006): a set of m integers 0 = a_1 < a_2 < ... < a_m such that
# all m(m-1)/2 pairwise differences are distinct. Minimise the length a_m.
# Outputs: length (int) and marks (the m mark positions).

import cvc5.pythonic as cz


def build(instance):
    m = instance["size"]

    # Mark positions, one integer per mark.
    marks = [cz.Int(f"mark_{i}") for i in range(m)]

    constraints = []

    # The marks are a set of integers 0 = a_1 < a_2 < ... < a_m.
    constraints.append(marks[0] == 0)
    for i in range(m - 1):
        constraints.append(marks[i] < marks[i + 1])

    # All m(m-1)/2 differences a_j - a_i, 1 <= i < j <= m, are distinct.
    diffs = [marks[j] - marks[i] for i in range(m) for j in range(i + 1, m)]
    if len(diffs) >= 2:
        constraints.append(cz.Distinct(diffs))

    # The ruler length is the position of the last mark; it is minimised.
    length = marks[m - 1]

    return constraints, {"length": length, "marks": marks}, ("minimize", length)
