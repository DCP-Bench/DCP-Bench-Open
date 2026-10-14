# Problem: Find a number other than 48 such that adding 1 to it gives a square and adding 1 to its half also gives a square.
from pycsp3 import *

# peculiar + 1 is a square and peculiar / 2 + 1 is a square, peculiar is not 48
peculiar = Var(dom=range(1, 10001))
h = Var(dom=range(1, 5001))
a = Var(dom=range(1, 101))
b = Var(dom=range(1, 71))
satisfy(
    # the number is even, so that half of it is a whole number
    peculiar == 2 * h,
    # adding 1 to the number gives a square number
    a * a == peculiar + 1,
    # adding 1 to half of the number gives a square number
    b * b == h + 1,
    # another number, not 48
    peculiar != 48,
)
