# Bank card PIN: four digits abcd with no two digits equal, where the two-digit number cd is three times the two-digit number ab, and the two-digit number da is two times the two-digit number bc.
from pycsp3 import *

# a, b, c, d are the four digits of the PIN
a = Var(dom=range(10))
b = Var(dom=range(10))
c = Var(dom=range(10))
d = Var(dom=range(10))

satisfy(
    # no two digits are the same
    AllDifferent(a, b, c, d),
    # the two-digit number cd is 3 times the two-digit number ab
    10 * c + d == 3 * (10 * a + b),
    # the two-digit number da is 2 times the two-digit number bc
    10 * d + a == 2 * (10 * b + c),
)
