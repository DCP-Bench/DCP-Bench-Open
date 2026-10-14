from pycsp3 import *

# Hanging weights puzzle: weights A to M hang from a system of bars, each weight is an integer from 1 to 13,
# and the diagram balances.
# Distances are read in units of three characters of the diagram, the spacing of the bar's holes.
# The pivot of the bar under the top bar is read at column 34; the vertical line at column 33 lands
# between the holes at 31 and 34, and only the reading at 34 has a solution with values 1 to 13.

a = Var(dom=range(1, 14))
b = Var(dom=range(1, 14))
c = Var(dom=range(1, 14))
d = Var(dom=range(1, 14))
e = Var(dom=range(1, 14))
f = Var(dom=range(1, 14))
g = Var(dom=range(1, 14))
h = Var(dom=range(1, 14))
i = Var(dom=range(1, 14))
j = Var(dom=range(1, 14))
k = Var(dom=range(1, 14))
l = Var(dom=range(1, 14))
m = Var(dom=range(1, 14))

satisfy(
    # the bar on the bottom right must have 5*C=D
    # the weights on either side of a given pivot point must be equal, when weighted by the distance from the pivot
    5 * c == d,
)

satisfy(
    # the one above it must have 3*G=2*(C+D)
    # a bar hanging beneath another contributes its total weight as though it were a single weight
    3 * g == 2 * (c + d),
)

satisfy(
    # the bar with A on its left end and B on its right must balance: 4*A=B
    # the weights on either side of a given pivot point must be equal, when weighted by the distance from the pivot
    4 * a == b,
)

satisfy(
    # the bar with E and F must balance: 3*E=2*F
    # the weights on either side of a given pivot point must be equal, when weighted by the distance from the pivot
    3 * e == 2 * f,
)

satisfy(
    # the bar with H and I, carrying the bar E-F, must balance: 3*H=3*I+2*(E+F)
    # a bar hanging beneath another contributes its total weight as though it were a single weight
    3 * h == 3 * i + 2 * (e + f),
)

satisfy(
    # the bar with L and M, carrying the bar H-I, must balance
    # a bar hanging beneath another contributes its total weight as though it were a single weight
    h + i + e + f == l + 4 * m,
)

satisfy(
    # the bar hanging from the right end of the top bar, carrying J, K, the bar A-B and the bar G-C-D, must balance
    # a bar hanging beneath another contributes its total weight as though it were a single weight
    3 * (a + b) + 2 * j == k + 2 * (g + c + d),
)

satisfy(
    # the top bar must balance: the bar L-M (with H-I and E-F) on one side, the bar on the right on the other
    # a bar hanging beneath another contributes its total weight as though it were a single weight
    4 * (l + m + h + i + e + f) == 3 * (j + k + a + b + g + c + d),
)

# print the weights (a, b, c, d, e, f, g, h, i, j, k, l, m) that satisfy the conditions above
