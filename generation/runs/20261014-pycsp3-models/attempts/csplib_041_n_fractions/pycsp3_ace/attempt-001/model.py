from pycsp3 import *

# find distinct non-zero digits A to I
a = Var(dom=range(1, 10))
b = Var(dom=range(1, 10))
c = Var(dom=range(1, 10))
d = Var(dom=range(1, 10))
e = Var(dom=range(1, 10))
f = Var(dom=range(1, 10))
g = Var(dom=range(1, 10))
h = Var(dom=range(1, 10))
i = Var(dom=range(1, 10))
# the digits are bound to the output names
A, B, C, D, E, F, G, H, I = a, b, c, d, e, f, g, h, i
# the two-digit numbers BC, EF and HI, with two different non-zero digits each
two_digit = [10 * d1 + d2 for d1 in range(1, 10) for d2 in range(1, 10) if d1 != d2]
bc = Var(dom=two_digit)
ef = Var(dom=two_digit)
hi = Var(dom=two_digit)
pairs = [(d1, d2, 10 * d1 + d2) for d1 in range(1, 10) for d2 in range(1, 10) if d1 != d2]
# products of the denominators, each as a binary product
ef_hi = Var(dom=range(100, 9900))
bc_hi = Var(dom=range(100, 9900))
bc_ef = Var(dom=range(100, 9900))
bc_ef_hi = Var(dom=range(1000, 1000000))
satisfy(
    # the nine digits are all different
    AllDifferent([a, b, c, d, e, f, g, h, i]),
    # BC is formed by the digits B and C
    Table(scope=[b, c, bc], supports=pairs),
    # EF is formed by the digits E and F
    Table(scope=[e, f, ef], supports=pairs),
    # HI is formed by the digits H and I
    Table(scope=[h, i, hi], supports=pairs),
    # each fraction is below 1, since the three fractions sum to 1 and are all positive
    a < bc,
    d < ef,
    g < hi,
    ef_hi == ef * hi,
    bc_hi == bc * hi,
    bc_ef == bc * ef,
    bc_ef_hi == bc * ef_hi,
    # A / BC + D / EF + G / HI = 1, multiplied out by BC * EF * HI to avoid fractions
    a * ef_hi + d * bc_hi + g * bc_ef == bc_ef_hi,
)
