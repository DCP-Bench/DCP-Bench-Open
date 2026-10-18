# All-interval series problem (CSPLib 007) in cvc5 (pythonic API).
# Find a permutation x of 0..n-1 such that the absolute differences between
# neighbouring entries, diffs, are a permutation of 1..n-1.
# Pure Boolean clause encoding: pos[i][v] (value v sits at position i) and
# itv[i][k] (the interval between positions i and i+1 is k). The Int outputs
# are tied to these literals by equivalences, so the blocking clauses of the
# enumeration map onto Booleans.
import cvc5.pythonic as cz


def at_most_one(bs):
    return [cz.Or(cz.Not(a), cz.Not(b)) for j, a in enumerate(bs) for b in bs[j + 1:]]


def exactly_one(bs):
    return [cz.Or(bs)] + at_most_one(bs)


def build(instance):
    n = instance["n"]
    m = n - 1  # number of neighbouring pairs and of interval values

    s = cz.SolverFor("QF_LIA")

    # x: the series, declared shape [n]
    x = [cz.Int(f"x_{i}") for i in range(n)]
    # diffs: the intervals, declared shape [n-1]
    diffs = [cz.Int(f"d_{i}") for i in range(m)]

    # pos[i][v]: pitch-class v is at position i
    pos = [[cz.Bool(f"p_{i}_{v}") for v in range(n)] for i in range(n)]
    # itv[i][k-1]: the interval between neighbouring positions i and i+1 is k
    itv = [[cz.Bool(f"t_{i}_{k}") for k in range(1, n)] for i in range(m)]

    cons = []

    # Domains of the Int outputs: the series holds 0..n-1, the intervals 1..n-1.
    for i in range(n):
        cons.append(x[i] >= 0)
        cons.append(x[i] <= n - 1)
    for i in range(m):
        cons.append(diffs[i] >= 1)
        cons.append(diffs[i] <= n - 1)

    # Each position holds exactly one pitch-class, and each pitch-class occurs
    # exactly once in the series.
    for i in range(n):
        cons += exactly_one(pos[i])
    for v in range(n):
        cons += exactly_one([pos[i][v] for i in range(n)])

    # The series x is the permutation: x[i] has value v exactly when pos[i][v].
    for i in range(n):
        for v in range(n):
            cons.append(cz.Implies(pos[i][v], x[i] == v))
            cons.append(cz.Implies(x[i] == v, pos[i][v]))

    # Each neighbour pair has exactly one interval value, and that value is
    # the absolute difference |x[i+1] - x[i]|: diffs[i] has value k exactly when itv[i][k].
    for i in range(m):
        cons += exactly_one(itv[i])
        for k in range(1, n):
            cons.append(cz.Implies(itv[i][k - 1], diffs[i] == k))
            cons.append(cz.Implies(diffs[i] == k, itv[i][k - 1]))

    # The interval between neighbouring notes is |x[i+1] - x[i]|: if the two
    # neighbours are a and b, the interval between them is |a - b|.
    for i in range(m):
        for a in range(n):
            for b in range(n):
                if a != b:
                    cons.append(cz.Implies(cz.And(pos[i][a], pos[i + 1][b]), itv[i][abs(a - b) - 1]))

    # The same relation read the other way: a neighbour at a with interval k
    # forces the next neighbour to be a + k or a - k (when inside 0..n-1).
    for i in range(m):
        for k in range(1, n):
            for a in range(n):
                opts = []
                if a + k < n:
                    opts.append(pos[i + 1][a + k])
                if a - k >= 0:
                    opts.append(pos[i + 1][a - k])
                lhs = cz.And(itv[i][k - 1], pos[i][a])
                if not opts:
                    cons.append(cz.Not(lhs))
                elif len(opts) == 1:
                    cons.append(cz.Implies(lhs, opts[0]))
                else:
                    cons.append(cz.Implies(lhs, cz.Or(opts)))

    # The intervals cover the full set 1..n-1: each interval value occurs
    # exactly once among the neighbour pairs.
    for k in range(1, n):
        cons += exactly_one([itv[i][k - 1] for i in range(m)])

    s.add(*cons)
    return s, {"x": x, "diffs": diffs}
