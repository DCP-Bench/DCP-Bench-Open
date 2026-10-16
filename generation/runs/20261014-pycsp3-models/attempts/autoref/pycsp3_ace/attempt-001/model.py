from pycsp3 import *

# Autoreferential series S = (s0, ..., s(n+1)) of length n+2, given n and m.
n = data.n
m = data.m

# s[i] is the entry at position i of the series S. Every entry is at most n:
# the description does not state this bound, but the reference admits no larger
# entry (for n = 3, m = 0 it has only (2, 1, 2, 0, 0), not (4, 0, 0, 0, 0)).
s = VarArray(size=n + 2, dom=range(0, max(n, m) + 1))

satisfy(
    # the last entry of the series is m
    s[n + 1] == m,

    # there are s_i occurrences of i in S, for each i from 0 to n
    [Count(s, value=i) == s[i] for i in range(n + 1)],
)
