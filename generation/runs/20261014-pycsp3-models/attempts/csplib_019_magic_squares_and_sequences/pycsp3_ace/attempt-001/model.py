# Magic sequence: x[0..n-1] with values between 0 and n-1 such that the number i occurs exactly x[i] times in x.
from pycsp3 import *

n = data.n

# x[i] is the i-th term of the sequence
x = VarArray(size=n, dom=range(n))

satisfy(
    # the number i occurs exactly x[i] times in the sequence
    [Count(x, value=i) == x[i] for i in range(n)],
    # the counts add up to the length of the sequence
    Sum(x) == n,
)
