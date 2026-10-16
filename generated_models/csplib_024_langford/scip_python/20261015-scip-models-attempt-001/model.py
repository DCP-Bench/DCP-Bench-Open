# Langford's problem: arrange two copies of each number 1..k in a sequence of
# 2k positions so that the two copies of i are separated by exactly i numbers
# (they sit i+1 positions apart).
from pyscipopt import Model, quicksum


def build(instance):
    k = instance["k"]  # numbers 1..k, each used twice
    length = 2 * k  # the sequence has 2k positions, numbered from 0

    m = Model()
    # f[i, j] = 1 if the first copy of number i is at position j, so the second
    # copy is at position j + i + 1. The first copy of i has to fit in the sequence.
    f = {}
    for i in range(1, k + 1):
        for j in range(length - (i + 1)):
            f[i, j] = m.addVar(name=f"first_{i}_{j}", vtype="B")
        # each number has exactly one placement
        m.addCons(quicksum(f[i, j] for j in range(length - (i + 1))) == 1,
                  name=f"place_{i}")

    # the number that occupies position s: either its first copy starts at s,
    # or its second copy lands at s
    def covering(i, s):
        # placements of number i that cover position s
        terms = []
        if (i, s) in f:
            terms.append(f[i, s])
        if (i, s - i - 1) in f:
            terms.append(f[i, s - i - 1])
        return terms

    # every position holds exactly one number
    for s in range(length):
        m.addCons(quicksum(v for i in range(1, k + 1) for v in covering(i, s)) == 1,
                  name=f"position_{s}")

    # the output is the number at each position
    sol = [quicksum(i * v for i in range(1, k + 1) for v in covering(i, s))
           for s in range(length)]
    return m, {"sol": sol}
