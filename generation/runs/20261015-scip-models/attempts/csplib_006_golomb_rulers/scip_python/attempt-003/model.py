# Golomb ruler: place m marks on a line, 0 = a_0 < a_1 < ... < a_{m-1}, so that all
# pairwise differences are distinct; minimise the length a_{m-1}.
from pyscipopt import Model, quicksum


def tri(k):
    # k(k+1)/2: the least total length of k distinct positive gaps
    return k * (k + 1) // 2


def build(instance):
    m = instance["size"]
    # Upper bound on the length, from the mark count alone (m^2 is above the optimum
    # for every size in this problem). It only bounds the search space.
    UB = m * m

    model = Model("golomb_ruler")

    # Marks: the i-th mark (0-indexed) is at least the sum of the i smallest gaps and
    # at most the length minus the sum of the m-1-i gaps after it.
    marks = []
    for i in range(m):
        lo = tri(i)
        hi = UB - tri(m - 1 - i)
        marks.append(model.addVar(name=f"a_{i}", vtype="I", lb=lo, ub=hi))
    model.addCons(marks[0] == 0)

    # The marks are strictly increasing, so each gap is at least 1.
    for i in range(m - 1):
        model.addCons(marks[i + 1] - marks[i] >= 1)

    # Difference between mark j and mark i (i < j) is one value d in its own range.
    # One binary per (pair, value): diff[i,j,d] = 1 when a_j - a_i = d.
    diff = {}
    for i in range(m):
        for j in range(i + 1, m):
            k = j - i
            lo = tri(k)
            hi = UB - tri(i) - tri(m - 1 - j)
            for d in range(lo, hi + 1):
                diff[i, j, d] = model.addVar(name=f"d_{i}_{j}_{d}", vtype="B")
            # exactly one value for this pair
            model.addCons(
                quicksum(diff[i, j, d] for d in range(lo, hi + 1)) == 1,
                name=f"one_gap_{i}_{j}",
            )
            # the chosen value is the distance between the two marks
            model.addCons(
                marks[j] - marks[i] == quicksum(d * diff[i, j, d] for d in range(lo, hi + 1)),
                name=f"gap_{i}_{j}",
            )

    # All pairwise differences are distinct: each value is used by at most one pair.
    for d in range(1, UB + 1):
        users = [diff[key] for key in diff if key[2] == d]
        if len(users) > 1:
            model.addCons(quicksum(users) <= 1, name=f"distinct_{d}")

    # Counting cut: the pair differences are distinct positive integers, so at most t
    # pairs can have a difference of t or less.
    for t in range(1, UB + 1):
        small = [diff[key] for key in diff if key[2] <= t]
        if len(small) > t:
            model.addCons(quicksum(small) <= t, name=f"at_most_{t}_small_gaps")

    # Reflection symmetry: the ruler read backwards is also a ruler. Keep the orientation
    # whose first gap is not longer than its last gap.
    model.addCons(marks[1] - marks[0] <= marks[m - 1] - marks[m - 2])

    # The length is the position of the last mark.
    model.setObjective(marks[m - 1], "minimize")

    return model, {"length": marks[m - 1], "marks": marks}
