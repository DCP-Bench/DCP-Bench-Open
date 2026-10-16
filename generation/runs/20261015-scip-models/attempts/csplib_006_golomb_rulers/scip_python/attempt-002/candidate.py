# Golomb ruler: place m marks at integer positions 0 = a_1 < ... < a_m so that all
# pairwise differences are distinct, minimising the length a_m of the ruler.
from pyscipopt import Model, quicksum


def build(instance):
    m = instance["size"]
    # Upper bound on the ruler length. The optimal length is below m*m for every
    # mark count in the corpus (known optima: 10 marks -> 55, 14 marks -> 127).
    M = m * m
    # The m(m-1)/2 pairwise differences are distinct and at most the length, so the
    # length is at least m(m-1)/2 (a bound from the problem statement).
    L_min = m * (m - 1) // 2

    model = Model("golomb_ruler")

    # a[i] = position of mark i (marks numbered from 0 here)
    a = [model.addVar(name=f"mark_{i}", vtype="I", lb=i, ub=M - (m - 1 - i)) for i in range(m)]

    # the first mark is at 0 (the ruler starts there)
    model.addCons(a[0] == 0)

    # the length of the ruler must allow all distinct differences
    model.addCons(a[m - 1] >= L_min)

    # marks are in strictly increasing order along the ruler
    for i in range(m - 1):
        model.addCons(a[i + 1] - a[i] >= 1)

    # every pair of marks (i, j) has a difference d = a[j] - a[i] in j-i..M.
    # One-hot binaries z[p, v] select the value of the difference of pair p.
    pairs = [(i, j) for i in range(m) for j in range(i + 1, m)]
    z = {}
    for p, (i, j) in enumerate(pairs):
        for v in range(j - i, M + 1):
            z[p, v] = model.addVar(name=f"diff_{i}_{j}_is_{v}", vtype="B")
        # the difference of pair (i, j) takes exactly one value
        model.addCons(quicksum(z[p, v] for v in range(j - i, M + 1)) == 1)
        # the chosen value is the distance between the two marks
        model.addCons(quicksum(v * z[p, v] for v in range(j - i, M + 1)) == a[j] - a[i])

    # all differences are distinct: each distance is used by at most one pair
    for v in range(1, M + 1):
        users = [z[p, v] for p in range(len(pairs)) if (p, v) in z]
        model.addCons(quicksum(users) <= 1)

    # the length of the ruler is the position of the last mark
    length = a[m - 1]
    model.setObjective(length, "minimize")

    marks = [a[i] for i in range(m)]
    return model, {"length": length, "marks": marks}
