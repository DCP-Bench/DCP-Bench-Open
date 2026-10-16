# Problem: Fill the Latin square so that each cage's target is met by its digits under an operation that is not given.
from pycsp3 import *

n = data.n
cages = data.problem
# x[r][c] is the digit in row r and column c, from 1 to n
x = VarArray(size=[n, n], dom=range(1, n + 1))
satisfy(
    # each row contains each digit once
    [AllDifferent(x[r]) for r in range(n)],
    # each column contains each digit once
    [AllDifferent(x[:, c]) for c in range(n)],
)
for target, cells in cages:
    values = [x[r - 1][c - 1] for r, c in cells]
    if len(values) == 1:
        # a cage of one cell holds its target
        satisfy(values[0] == target)
    elif len(values) == 2:
        a, b = values
        satisfy(
            # the cage of two cells has a target made by addition, subtraction, multiplication or division of its digits
            Or(a + b == target, a * b == target, a - b == target, b - a == target, a == b * target, b == a * target),
        )
    else:
        satisfy(
            # the cage of more cells has a target made by addition or multiplication of its digits
            Or(Sum(values) == target, Product(values) == target),
        )
