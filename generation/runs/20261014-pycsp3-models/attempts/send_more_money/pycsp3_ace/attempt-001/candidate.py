from pycsp3 import *

# each letter stands for a different digit
s = Var(dom=range(10))
e = Var(dom=range(10))
n = Var(dom=range(10))
d = Var(dom=range(10))
m = Var(dom=range(10))
o = Var(dom=range(10))
r = Var(dom=range(10))
y = Var(dom=range(10))

satisfy(
    # each letter is assigned a different digit
    AllDifferent([s, e, n, d, m, o, r, y]),
    # the first letter of each word cannot be zero
    s != 0,
    m != 0,
    # SEND + MORE = MONEY, column by column in the sum
    1000 * s + 100 * e + 10 * n + d + 1000 * m + 100 * o + 10 * r + e
    == 10000 * m + 1000 * o + 100 * n + 10 * e + y,
)
