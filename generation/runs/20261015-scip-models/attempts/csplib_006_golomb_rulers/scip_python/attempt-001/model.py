# Golomb ruler: place m marks 0 = a_1 < a_2 < ... < a_m on an integer line so that all pairwise differences are distinct, minimising the length a_m.
from pyscipopt import Model, quicksum


def build(instance):
    m_marks = instance["size"]
    m = Model()

    # upper bound on every mark: the optimal length is below m^2 for the sizes in this corpus,
    # and the bound only limits the search space (chosen by hand; not part of the instance data)
    ub = m_marks * m_marks
    length = m.addVar(name="length", vtype="I", lb=0, ub=ub)
    a = [m.addVar(name=f"mark_{i}", vtype="I", lb=0, ub=ub) for i in range(m_marks)]

    # the first mark is at position 0
    m.addCons(a[0] == 0)

    # the marks are strictly increasing
    for i in range(m_marks - 1):
        m.addCons(a[i + 1] - a[i] >= 1)

    # the gaps between consecutive marks are distinct differences, so the first i+1 marks
    # are at least 1 + 2 + ... + i apart; the last i marks lie at least that far from the end
    for i in range(m_marks):
        m.addCons(a[i] >= i * (i + 1) // 2)
        m.addCons(a[m_marks - 1 - i] + i * (i + 1) // 2 <= length)

    # reflection symmetry: the first gap is smaller than the last gap (they cannot be equal,
    # since equal gaps repeat a difference)
    if m_marks >= 3:
        m.addCons(a[1] - a[0] + 1 <= a[m_marks - 1] - a[m_marks - 2])

    # the difference of each pair of marks: a_j - a_i = delta[i, j], with one value chosen per pair
    # (one-hot binaries y[i, j, d] = 1 when the difference of marks i < j is d)
    pairs = [(i, j) for i in range(m_marks) for j in range(i + 1, m_marks)]
    y = {}
    for i, j in pairs:
        span = j - i
        # the span-many gaps between marks i and j are distinct positive integers
        lo = span * (span + 1) // 2
        hi = ub
        for d in range(lo, hi + 1):
            y[i, j, d] = m.addVar(name=f"y_{i}_{j}_{d}", vtype="B")
        m.addCons(quicksum(y[i, j, d] for d in range(lo, hi + 1)) == 1)
        m.addCons(a[j] - a[i] == quicksum(d * y[i, j, d] for d in range(lo, hi + 1)))

    # all differences are distinct: each difference value d is used by at most one pair of marks
    for d in range(1, ub + 1):
        users = [y[i, j, d] for (i, j) in pairs if (i, j, d) in y]
        if len(users) > 1:
            m.addCons(quicksum(users) <= 1)

    # counting cut: the pairs that use a difference of at most d are at most d in number,
    # because all differences are distinct positive integers
    for d in range(1, ub + 1):
        short = [y[i, j, e] for (i, j) in pairs for e in range(1, d + 1) if (i, j, e) in y]
        if len(short) > d:
            m.addCons(quicksum(short) <= d)

    # m(m-1)/2 distinct differences, all at most the length, so the length is at least that many
    m.addCons(length >= m_marks * (m_marks - 1) // 2)

    # the length of the ruler is the position of the last mark
    m.addCons(length == a[m_marks - 1])
    m.setObjective(length, "minimize")

    # the outputs give the mark positions and the ruler length
    return m, {"length": length, "marks": a}
