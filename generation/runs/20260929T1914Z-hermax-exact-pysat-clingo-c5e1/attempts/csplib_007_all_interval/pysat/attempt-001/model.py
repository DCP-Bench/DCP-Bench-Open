# All-interval series: a permutation of the pitch classes 0..n-1 whose
# successive absolute differences are themselves all distinct.
from pysat.formula import IDPool
from pysat.integer import Integer, IntegerEngine


def build(instance):
    n = instance["n"]

    pool = IDPool()
    # x[i] = the i-th pitch class; diffs[i] = the interval between x[i] and x[i+1]
    x = [Integer(f"x_{i}", 0, n - 1, vpool=pool) for i in range(n)]
    diffs = [Integer(f"diff_{i}", 1, n - 1, vpool=pool) for i in range(n - 1)]
    engine = IntegerEngine(vars=x + diffs, vpool=pool)

    # the pitch classes are a permutation, and all intervals differ
    engine.add_alldifferent(x)
    engine.add_alldifferent(diffs)
    cnf = engine.clausify()

    # each interval is the absolute difference of its two pitch classes: for every
    # pair of neighbouring values a != b the interval is |a - b|
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    cnf.append([-x[i].equals(a), -x[i + 1].equals(b), diffs[i].equals(abs(a - b))])

    return cnf, {"x": x, "diffs": diffs}
