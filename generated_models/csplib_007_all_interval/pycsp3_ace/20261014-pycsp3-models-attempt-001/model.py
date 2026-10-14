from pycsp3 import *

n = data.n
# the pitch-classes in the series, each from 0 to n-1
x = VarArray(size=n, dom=range(n))
# the intervals between neighbouring pitch-classes, each from 1 to n-1
diffs = VarArray(size=n - 1, dom=range(1, n))

satisfy(
    # each pitch-class occurs exactly once
    AllDifferent(x),
    # the intervals between neighbouring notes are all different
    AllDifferent(diffs),
    # each interval is the distance between two neighbouring pitch-classes
    [diffs[i] == abs(x[i + 1] - x[i]) for i in range(n - 1)],
)
