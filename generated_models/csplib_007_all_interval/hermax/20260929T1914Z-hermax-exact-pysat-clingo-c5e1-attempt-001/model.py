# All-interval series: a permutation of the pitch classes 0..n-1 whose
# successive absolute differences are themselves all distinct.
from hermax.model import Model


def build(instance):
    n = instance["n"]

    m = Model()
    # x[i] = the i-th pitch class; a permutation of 0..n-1
    x = m.int_vector("x", n, 0, n - 1)
    m &= x.all_different()
    # diffs[i] = the interval between x[i] and x[i+1]; all intervals differ
    diffs = m.int_vector("diffs", n - 1, 1, n - 1)
    m &= diffs.all_different()

    # each interval is the absolute difference of its two pitch classes: for every
    # pair of neighbouring values a != b the interval is |a - b|
    for i in range(n - 1):
        for a in range(n):
            for b in range(n):
                if a != b:
                    m &= (~(x[i] == a) | ~(x[i + 1] == b) | (diffs[i] == abs(a - b)))

    return m, {"x": x, "diffs": diffs}
