from pycsp3 import *

A = data.A
n = len(A)
# in_S[i] is 1 when element i is in the subset S, in_T[i] when it is in the subset T
in_S = VarArray(size=n, dom={0, 1})
in_T = VarArray(size=n, dom={0, 1})

satisfy(
    # the subsets S and T are disjoint
    [in_S[i] + in_T[i] <= 1 for i in range(n)],
    # S and T are non-empty
    Sum(in_S) >= 1,
    Sum(in_T) >= 1,
    # the sum of the elements in S equals the sum of the elements in T
    Sum(A[i] * in_S[i] for i in range(n)) == Sum(A[i] * in_T[i] for i in range(n)),
)
