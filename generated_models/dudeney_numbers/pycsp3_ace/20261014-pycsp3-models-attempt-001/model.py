from pycsp3 import *

# Dudeney numbers: a perfect cube, larger than 1, with at most n digits,
# whose digit sum equals the cube root of the number.
n = data.n

# number is the Dudeney number, larger than 1
number = Var(dom=range(2, 10 ** n))

# root is the cube root of the number
root = Var(dom=range(2, 10 ** ((n + 2) // 3) + 1))

# digits[i] is the digit at position i (units first), so the number has at most n digits
digits = VarArray(size=n, dom=range(10))

satisfy(
    # the number is written with its digits
    number == Sum(digits[i] * 10 ** i for i in range(n)),
    # the number is a perfect cube of the root
    number == root * root * root,
    # the sum of the digits equals the cube root
    Sum(digits) == root,
)
