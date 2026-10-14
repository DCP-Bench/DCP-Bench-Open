from pycsp3 import *

# Pythagorean triplet: three natural numbers a < b < c with a^2 + b^2 = c^2 and
# a + b + c = 1000. The ordering a < b < c picks the one triplet, not its swapped copy.

a = Var(dom=range(1, 1000))
b = Var(dom=range(1, 1000))
c = Var(dom=range(1, 1000))

satisfy(
    # the three numbers are in increasing order
    a < b,
    b < c,

    # the three numbers form a right-angled triangle: a^2 + b^2 = c^2
    a * a + b * b == c * c,

    # the three numbers add up to 1000
    a + b + c == 1000,
)
