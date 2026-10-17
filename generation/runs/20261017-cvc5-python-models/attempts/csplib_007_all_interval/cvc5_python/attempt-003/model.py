# All-interval series problem (CSPLib 007) in cvc5 (pythonic API).
# Find a permutation x of 0..n-1 such that the absolute differences between
# neighbouring entries, diffs, are a permutation of 1..n-1.
# n is read from the instance. Boolean one-hot encoding: no Distinct over integers.
import cvc5.pythonic as cz


def build(instance):
    n = instance["n"]
    m = n - 1  # number of intervals

    s = cz.SolverFor("QF_LIA")

    # pos[i][v] = 1 if pitch-class v is at position i of the series
    pos = [[cz.Bool(f"p_{i}_{v}") for v in range(n)] for i in range(n)]
    # itv[i][k] = 1 if the interval between positions i and i+1 is k (k = 1..n-1)
    itv = [[cz.Bool(f"t_{i}_{k}") for k in range(1, n)] for i in range(m)]

    def exactly_one(bs):
        return cz.Sum([cz.If(b, 1, 0) for b in bs]) == 1

    # the series is a permutation of 0..n-1: each position holds exactly one pitch-class
    for i in range(n):
        s.add(exactly_one(pos[i]))
    # ... and each pitch-class occurs exactly once
    for v in range(n):
        s.add(exactly_one([pos[i][v] for i in range(n)]))

    # the interval between neighbouring notes: each neighbour pair has exactly one interval value
    for i in range(m):
        s.add(exactly_one(itv[i]))
    # the intervals cover the full set 1..n-1: each interval value occurs exactly once
    for k in range(1, n):
        s.add(exactly_one([itv[i][k - 1] for i in range(m)]))

    # link the two: if neighbours at positions i, i+1 hold a and b, the interval is |a - b|
    for i in range(m):
        for a in range(n):
            for b in range(n):
                if a == b:
                    continue
                k = abs(a - b)
                s.add(cz.Implies(cz.And(pos[i][a], pos[i + 1][b]), itv[i][k - 1]))

    # the output x: the pitch-class at each position, as an integer
    x = [cz.Sum([cz.If(pos[i][v], v, 0) for v in range(n)]) for i in range(n)]
    # the output diffs: the interval at each neighbour pair, as an integer
    diffs = [cz.Sum([cz.If(itv[i][k - 1], k, 0) for k in range(1, n)]) for i in range(m)]

    return s, {"x": x, "diffs": diffs}
