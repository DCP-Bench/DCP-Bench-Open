# Problem: Split the sorted elements into K groups at value boundaries so that group sizes are as close as possible to round(N/K).
from pycsp3 import *

a = data.a
K = data.k
N = len(a)
# the groups are as close as possible to this size
target = round(N / K)
# a break point x is the 1-based index of the last element before the split, a split is only allowed between two different values
breaks_allowed = [p for p in range(1, N) if a[p - 1] != a[p]]
# x[i] is the 1-based index of the last element of group i (the groups are separated after x[i])
x = VarArray(size=K - 1, dom=breaks_allowed)
satisfy(
    # the break points are in increasing order and every group has at least one element
    Increasing(x, strict=True),
)
# sizes of the K groups, from the break points
sizes = [x[0]] + [x[i] - x[i - 1] for i in range(1, K - 1)] + [N - x[K - 2]]
# minimize the total deviation of the group sizes from the target size
minimize(Sum(abs(sizes[g] - target) for g in range(K)))
