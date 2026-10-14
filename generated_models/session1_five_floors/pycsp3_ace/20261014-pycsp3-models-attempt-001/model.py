from pycsp3 import *

# five people live on the floors 1 to 5 of an apartment house, one person per floor
b = Var(dom=range(1, 6))
c = Var(dom=range(1, 6))
f = Var(dom=range(1, 6))
m = Var(dom=range(1, 6))
s = Var(dom=range(1, 6))
# the output names are bound to the floor variables
B, C, F, M, S = b, c, f, m, s
satisfy(
    # they all live on different floors
    AllDifferent([b, c, f, m, s]),
    # Baker does not live on the fifth floor
    b != 5,
    # Cooper does not live on the first floor
    c != 1,
    # Fletcher does not live on either the fifth or the first floor
    f != 5,
    f != 1,
    # Miller lives on a higher floor than Cooper
    m > c,
    # Smith does not live on a floor adjacent to Fletcher's
    abs(s - f) != 1,
    # Fletcher does not live on a floor adjacent to Cooper's
    abs(f - c) != 1,
)
