from pycsp3 import *

# four different numbers from 1 to 100 with a^2 + b^2 = c^2 + d^2
a = Var(dom=range(1, 101))
b = Var(dom=range(1, 101))
c = Var(dom=range(1, 101))
d = Var(dom=range(1, 101))

satisfy(
    # the four numbers are different from each other
    AllDifferent([a, b, c, d]),
    # the sum of the squares of the first two numbers equals the sum of the squares of the other two
    a * a + b * b == c * c + d * d,
)
