# Five brigands: whole numbers of doubloons for the five brigands that add up to 200, each at least one, and that still add up to 200 when Alfonso has twelve times as much, Benito three times, Carlos the same, Diego half and Esteban one-third.
from pycsp3 import *

# the variables are named in lower case; the output names are bound to them at the end
# a, b, c, d, e are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban
a = Var(dom=range(1, 201))
b = Var(dom=range(1, 201))
c = Var(dom=range(1, 201))
d = Var(dom=range(1, 201))
e = Var(dom=range(1, 201))

satisfy(
    # together they had exactly 200 doubloons
    a + b + c + d + e == 200,
    # with the changed amounts they still have altogether 200 doubloons, multiplied through by 6 to stay in whole numbers
    72 * a + 18 * b + 6 * c + 3 * d + 2 * e == 1200,
)

# output names, bound to the variables above
A = a
B = b
C = c
D = d
E = e
